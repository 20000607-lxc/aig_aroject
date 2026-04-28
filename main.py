import os
from dotenv import load_dotenv
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import (
    BooleanType, FloatType, LongType,
    StringType, StructField, StructType,
)
from rag_utils import clean_text, chunk_text, build_tfidf, retrieve_top_k, SOURCE_TEXT_PATH
from groud_truth_config import RETRIEVAL_QUERIES, OBSERVATIONS_CONFIG

load_dotenv()

# 1. SparkSession
spark = SparkSession.builder \
    .appName("AIG_RAG_2019") \
    .master("local[*]") \
    .config("spark.driver.memory", "4g") \
    .config("spark.executor.memory", "2g") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
print("Spark version:", spark.version)


# 2. Load & chunk source text → Spark DataFrame
print("\n 1 Loading and chunking source text...")
with open(SOURCE_TEXT_PATH, "r", encoding="utf-8") as f:
    raw = f.read()
text = clean_text(raw)
chunks = chunk_text(text, year=2019, chunk_size=2000, overlap=400)
print(f"      {len(chunks)} chunks created")

chunks_schema = StructType([
    StructField("chunk_id",   StringType()),
    StructField("chunk_text", StringType()),
    StructField("start_char", LongType()),
    StructField("end_char",   LongType()),
])
chunks_df = spark.createDataFrame(chunks, schema=chunks_schema)


# 3. Fit TF-IDF on driver; broadcast to all workers
print("\n 2 Building TF-IDF index and broadcasting...")
vectorizer, tfidf_matrix = build_tfidf(chunks)
bc_vectorizer  = spark.sparkContext.broadcast(vectorizer)
bc_tfidf_mat   = spark.sparkContext.broadcast(tfidf_matrix)
print(f"      TF-IDF matrix shape: {tfidf_matrix.shape}")


# 4. Retrieve top-5 chunks per query (4 query in total)
print("\n 3 Retrieving top-k chunks per query...")
retrieved_rows = []
for query_key, query_text in RETRIEVAL_QUERIES.items():
    top_chunks = retrieve_top_k(chunks, vectorizer, tfidf_matrix, query_text, k=5)
    for rank, c in enumerate(top_chunks, 1):
        retrieved_rows.append((
            query_key,
            c["chunk_id"],
            c["chunk_text"],
            float(c["score"]),
            rank,
        ))

retrieved_schema = StructType([
    StructField("query_key",  StringType()),
    StructField("chunk_id",   StringType()),
    StructField("chunk_text", StringType()),
    StructField("score",      FloatType()),
    StructField("rank",       LongType()),
])
retrieved_df = spark.createDataFrame(retrieved_rows, schema=retrieved_schema)
print(f"      {retrieved_df.count()} (query, chunk) rows in retrieved_df")


# 5. Build observations DataFrame; join retrieved chunks
print("\n 4 Building observations DataFrame and joining chunks...")
obs_rows = [
    (
        o["obs_id"],
        o["variable"],
        o["var_type"],
        o["query_key"],
        str(o.get("source_page") or ""),
        o["description"],
        o["extraction_hint"],
    )
    for o in OBSERVATIONS_CONFIG
]
obs_schema = StructType([
    StructField("obs_id",          StringType()),
    StructField("variable",        StringType()),
    StructField("var_type",        StringType()),
    StructField("query_key",       StringType()),
    StructField("source_page",     StringType()),
    StructField("description",     StringType()),
    StructField("extraction_hint", StringType()),
])
obs_df = spark.createDataFrame(obs_rows, schema=obs_schema)

# Join observation and retrieved chunks for that query 
obs_with_chunks = obs_df.join(
    retrieved_df.select("query_key", "chunk_id", "chunk_text", "score"),
    on="query_key",
    how="left",
)
obs_grouped = obs_with_chunks.groupBy(
    "obs_id", "variable", "var_type", "query_key",
    "source_page", "description", "extraction_hint",
).agg(
    F.collect_list(F.struct("chunk_id", "chunk_text", "score")).alias("retrieved_chunks")
)
print(f"      {obs_grouped.count()} observation rows with retrieved chunks")


# 6. LLM extraction via mapInPandas (parallel across Spark partitions)
print("\n 5 Running LLM extraction (mapInPandas)...")

extract_out_schema = StructType([
    StructField("obs_id",          StringType()),
    StructField("extracted_value", StringType()),
    StructField("confidence",      StringType()),
    StructField("source_text",     StringType()),
    StructField("reasoning",       StringType()),
])


def extract_partition(pdf_iter):
    import os, time
    import anthropic
    import pandas as pd
    from dotenv import load_dotenv
    from llm_utils import build_prompt, parse_response

    load_dotenv()
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    for pdf in pdf_iter:
        results = []
        for _, row in pdf.iterrows():
            obs = {
                "obs_id":          row["obs_id"],
                "variable":        row["variable"],
                "var_type":        row["var_type"],
                "description":     row["description"],
                "extraction_hint": row["extraction_hint"],
            }
            raw_chunks = row["retrieved_chunks"] if row["retrieved_chunks"] is not None else []
            chunk_list = [
                {
                    "chunk_id":   c["chunk_id"],
                    "chunk_text": c["chunk_text"],
                    "score":      c["score"],
                }
                for c in raw_chunks
            ]

            prompt = build_prompt(obs, chunk_list)
            record = {
                "obs_id":          row["obs_id"],
                "extracted_value": "API_ERROR",
                "confidence":      "low",
                "source_text":     "",
                "reasoning":       "",
            }

            for attempt in range(3):
                try:
                    resp = client.messages.create(
                        model="claude-sonnet-4-6", # "claude-haiku-4-5-20251001",
                        max_tokens=512,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    parsed = parse_response(resp.content[0].text, row["var_type"])
                    ev = parsed.get("extracted_value")
                    record.update({
                        "extracted_value": str(ev) if ev is not None else "NOT_FOUND",
                        "confidence":      str(parsed.get("confidence", "low")),
                        "source_text":     str(parsed.get("source_text", "")),
                        "reasoning":       str(parsed.get("reasoning", "")),
                    })
                    break
                except Exception as exc:
                    if attempt < 2:
                        time.sleep(2 ** attempt)
                    else:
                        record["reasoning"] = str(exc)

            results.append(record)

        yield pd.DataFrame(results)

extraction_df = obs_grouped.mapInPandas(extract_partition, schema=extract_out_schema)
extraction_df = extraction_df.cache()
extraction_df.count()  # execution
print("      Extraction complete")
extraction_df.select("obs_id", "extracted_value", "confidence").orderBy("obs_id").show(15)


# 7. evaluate
print("\n 6 Evaluating against ground truth...")
gt_df = spark.read.csv("data/ground_truth2019.csv", header=True) # Columns: Variable, Observation_ID, Ground_Truth_Value, Unit_or_Type

results_df = extraction_df.join(
    gt_df.withColumnRenamed("Observation_ID", "obs_id"),
    on="obs_id",
    how="left",
)

@F.udf(BooleanType())
def is_correct_udf(extracted, gt_value, unit_or_type):
    from evaluate import compare_numeric, compare_categorical
    if unit_or_type == "Millions_USD":
        result = compare_numeric(extracted, gt_value)
    else:
        result = compare_categorical(extracted, gt_value)
    return result["is_correct"]


results_df = results_df.withColumn(
    "is_correct",
    is_correct_udf(F.col("extracted_value"), F.col("Ground_Truth_Value"), F.col("Unit_or_Type")),
)

# Page-hit evaluation: check if any retrieved chunk contains the expected source page
@F.udf(BooleanType())
def page_hit_udf(source_page, retrieved_chunks):
    from evaluate import check_page_hit
    if not source_page:
        return None
    chunks = [{"chunk_text": c["chunk_text"]} for c in (retrieved_chunks or [])]
    return check_page_hit(chunks, int(source_page))

page_ref = obs_grouped.select("obs_id", "source_page", "retrieved_chunks")
results_df = results_df \
    .join(page_ref, on="obs_id", how="left") \
    .withColumn("page_hit", page_hit_udf(F.col("source_page"), F.col("retrieved_chunks"))) \
    .cache()


# 8. Compute & report metrics
from evaluate import compute_metrics

results_pd = results_df.drop("retrieved_chunks").toPandas()
m = compute_metrics(results_pd)

def _table(headers, rows):
    widths = [len(h) for h in headers]
    for row in rows:
        for i, v in enumerate(row):
            widths[i] = max(widths[i], len(str(v)))
    sep = "+-" + "-+-".join("-" * w for w in widths) + "-+"
    fmt = "| " + " | ".join(f"{{:<{w}}}" for w in widths) + " |"
    lines = [sep, fmt.format(*headers), sep]
    for row in rows:
        lines.append(fmt.format(*[str(v) for v in row]))
    lines.append(sep)
    return "\n".join(lines)

out = []
out.append(f"Overall Accuracy : {m['overall_accuracy']:.1%}  ({m['correct']}/{m['total']})")
if m["page_hit_rate"] is not None:
    out.append(f"Page Hit Rate    : {m['page_hit_rate']:.1%}  ({m['page_hit_cnt']}/{m['page_hit_total']})")

out.append("")
out.append("--- Numeric Variables (Millions USD) ---")
out.append(f"Accuracy : {m['numeric_accuracy']:.1%}")
out.append(f"MAE      : {m['numeric_mae_millions_usd']:,.2f} M USD" if m["numeric_mae_millions_usd"] is not None else "MAE      : N/A")

out.append("")
out.append("--- Categorical Variables ---")
out.append(f"Accuracy  : {m['categorical_accuracy']:.1%}")
out.append(f"Precision : {m['categorical_precision']:.4f}")
out.append(f"Recall    : {m['categorical_recall']:.4f}")
out.append(f"F1        : {m['categorical_f1']:.4f}")

out.append("")
out.append("--- Per-Variable Summary ---")
per_var = (results_pd.groupby("Variable")
           .agg(accuracy=("is_correct", "mean"),
                correct=("is_correct", "sum"),
                n=("is_correct", "count"))
           .reset_index()
           .sort_values("Variable"))
out.append(_table(
    ["Variable", "Accuracy", "Correct", "N"],
    [(r["Variable"], f"{r['accuracy']:.1%}", int(r["correct"]), int(r["n"]))
     for _, r in per_var.iterrows()],
))

out.append("")
out.append("--- Detailed Results ---")
detail_rows = []
for _, r in results_pd.sort_values("obs_id").iterrows():
    ph = r["page_hit"]
    ph_str = "N/A" if ph is None or str(ph) == "nan" else str(bool(ph))
    detail_rows.append((
        r["obs_id"], r["Variable"], r["Ground_Truth_Value"],
        r["extracted_value"], r["confidence"], str(r["is_correct"]), ph_str,
    ))
out.append(_table(
    ["obs_id", "Variable", "Ground_Truth", "Extracted", "Conf", "Correct", "PageHit"],
    detail_rows,
))
out.append("=" * 56)

report = "\n".join(out)
print(report)

# 9. Save results
os.makedirs("results", exist_ok=True)
with open("results/result.txt", "w", encoding="utf-8") as f:
    f.write(report + "\n")
print("\nReport saved to results/result.txt")

results_df.drop("retrieved_chunks").write.mode("overwrite").option("header", "true") \
    .csv("results/pyspark_extraction_results")
print("CSV    saved to results/pyspark_extraction_results/")

spark.stop()
