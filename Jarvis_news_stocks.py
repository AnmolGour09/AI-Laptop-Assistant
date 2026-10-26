import os
import requests
import logging
from livekit.agents import function_tool
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

@function_tool
async def get_news(topic: str = "technology", country: str = "us") -> str:
    """Fetch latest news articles
    
    Args:
        topic: News category (e.g., technology, business, sports, health, science)
        country: Country code (e.g., us, in, uk, ca)
    """
    try:
        api_key = os.getenv("NEWS_API_KEY")
        
        if not api_key:
            return "Error: NEWS_API_KEY not set in .env. Get one free from newsapi.org"
        
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "category": topic,
            "country": country,
            "apiKey": api_key,
            "pageSize": 5
        }
        
        logger.info(f"Fetching {topic} news for {country}...")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"News API error: {response.status_code}")
            return f"Error fetching news: {response.status_code}"
        
        data = response.json()
        articles = data.get("articles", [])
        
        if not articles:
            return f"No news articles found for '{topic}' in {country}"
        
        news_list = "\n\n".join([
            f"📰 {article['title']}\n{article['description']}"
            for article in articles[:5]
        ])
        
        return f"Top {topic.capitalize()} News:\n{news_list}"
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return f"Error fetching news: {str(e)}"
    except Exception as e:
        logger.error(f"Error getting news: {str(e)}")
        return f"Error: {str(e)}"

@function_tool
async def get_stock_price(symbol: str) -> str:
    """Get current stock price
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, GOOGL, MSFT)
    """
    try:
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        
        if not api_key:
            return "Error: ALPHA_VANTAGE_API_KEY not set in .env. Get one free from alphavantage.co"
        
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol.upper(),
            "apikey": api_key
        }
        
        logger.info(f"Fetching stock price for {symbol}...")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"Stock API error: {response.status_code}")
            return f"Error fetching stock: {response.status_code}"
        
        data = response.json()
        quote = data.get("Global Quote", {})
        
        if not quote:
            return f"Stock symbol '{symbol}' not found"
        
        price = quote.get("05. price", "N/A")
        change = quote.get("09. change", "N/A")
        change_percent = quote.get("10. change percent", "N/A")
        
        result = f"""
Stock: {symbol.upper()}
Price: ${price}
Change: {change} ({change_percent})
"""
        logger.info(f"Stock price for {symbol}: ${price}")
        return result.strip()
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return f"Error fetching stock: {str(e)}"
    except Exception as e:
        logger.error(f"Error getting stock price: {str(e)}")
        return f"Error: {str(e)}"
