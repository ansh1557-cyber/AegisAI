from engine.institutional_score import InstitutionalScore

score = InstitutionalScore()

score.add_buy(30, "H4 Bullish")
score.add_buy(20, "H1 Bullish")
score.add_buy(15, "Bullish Order Block")
score.add_buy(10, "Discount Zone")

score.add_sell(10, "Premium Zone")

score.print_result()