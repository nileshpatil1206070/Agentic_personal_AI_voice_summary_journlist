
from exa_py import Exa
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

from dotenv import load_dotenv
import os

from pathlib import Path

print(Path(".env").exists())

load_dotenv()
print(os.getenv("EXA_API_KEY"))

# Initialize Exa client
exa = Exa(api_key=os.getenv("EXA_API_KEY"))


# Search for the latest AI news and retrieve content
results = exa.search_and_contents(
    query="latest bitcoin news",
    category="news",
    num_results=3,
    text=True,
)

# Print the results
for result in results.results:
    print(f"TITLE: {result.title}")
    print(f"URL: {result.url}")
    print(f"TEXT: {result.text[:200]}")
    print("-" * 80)


