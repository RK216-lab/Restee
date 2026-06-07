import re
import os
import json
import tempfile
import opensmile
from sentence_transformers import SentenceTransformer, util

# テキスト用モデルの初期化
text_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# openSMILEの初期化（eGeMAPS特徴量セットを使用）
smile = opensmile.Smile(
    feature_set=opensmile.FeatureSet.eGeMAPS,
    feature_level=opensmile.FeatureLevel.Functionals,
)

def normalize(text):
    text = text.lower()
    text = re.sub(r"\s+", "", text)
    text = text.replace("なんか", "").replace("えー", "").replace("あの", "")
    return text

refs = {
    "brain": "スマホ SNS YouTube 勉強 情報が多くて頭が疲れる パソコン 目が痛い 集中できない",
    "mental": "ストレス しんどい 無理 やる気が出ない 心が疲れる 落ち込む イライラする 辛い",
    "body": "座りっぱなし 眠い 体がだるい 体力がない 肩こり 筋肉痛 立ち仕事 疲労"
}

def analyze_voice_fatigue(audio_bytes):
    """
    openSMILE (eGeMAPS) を使って音声から声の疲労・ストレス度を簡易判定する
    """
    if not audio_bytes:
        return 0.0

    try:
        # WebMなどのバイナリデータを一時ファイルに保存
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
            temp_audio.write(audio_bytes)
            temp_path = temp_audio.name

        # openSMILEで特徴量を抽出 (Pandas DataFrameが返る)
        features = smile.process_file(temp_path)
        os.remove(temp_path)  # 一時ファイルの削除

        # eGeMAPSから声の元気がなくなる指標（ピッチの平均やジッター、発話エネルギーなど）を取得
        # ※一般的にストレスや疲労でF0の平均が下がったり、声の輝き（alphaRatio）が変わる
        f0_mean = float(features["F0semitoneFrom27.5Hz_sma3nz_amean"].iloc[0])
        shimmer_mean = float(features["shimmerLocaldB_sma3nz_amean"].iloc[0])
        
        # 簡易的な音声ストレススコア（0.0 ~ 1.0）の計算ロジック
        # 声の揺らぎ（シマー）が大きい、またはトーンが極端に低い場合に数値を上げる
        voice_stress = 0.3
        if shimmer_mean > 1.5: voice_stress += 0.2
        if f0_mean < 20.0: voice_stress += 0.2 # 低く沈んだ声

        return min(voice_stress, 1.0)
    except Exception as e:
        print(f"openSMILE解析エラー (モック値で代用します): {e}")
        return 0.4 # エラー時は平均的な疲労度を返す

def classify_text(text):
    text = normalize(text)
    text_emb = text_model.encode(text, convert_to_tensor=True)

    scores = {}
    for k, ref in refs.items():
        ref_emb = text_model.encode(ref, convert_to_tensor=True)
        sim = util.pytorch_cos_sim(text_emb, ref_emb).item()
        scores[k] = sim

    best = max(scores, key=scores.get)
    return best, scores

def calc_fatigue(texts, audio_bytes):
    # 3ターンのテキストを結合
    combined_text = " ".join(texts)

    # 1. テキスト分析
    category, text_scores = classify_text(combined_text)
    max_text_sim = max(text_scores.values())

    # 2. 音声分析 (openSMILE)
    voice_fatigue_factor = analyze_voice_fatigue(audio_bytes)

    # 3. 3軸スコアの計算 (テキスト類似度ベース + 声の疲労度によるブースト)
    # 類似度が低くても声が疲れていればベースラインが上がる仕様
    brain_base = text_scores["brain"] * 100
    mental_base = text_scores["mental"] * 100
    body_base = text_scores["body"] * 100

    # 音声の疲労要因をボーナスとして加算 (最大+30点)
    voice_bonus = voice_fatigue_factor * 30

    brain = min(round(brain_base + voice_bonus), 100)
    mental = min(round(mental_base + voice_bonus + (10 if category == "mental" else 0)), 100)
    body = min(round(body_base + voice_bonus), 100)

    # 判定の閾値
    if max_text_sim < 0.20 and voice_fatigue_factor < 0.3:
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
