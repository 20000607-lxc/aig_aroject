# AIG 2019 10-K RAG Extraction
A RAG pipeline that extracts financial data from AIG's 2019 Form 10-K using TF-IDF, a Claude LLM, and PySpark for distributed execution.

## Data 

Source: https://huggingface.co/datasets/eloukas/edgar-corpus

We first extract AIG's 2019 Form 10-K from the dataset, and save it in `data/aig_source_text2019.txt`. 

## Pipeline

1. **Chunk** — splits the source text (`data/aig_source_text2019.txt`) into overlapping 2000-character chunks
2. **Retrieve** — builds a TF-IDF index and fetches the top-5 most relevant chunks per query
3. **Extract** — sends retrieved chunks to Claude LLM to extract values
4. **Evaluate** — compares extracted values against `data/ground_truth2019.csv` 

15 observations are extracted across three variable types:

| Variable | Type | Description |
|---|---|---|
| `Premiums_and_Deposits` | numeric (millions USD) | Life Insurance & Institutional Markets premiums/deposits for 2017–2019 |
| `Reserves_by_Charge` | numeric (millions USD) | Group Retirement annuity reserves by surrender-charge tier |
| `Business_Sub_Segment` | categorical | Operating segment names under Life and Retirement |


## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```
ANTHROPIC_API_KEY=your_key_here
```

## Run

```bash
python main.py
```

Results saved to `results/pyspark_extraction_results/`.

## Selected Results

The full results is saved to `results/result.txt`. 

**Overall accuracy: 15 / 15 = 100%**

### Premiums and Deposits (millions USD)

| ID | Description | Ground Truth | Extracted | Correct |
|---|---|---|---|---|
| Obs_01 | Life Insurance 2019 | 4,086 | 4,086 | True |
| Obs_02 | Life Insurance 2018 | 3,914 | 3,914 | True |
| Obs_03 | Life Insurance 2017 | 3,755 | 3,755 | True |
| Obs_04 | Institutional Markets 2019 | 2,758 | 2,758 | True |
| Obs_05 | Institutional Markets 2018 | 3,032 | 3,032 | True |

### Reserves by Surrender Charge — Group Retirement at Dec 31, 2019 (millions USD)

| ID | Category | Ground Truth | Extracted | Correct |
|---|---|---|---|---|
| Obs_06 | No surrender charge | 71,912 | 71,912 | True |
| Obs_07 | Greater than 0%–2% | 1,140 | 1,140 | True |
| Obs_08 | Greater than 2%–4% | 1,115 | 1,115 | True |
| Obs_09 | Greater than 4% | 6,038 | 6,038 | True |
| Obs_10 | Total reserves | 80,376 | 80,376 | True |

### Business Sub-Segments (categorical)

| ID | Description | Ground Truth | Extracted | Correct |
|---|---|---|---|---|
| Obs_11 | Group retirement segment | Group Retirement | Group Retirement | True |
| Obs_12 | Life insurance segment | Life Insurance | Life Insurance | True |
| Obs_13 | Institutional markets segment | Institutional Markets | Institutional Markets | True |
| Obs_14 | Domestic life sub-segment | Domestic Life | domestic life | True |
| Obs_15 | International life sub-segment | International Life | International Life | True |
