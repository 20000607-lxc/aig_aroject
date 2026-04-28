import re
import json

FILING_YEAR = 2019

def _format_excerpts(chunks):
    parts = []
    for i, c in enumerate(chunks, 1):
        score = c.get('score', 0)
        parts.append(
            f'[Excerpt {i} | chunk_id={c["chunk_id"]} | score={score:.4f}]\n'
            f'{c["chunk_text"]}'
        )
    return '\n\n---\n\n'.join(parts)

def build_prompt(obs, chunks):
    excerpts    = _format_excerpts(chunks)
    obs_id      = obs['obs_id']
    variable    = obs['variable']
    description = obs['description']
    hint        = obs['extraction_hint']

    if obs['var_type'] == 'numeric':
        return f"""You are a financial data extraction specialist.
The excerpts are from AIG's {FILING_YEAR} Form 10-K.

OBSERVATION ID: {obs_id}
VARIABLE: {variable}
DESCRIPTION: {description}
EXTRACTION HINT: {hint}

EXCERPTS:
---
{excerpts}
---

INSTRUCTIONS:
1. {hint}
2. Report as a plain integer in MILLIONS USD — no commas, no $ signs.
3. For losses use a negative sign (NOT parentheses).
4. If the value cannot be found, respond with "NOT_FOUND".

Respond with ONLY this JSON (no other text):
{{"extracted_value": "<integer or NOT_FOUND>", "confidence": "<high|medium|low>", "source_text": "<exact row or phrase>", "reasoning": "<brief>"}}"""
    else:
        return f"""You are a financial document extraction specialist.
The excerpts are from AIG's {FILING_YEAR} Form 10-K.

OBSERVATION ID: {obs_id}
VARIABLE: {variable}
DESCRIPTION: {description}
EXTRACTION HINT: {hint}

EXCERPTS:
---
{excerpts}
---

{hint}
Report only the exact English name. If not found, respond with "NOT_FOUND".

Respond with ONLY this JSON (no other text):
{{"extracted_value": "<name or NOT_FOUND>", "confidence": "<high|medium|low>", "source_text": "<exact phrase>", "reasoning": "<brief>"}}"""


def parse_response(raw_text, var_type):
    try:
        data = json.loads(raw_text.strip())
    except json.JSONDecodeError:
        m = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(0))
            except json.JSONDecodeError:
                return {'extracted_value': 'PARSE_ERROR', 'confidence': 'low',
                        'source_text': '', 'reasoning': ''}
        else:
            return {'extracted_value': 'PARSE_ERROR', 'confidence': 'low',
                    'source_text': '', 'reasoning': ''}

    raw_val = str(data.get('extracted_value', 'NOT_FOUND'))

    if var_type == 'numeric':
        if raw_val in ('NOT_FOUND', 'PARSE_ERROR', ''):
            data['extracted_value'] = None
        else:
            negative = raw_val.startswith('(') and raw_val.endswith(')')
            cleaned  = re.sub(r'[\$,\s()]', '', raw_val)
            m = re.search(r'-?[\d]+', cleaned)
            if m:
                val = float(m.group(0))
                data['extracted_value'] = -abs(val) if negative else val
            else:
                data['extracted_value'] = None
    else:
        if raw_val in ('NOT_FOUND', 'PARSE_ERROR', ''):
            data['extracted_value'] = None
        else:
            data['extracted_value'] = raw_val.strip().strip('"\'')

    return data
