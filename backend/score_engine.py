from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

brain_refs = {
    "スマホ疲労": "スマホ SNS TikTok YouTube 無限スクロール",
    "勉強疲労": "勉強 暗記 テスト 集中できない",
}
def semantic_score(text, refs):
    text_emb = model.encode(text, convert_to_tensor=True)

    score = 0

    for _, ref in refs.items():
        ref_emb = model.encode(ref, convert_to_tensor=True)
        sim = util.pytorch_cos_sim(text_emb, ref_emb).item()

        if sim > 0.5:
            score += 40

    return score
    
def calc_fatigue(texts):
    text = " ".join(texts)

    brain = 0
    mental = 0
    body = 0

    brain += semantic_score(text, brain_refs)

    brain_keywords = {
        "スマホ": 30,
        "SNS": 30,
        "情報": 20,
        "無限スクロール": 40,
        "勉強": 20,
        "暗記": 25
    }

    for k, v in brain_keywords.items():
        if k in text:
            brain += v

    strong = ["しんどい", "無理", "限界", "もうやだ"]
    mid = ["だるい", "やる気出ない", "疲れた", "めんどい"]
    light = ["眠い", "ぼーっと", "ちょっと疲れ"]

    for w in strong:
        if w in text:
            mental += 45

    for w in mid:
        if w in text:
            mental += 25

    for w in light:
        if w in text:
            mental += 10

    vague_boost = ["なんか", "とりあえず", "全体的に"]
    for w in vague_boost:
        if w in text:
            mental += 10

    body_keywords = {
        "座りっぱなし": 30,
        "通学": 20,
        "だるい": 10,
        "眠い": 15
    }

    for k, v in body_keywords.items():
        if k in text:
            body += v

    brain = max(0, min(brain, 100))
    mental = max(0, min(mental, 100))
    body = max(0, min(body, 100))

    total = (brain + mental + body) / 3

    return {
        "brain": brain,
        "mental": mental,
        "body": body,
        "total": round(total, 1)
    }
