def recommend(brain, mental, body):

    videos = {
        "brain": [
            "5分目の目のストレッチ",
            "デジタルデトックスBGM",
            "散歩用リラックス音楽"
        ],
        "mental": [
            "深呼吸ガイド",
            "自己肯定感を回復する動画",
            "何もしなくていい時間の作り方"
        ],
        "body": [
            "肩こりストレッチ",
            "姿勢改善エクササイズ",
            "寝る前リラックスBGM"
        ]
    }

    result = []

    # メイン疲労を判定
    if brain >= mental and brain >= body:
        result += videos["brain"][:2]

    elif mental >= brain and mental >= body:
        result += videos["mental"][:2]

    else:
        result += videos["body"][:2]

    # サブ1本追加（軽いやつ）
    result.append("3分リラックスBGM")

    return result
