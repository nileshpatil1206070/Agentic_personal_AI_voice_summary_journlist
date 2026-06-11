# utils.py will be created for other functions which will be used in news scraping, HTML content, etc for out main project
# we will create a function - when we give the topic - it will return query url -https://news.google.com/search?q=climate%20change&hl=en-GB&gl=GB&ceid=GB%3Aen

from urllib.parse import quote_plus

import os
from dotenv import load_dotenv

from exa_py import Exa
from groq import Groq

from elevenlabs.client import ElevenLabs

from datetime import datetime

load_dotenv()


# =========================
# API Clients
# =========================

exa_client = Exa(
    api_key=os.getenv("EXA_API_KEY")
)

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# =========================
# EXA NEWS SEARCH
# =========================
# =========================
# EXA NEWS SEARCH (OPTIMIZED FOR FREE TIER)
# =========================

def get_news_from_exa(topic: str, num_results: int = 2) -> str:
    """
    Fetch latest news headlines and short highlights to save Exa credits.
    """
    # Using highlights=True uses significantly fewer tokens/credits than full text=True
    results = exa_client.search_and_contents(
        query=topic,
        category="news",
        num_results=num_results,
        highlights={"num_sentences": 2}  # Gets just the core summary
    )

    content = []

    for result in results.results:
        # Check for highlights first, fall back to snippet if available
        summary = result.highlights[0] if result.highlights else "No summary available."
        content.append(
            f"TITLE: {result.title}\nSUMMARY: {summary}"
        )

    return "\n\n".join(content)


# =========================
# EXA REDDIT SEARCH (OPTIMIZED FOR FREE TIER)
# =========================

def get_reddit_from_exa(topic: str, num_results: int = 2) -> str:
    """
    Fetch quick Reddit discussion summaries to save Exa credits.
    """
    results = exa_client.search_and_contents(
        query=f"{topic}",
        include_domains=["reddit.com"],
        num_results=num_results,
        highlights={"num_sentences": 2}  # Drops heavy text payloads
    )

    content = []

    for result in results.results:
        summary = result.highlights[0] if result.highlights else "No summary available."
        content.append(
            f"REDDIT POST: {result.title}\nDISCUSSION HIGHLIGHT: {summary}"
        )

    return "\n\n".join(content)



# =========================
# GROQ SUMMARIZER
# =========================

def summarize_content_groq(content: str) -> str:

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": """

                You are an expert news analyst.


                Summarize the information into concise bullet points.
                Focus on important developments and facts.
                """
            },
            {
                "role": "user",
                "content": content
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content


# =========================
# BROADCAST GENERATOR
# =========================

def generate_broadcast_news(
    news_data: dict,
    reddit_data: dict,
    topics: list
):

    topic_blocks = []

    for topic in topics:

        news_content = (
            news_data.get("news_analysis", {}).get(topic, "")
            if news_data else ""
        )

        reddit_content = (
            reddit_data.get("reddit_analysis", {}).get(topic, "")
            if reddit_data else ""
        )

        combined = []

        if news_content:
            combined.append(
                f"NEWS SUMMARY:\n{news_content}"
            )

        if reddit_content:
            combined.append(
                f"REDDIT DISCUSSION:\n{reddit_content}"
            )

        if combined:
            topic_blocks.append(
                f"""

                TOPIC: {topic}


                {chr(10).join(combined)}
                """
            )

    final_prompt = "\n\n".join(topic_blocks)

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": """

                You are a professional radio journalist.


                Create a natural spoken news broadcast.


                Requirements:

                - Conversational

                - Easy to listen to

                - Combine official news and public sentiment

                - No bullet points

                - Produce a continuous script suitable for text-to-speech
                - only 100 words maximum not more
                - word limit is 100 words only -i.e maximum 100 words

                """
            },
            {
                "role": "user",
                "content": final_prompt
            }
        ],
        temperature=0.4
    )

    return response.choices[0].message.content


# =========================
# ELEVENLABS TTS
# =========================

def text_to_audio_elevenlabs(
    text: str,
    output_dir: str = "audio"
):

    client = ElevenLabs(
        api_key=os.getenv("ELEVEN_API_KEY")
    )

    audio = client.text_to_speech.convert(
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_multilingual_v2",
        text=text
    )

    os.makedirs(output_dir, exist_ok=True)

    filename = (
        f"news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
    )

    filepath = os.path.join(output_dir, filename)

    with open(filepath, "wb") as f:
        for chunk in audio:
            f.write(chunk)

    return filepath