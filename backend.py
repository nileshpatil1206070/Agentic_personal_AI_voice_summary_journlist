# phase two setup - backend logic
# 1. scrape data
# 2. send to LLM summarizer
# 3. convert to audio
# 4. send to frontend

import base64
import os
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

from models import NewsRequest
from utils import (
    get_news_from_exa,
    get_reddit_from_exa,
    summarize_content_groq,
    generate_broadcast_news,
    text_to_audio_elevenlabs
)

load_dotenv()

app = FastAPI()


@app.post("/generate-news-audio")

    
async def generate_news_audio(request: NewsRequest):

    print("REQUEST RECEIVED:", request)
    print("REQUEST:", request)
    print("TOPICS:", request.topics)
    print("SOURCE:", request.source_type)
 
    try:
        news_results = {}
        reddit_results = {}

        # =========================
        # NEWS SEARCH
        # =========================
        if request.source_type.lower() in ["news", "both"]:
            for topic in request.topics:
                raw_news = get_news_from_exa(topic)
                summary = summarize_content_groq(raw_news)
                news_results[topic] = summary

        # =========================
        # REDDIT SEARCH
        # =========================
        if request.source_type.lower() in ["reddit", "both"]:
            for topic in request.topics:
                raw_reddit = get_reddit_from_exa(topic)
                summary = summarize_content_groq(raw_reddit)
                reddit_results[topic] = summary

        # =========================
        # FINAL BROADCAST SCRIPT
        # =========================
        broadcast_script = generate_broadcast_news(
            news_data={"news_analysis": news_results},
            reddit_data={"reddit_analysis": reddit_results},
            topics=request.topics
        )

        # =========================
        # TEXT TO SPEECH
        # =========================
        # =========================
        # COMBINE NEWS & REDDIT DATA (REPLACES BROADCAST SCRIPT)
        # =========================
        combined_text_list = []
        
        if news_results:
            combined_text_list.append("📰 --- OFFICIAL NEWS SUMMARIES ---")
            for topic, text in news_results.items():
                combined_text_list.append(f"• {topic.upper()}:\n{text}")
                
        if reddit_results:
            combined_text_list.append("\n💬 --- REDDIT DISCUSSION SUMMARIES ---")
            for topic, text in reddit_results.items():
                combined_text_list.append(f"• {topic.upper()}:\n{text}")

        # This joins everything into a clean paragraph summary layout
        clean_text_summary = "\n\n".join(combined_text_list)

        # Fallback if everything was empty
        if not clean_text_summary:
            clean_text_summary = "No news or Reddit summaries could be generated."

        # =========================
        # TEXT TO SPEECH (Reads the clean text summary instead)
        # =========================
        audio_path = text_to_audio_elevenlabs(
            text=clean_text_summary
        )

        # Read the binary audio data
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()

        # Convert raw binary bytes into a Base64 UTF-8 string for JSON transmission
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

        if os.path.exists(audio_path):
            os.remove(audio_path)

        # Return both the text script and the audio payload together
        return {
            "summary": clean_text_summary,  # Frontend gets the clean string under the same key!
            "audio_bytes": audio_b64
        }


    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/")
async def home():
    return {
        "message": "AI Voice Journalist Backend Running"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend:app",
        host="0.0.0.0",
        port=1234,
        reload=True
    )
