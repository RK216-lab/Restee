from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from score_engine import calc_fatigue
from recommender import recommend

app = FastAPI()

# 🌐CORS（フロント接続用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputData(BaseModel):
    texts: list[str]

@app.post("/analyze")
def analyze(data: InputData):

    score = calc_fatigue(data.texts)

    videos = recommend(
        score["brain"],
        score["mental"],
        score["body"]
    )

    return {
        "score": score,
        "recommendations": videos
    }
