from fastapi import FastAPI
from pydantic import BaseModel
from score_engine import calc_fatigue

app = FastAPI()

# 入力形式
class TextInput(BaseModel):
    texts: list[str]

# APIエンドポイント
@app.post("/score")
def score(data: TextInput):
    result = calc_fatigue(data.texts)
    return result
