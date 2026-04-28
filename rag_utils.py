import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SOURCE_TEXT_PATH  = 'data/aig_source_text2019.txt'
GROUND_TRUTH_PATH = 'data/ground_truth2019.csv'

def clean_text(text):
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def chunk_text(text, year, chunk_size=2000, overlap=400):
    text = clean_text(text)
    chunks, start, idx = [], 0, 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append({
            'chunk_id':   f'{year}_{idx}',
            'chunk_text': text[start:end],
            'start_char': start,
            'end_char':   end,
        })
        idx   += 1
        start += chunk_size - overlap
    return chunks

def build_tfidf(chunks):
    texts = [c['chunk_text'] for c in chunks]
    vectorizer = TfidfVectorizer(max_features=20_000, stop_words='english')
    matrix = vectorizer.fit_transform(texts)
    return vectorizer, matrix

def retrieve_top_k(chunks, vectorizer, matrix, query_text, k=5):
    q_vec  = vectorizer.transform([query_text])
    scores = cosine_similarity(q_vec, matrix)[0]
    top_idx = scores.argsort()[::-1][:k]
    return [{**chunks[i], 'score': float(scores[i])} for i in top_idx]

