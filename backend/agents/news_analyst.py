from .base_agent import BaseAgent
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from modules.nse_live_feed import nse_live_feed

class NewsAnalyst(BaseAgent):
    """
    Agent 02: Real-Time News & Sentiment Analyst
    Scrapes and analyzes live financial news feeds from Moneycontrol, Economic Times, and LiveMint.
    """
    def __init__(self):
        super().__init__("News Analyst", "Live Financial News Ingestion & Sentiment Analysis")
        self.analyzer = SentimentIntensityAnalyzer()

    def analyze(self, symbol: str = "MARKET"):
        self.log(f"Fetching real-time financial headlines for {symbol}...")
        news_items = nse_live_feed.get_financial_news(limit=10)
        
        if not news_items:
            return {"sentiment": "NEUTRAL", "score": 0.0, "count": 0, "headlines": []}

        total_score = 0
        scored_headlines = []
        for item in news_items:
            sentiment = self.analyzer.polarity_scores(item['title'])
            compound = sentiment['compound']
            total_score += compound
            scored_headlines.append({
                "title": item['title'],
                "source": item['source'],
                "published": item.get('published', 'Live'),
                "score": round(compound, 2),
                "bias": "BULLISH" if compound > 0.05 else ("BEARISH" if compound < -0.05 else "NEUTRAL")
            })

        avg_score = total_score / len(news_items) if news_items else 0.0
        
        if avg_score >= 0.10:
            mkt_sentiment = "BULLISH"
        elif avg_score <= -0.10:
            mkt_sentiment = "BEARISH"
        else:
            mkt_sentiment = "NEUTRAL"

        return {
            "sentiment": mkt_sentiment,
            "score": round(avg_score, 3),
            "count": len(news_items),
            "headlines": scored_headlines
        }
