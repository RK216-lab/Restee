def recommend(score):

    rec = []

    if score["brain"] > 50:
        rec.append("短い休憩で情報遮断しよう")

    if score["mental"] > 50:
        rec.append("深呼吸・音楽でリラックス")

    if score["body"] > 50:
        rec.append("ストレッチして体ほぐそう")

    if not rec:
        rec.append("軽く休憩しよう")

    return rec