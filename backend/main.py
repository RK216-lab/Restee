import json
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from score_engine import calc_fatigue
from recommender import recommend

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(
    texts: str = Form(...),  # JSON文字列として受け取る
    audio: UploadFile = File(...)
):
    # JSON文字列をリストにパース
    text_list = json.loads(texts)

    # 音声データを一時的にバイナリとして読み込む
    audio_bytes = await audio.read()

    # スコア計算エンジンを呼び出す（テキストと音声を両方渡す）
    score = calc_fatigue(text_list, audio_bytes)

    # 推薦ロジック
    rec = recommend(score)

    return {
        "score": score,
        "recommendations": rec
    }
