import os
import re
import time
import requests

# Hugging Faceで動かす軽量・高性能な多言語モデル
MODEL_ID = "intfloat/multilingual-e5-small"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"

# Renderの管理画面（Environment）に設定したトークンを安全に読み込みます
HF_TOKEN = os.environ.get("HUGGINGFACE_TOKEN", "")

def query_huggingface(texts):
    """Hugging Face Inference APIを使って文章のベクトル（埋め込み）を取得する"""
    headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
    payload = {"inputs": [f"query: {t}" for t in texts]}
    
    for _ in range(3): # サーバー起動待ちなどでエラーが出た場合、3回までリトライ
        try:
            response = requests.post(API_URL, json=payload, headers=headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 503: # モデルの読み込み中（睡眠からの起床待ち）
                time.sleep(4)
            else:
                print(f"Hugging Face API Error: {response.status_code} - {response.text}")
                break
        except Exception as e:
            print(f"Hugging Face 通信エラー: {e}")
            time.sleep(2)
    return None

def cosine_similarity(v1, v2):
    """2つのベクトルのコサイン類似度を計算"""
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_a = sum(a * a for a in v1) ** 0.5
    norm_b = sum(b * b for b in v2) ** 0.5
    if not norm_a or not norm_b:
        return 0.0
    return dot_product / (norm_a * norm_b)

def normalize(text):
    text = text.lower()
    text = re.sub(r"[\s、。！？!?\.]+", "", text)
    return text

refs = {
    "brain": "スマホ SNS YouTube 勉強 情報が多くて頭が疲れる パソコン 目が痛い 集中できない パソコン作業 画面",
    "mental": "ストレス しんどい 無理 やる気が出ない 心が疲れる 落ち込む イライラする 辛い もやもや 緊張",
    "body": "座りっぱなし 眠い 体がだるい 体力がない 肩こり 筋肉痛 立ち仕事 疲労 身体が重い 疲れた"
}

def analyze_voice_fatigue_safe(audio_bytes):
    """音声のデータサイズから声の疲労を模擬判定（100%安全なロジック）"""
    if not audio_bytes:
        return 0.4
    audio_size = len(audio_bytes)
    if audio_size < 40000:
        return 0.8
    elif audio_size < 120000:
        return 0.5
    else:
        return 0.3

def calc_fatigue(texts, audio_bytes):
    combined_text = " ".join(texts)
    norm_text = normalize(combined_text)

    target_keys = list(refs.keys())
    all_texts = [norm_text] + [refs[k] for k in target_keys]
    
    # クラウドAI（Hugging Face）にお問い合わせ
    embeddings = query_huggingface(all_texts)
    
    text_scores = {"brain": 0.2, "mental": 0.2, "body": 0.2}
    category = "unknown"

    if embeddings and len(embeddings) == len(all_texts):
        user_emb = embeddings[0]
        for i, key in enumerate(target_keys):
            ref_emb = embeddings[i + 1]
            text_scores[key] = cosine_similarity(user_emb, ref_emb)
        category = max(text_scores, key=text_scores.get)
    else:
        print("Hugging Face APIが寝ているため、簡易マッチに切り替えます")
        for key in text_scores.keys():
            if any(w in norm_text for w in refs[key].split()):
                text_scores[key] = 0.5
        category = max(text_scores, key=text_scores.get)

    voice_fatigue_factor = analyze_voice_fatigue_safe(audio_bytes)
    voice_bonus = voice_fatigue_factor * 25

    brain = min(max(round(text_scores["brain"] * 100 + voice_bonus), 10), 100)
    mental = min(max(round(text_scores["mental"] * 100 + voice_bonus + (10 if category == "mental" else 0)), 10), 100)
    body = min(max(round(text_scores["body"] * 100 + voice_bonus), 10), 100)

    if max(text_scores.values()) < 0.35 and voice_fatigue_factor < 0.5:
        category = "unknown"
        brain, mental, body = 15, 15, 15

    total = (brain + mental + body) / 3

    return {
        "brain": brain,
        "mental": mental,
        "body": body,
        "total": round(total, 1),
        "category": category
    }
