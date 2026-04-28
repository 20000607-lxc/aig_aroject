import re

# Chunk retrieval page evaluation 
def check_page_hit(chunks, page):
    """
    Return True if any chunk contains the expected page marker.
    """
    if page is None:
        return None
    pattern = re.compile(
        rf'\b{page}\s+AIG\b|\bForm 10-K\s+{page}\b',
        re.IGNORECASE,
    )
    return any(pattern.search(c['chunk_text']) for c in chunks)


def compare_numeric(extracted, gt_value, tol_pct=0.01):
    if extracted is None or str(extracted) in ('NOT_FOUND', 'PARSE_ERROR', 'API_ERROR'):
        return {'is_correct': False, 'abs_error': None, 'rel_error_pct': None}
    try:
        ext, gt  = float(extracted), float(gt_value)
        abs_err  = abs(ext - gt)
        rel_err  = (abs_err / abs(gt) * 100) if gt != 0 else None
        correct  = rel_err is not None and rel_err <= tol_pct * 100
        return {
            'is_correct':    correct,
            'abs_error':     round(abs_err, 2),
            'rel_error_pct': round(rel_err, 4) if rel_err is not None else None,
        }
    except (ValueError, TypeError):
        return {'is_correct': False, 'abs_error': None, 'rel_error_pct': None}


def compare_categorical(extracted, gt_value):
    if extracted is None or str(extracted) in ('NOT_FOUND', 'PARSE_ERROR', 'API_ERROR'):
        return {'is_correct': False, 'abs_error': None, 'rel_error_pct': None}
    match = str(extracted).strip().lower() == str(gt_value).strip().lower()
    return {'is_correct': match, 'abs_error': None, 'rel_error_pct': None}


def compute_metrics(df):
    """
    Compute all evaluation metrics from a collected pandas DataFrame.

    Expected columns: obs_id, extracted_value, Ground_Truth_Value, Unit_or_Type,
                      Variable, is_correct, page_hit, source_page
    """
    df = df.copy()
    df["is_correct"] = df["is_correct"].fillna(False).astype(bool)

    total   = len(df)
    correct = int(df["is_correct"].sum())
    overall_accuracy = correct / total if total > 0 else 0.0

    # Numeric: MAE (mean absolute error across parseable extractions)
    numeric  = df[df["Unit_or_Type"] == "Millions_USD"]
    mae_vals = []
    for _, row in numeric.iterrows():
        r = compare_numeric(row["extracted_value"], row["Ground_Truth_Value"])
        if r["abs_error"] is not None:
            mae_vals.append(r["abs_error"])
    mae = round(sum(mae_vals) / len(mae_vals), 2) if mae_vals else None

    # Categorical: Precision / Recall / F1
    # TP: extracted something AND correct
    # FP: extracted something (non-error) AND wrong  → also counted as FN (missed right answer)
    # FN: extracted nothing (NOT_FOUND / error)      → missed right answer
    categorical = df[df["Unit_or_Type"] != "Millions_USD"]
    _errors = {"NOT_FOUND", "PARSE_ERROR", "API_ERROR", ""}
    tp = fp = fn = 0
    for _, row in categorical.iterrows():
        ext = str(row["extracted_value"]) if row["extracted_value"] is not None else ""
        not_extracted = ext in _errors
        if row["is_correct"]:
            tp += 1
        elif not not_extracted:   # extracted something wrong
            fp += 1
            fn += 1
        else:                     # nothing extracted
            fn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1        = (2 * precision * recall / (precision + recall)
                 if (precision + recall) > 0 else 0.0)

    # Page hit rate (only obs that have a known source page)
    with_page = df[df["source_page"].notna() & (df["source_page"].astype(str) != "")]
    ph_total  = len(with_page)
    ph_cnt    = int(with_page["page_hit"].fillna(False).astype(bool).sum()) if ph_total > 0 else 0
    ph_rate   = ph_cnt / ph_total if ph_total > 0 else None

    return {
        "overall_accuracy":         overall_accuracy,
        "total":                    total,
        "correct":                  correct,
        "numeric_accuracy":         numeric["is_correct"].mean() if len(numeric) > 0 else None,
        "numeric_mae_millions_usd": mae,
        "categorical_accuracy":     categorical["is_correct"].mean() if len(categorical) > 0 else None,
        "categorical_precision":    round(precision, 4),
        "categorical_recall":       round(recall, 4),
        "categorical_f1":           round(f1, 4),
        "page_hit_rate":            round(ph_rate, 4) if ph_rate is not None else None,
        "page_hit_cnt":             ph_cnt,
        "page_hit_total":           ph_total,
    }
