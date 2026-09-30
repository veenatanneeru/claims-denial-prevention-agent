"""TF-IDF retrieval over the policy documents. Light enough for a 512 MB host."""
from functools import lru_cache
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

POLICY_DIR = Path(__file__).resolve().parents[2] / "data" / "policies"


@lru_cache(maxsize=1)
def _index():
    files = sorted(POLICY_DIR.glob("*.md"))
    texts = [f.read_text() for f in files]
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(texts)
    return files, texts, vectorizer, matrix


def search(query: str, k: int = 3) -> list[dict]:
    files, texts, vectorizer, matrix = _index()
    scores = cosine_similarity(vectorizer.transform([query]), matrix)[0]
    ranked = scores.argsort()[::-1][:k]
    return [{"source": files[i].name, "text": texts[i]} for i in ranked]