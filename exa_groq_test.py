import os
from dotenv import load_dotenv
from exa_py import Exa
from groq import Groq

load_dotenv()

exa = Exa(api_key=os.getenv("EXA_API_KEY"))
groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

results = exa.search_and_contents(
    query="latest bitcoin news",
    category="news",
    num_results=3,
    text=True
)

content = "\n\n".join(
    f"{r.title}\n{(r.text or '')[:1000]}"
    for r in results.results
)

print("content by exa-api\n", content)

response = groq.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": "Summarize the news."
        },
        {
            "role": "user",
            "content": content
        }
    ]
)

print("news response summary \n",response.choices[0].message.content)