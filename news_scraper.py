#phase 3-News scraper
#1.Setup scraper with BrightData at MCP
#2.Text to scraping with BrightData
#3.Setup Fast API endpoint
#4.Bring everything together

# we will also create utils file python and inside we will create functions

from utils import *
from typing import Dict, List
import asyncio

import os
from aiolimiter import AsyncLimiter
from dotenv import load_dotenv

load_dotenv()

class NewsScraper:
    _rate_limiter = AsyncLimiter(5,1) # 5 requests/sec

    async def scrape_news(self, topics: List[str]) -> Dict[str,str]:

        """scrape and analyse news articles"""

        results ={}

        for topic in topics:
            async with self.rate_limiter:
                try:
                    urls=generate_news_to_scrape([topic])
                    search_html = scrape_with_exa_api(urls[topic])
                    clean_text = clean_html_to_text(search_html)
                    headlines = extract_headlines(clean_text)
                    summary = summarize_news_groq_cloud_llama_instant(
                        api_key=api_key,
                        headlines=headlines
                    )
                    results[topic] = summary

                except Exception as e:
                    results[topic] = f"Error: {str(e)}"

                await asyncio.sleep(1)

            return {"news_analysis": results}