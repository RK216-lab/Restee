from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from score_engine import calc_fatigue
from recommender import recommend

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputData(BaseModel):
    texts: list[str]

@app.post("/analyze")
def analyze(data: InputData):

    score = calc_fatigue(data.texts)

    rec = recommend(score)

    return {
        "score": score,
        "recommendations": rec
    }