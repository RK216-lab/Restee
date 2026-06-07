import re
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

def normalize(text):
    text = text.lower()
    text = re.sub(r"\s+", "", text)
    text = text.replace("なんか", "")
    text = text.replace("えー", "")
    return text


refs = {
    "brain": "スマホ SNS YouTube 勉強 情報が多くて頭が疲れる",
    "mental": "ストレス しんどい 無理 やる気が出ない 心が疲れる",
    "body": "座りっぱなし 眠い 体がだるい 体力がない"
}


def classify(text):
    text = normalize(text)
    text_emb = model.encode(text, convert_to_tensor=True)

    scores = {}

    for k, ref in refs.items():
        ref_emb = model.encode(ref, convert_to_tensor=True)
        sim = util.pytorch_cos_sim(text_emb, ref_emb).item()
        scores[k] = sim

    best = max(scores, key=scores.get)

    return best, scores


def calc_fatigue(texts):

    text = " ".join(texts)

    category, scores = classify(text)

    brain = 0
    mental = 0
    body = 0

    if max(scores.values()) < 0.25:
        category = "unknown"

    if category == "brain":
        brain = 60
    elif category == "mental":
        mental = 60
    elif category == "body":
        body = 60

    total = (brain + mental + body) / 3

    return {
        "brain": brain,
        "mental": mental,
        "body": body,
        "total": round(total, 1),
        "category": category
    }