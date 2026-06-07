def recommend(score):
    rec = []
    
    # 深刻度の判定
    is_severe = score["total"] > 70

    if score["brain"] > 55:
        if is_severe:
            rec.append("【即実践】画面を全て消し、ホットアイマスクか濡れタオルを5分目元に当ててください（情報の完全遮断）。")
        else:
            rec.append("スマホを置いて、遠くの景色や部屋の観葉植物をぼーっと眺める時間を3分作りましょう。")

    if score["mental"] > 55:
        if is_severe:
            rec.append("【心のリセット】4秒吸って8秒吐く深呼吸を5回繰り返してください。お気に入りのスローテンポな音楽を聴くのも効果的です。")
        else:
            rec.append("温かい白湯やノンカフェインのお茶を淹れて、一口ずつゆっくり味わってみてください。")

    if score["body"] > 55:
        if is_severe:
            rec.append("【身体のケア】座りっぱなしで血流が滞っています。立ち上がって、首・肩を大きく後ろに5回回しましょう。")
        else:
            rec.append("背伸びを大きく1回して、固まった腰まわりを左右にゆっくりひねってほぐしてください。")

    # 特化型ではない、または全体の疲労が低い場合
    if not rec or score["total"] < 35:
        rec.append("今のところバランスは良好です。お気に入りの癒やし動画を1本見て、今のうちに軽くリフレッシュしておきましょう。")

    return rec
