from fastapi import FastAPI
from pydantic import BaseModel

from score_engine import calc_fatigue
from recommender import recommend

app = FastAPI()

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
