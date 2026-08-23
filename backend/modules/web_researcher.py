import requests
from bs4 import BeautifulSoup
import pandas as pd
from nsepython import nse_get_top_gainers, nse_get_top_losers

class WebResearcher:
    """
    Finds the best stocks for intraday trading by sourcing internet data.
    """
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0'}

    def get_top_movers(self):
        """Fetch top gainers and losers from NSE"""
        try:
            gainers = nse_get_top_gainers()
            losers = nse_get_top_losers()
            return {
                "gainers": gainers['symbol'].tolist() if not gainers.empty else [],
                "losers": losers['symbol'].tolist() if not losers.empty else []
            }
        except Exception as e:
            print(f"Error fetching top movers: {e}")
            return {"gainers": [], "losers": []}

    def get_trending_stocks(self):
        """
        Fetch real trending stocks from Live NSE Data
        """
        trending = []
        try:
            # Using nsepython for real-time market data instead of scraping mock data
            from nsepython import nse_get_index_quotes
            data = nse_get_index_quotes("NIFTY 50")
            if 'data' in data:
                # Sort by % change to find truly trending stocks
                sorted_stocks = sorted(data['data'], key=lambda x: float(x['pChange']), reverse=True)
                trending = [stock['symbol'] for stock in sorted_stocks[:10]]
        except Exception as e:
            print(f"Error fetching live NSE trending stocks: {e}")
        return trending

    def search_hot_stocks(self):
        """Combine real NSE movers to find hot intraday stocks"""
        movers = self.get_top_movers()
        trending = self.get_trending_stocks()
        
        # Merge and prioritize real data
        hot_list = list(dict.fromkeys(movers['gainers'] + movers['losers'] + trending))
        return hot_list[:15]
