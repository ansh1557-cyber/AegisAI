from engine.news_filter import NewsFilter

news = NewsFilter()

print("Trading Allowed :", news.allowed())
print("Reason          :", news.reason())
print("Next Event      :", news.next_event())