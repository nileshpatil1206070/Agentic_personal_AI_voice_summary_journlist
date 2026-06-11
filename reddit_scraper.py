#reddit scraper using mcp protocol etc

from typing import List
import os
from utils import *
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
from aiolimiter import AsyncLimiter
from datetime import datetime, timedelta

load_dotenv

server_params = stdioServerParameters(
    command="npx",
    env = {
        "API_TOKEN":os.getenv{"API_TOKEN"}
        "WEB_UNLOCKER_ZONE": os.getenv("WEB_UNLOCKER_ZONE")

    },
    args=["@brightdata/mcp"]
)

model = ChatAnthropic(model="claude-3-5-sonnet-20240620")

async def scrape_reddit_topics(topics: List[str]) -> dict[str,dict]:
    """process list of topics and return analysis results"""

    async with stdio_client(server_params) as (read,write):
        async with ClientSession(read,write) as sessions:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(model, tools)

            reddit_results = {}
            for topic in topics:
                summary = await process_topic(agent, topic)
                reddit_results[topic] = summary
                await asyncio.sleep(5) # maintain rate limiting

            return {"reddit_analysis": reddit_results}


mcp_limiter = AsyncLimiter(1,15)

two_weeks_ago = datetime.today() - timedelta(days=14)
two_weeks_ago_str = two_weeks_ago.strftime('%Y-%m-%d')

async def process_topic(agent, topic: str):
    async with mcp_limiter:
        messages = [
            {
                "role":"system",
                "content": f"""you are reddit analysis expert
                and find out 2 posts about given topic only after{two_weeks_ago_str}"""
            },

            {
                "role":"user",
                "content": f"""analyze reddit post about '{topic}'.
                provide a comprehensive summary"""
            }
        ]

        try:
            response = await agent.aiinvoke({"messages":messages})
            return response["messages"][-1].content
        except Exception as e:
            raise e