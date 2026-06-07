  def calc_fatigue(texts):
    text = " ".join(texts)

    brain = 0
    mental = 0
    body = 0

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

    brain = min(max(brain, 0), 100)
    mental = min(max(mental, 0), 100)
    body = min(max(body, 0), 100)

    total = (brain + mental + body) / 3

    return {
        "brain": brain,
        "mental": mental,
        "body": body,
        "total": round(total, 1)
    }
