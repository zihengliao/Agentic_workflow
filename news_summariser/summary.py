import requests
from markdownify import markdownify
from serpapi import GoogleSearch
from langchain_community.llms import Ollama
import argparse
from tqdm import tqdm
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)



def get_api_key():
    with open("api_key.txt", "r") as file:
        content = file.read()
    return str(content)


def google_search(query):

    api_key = get_api_key()

    params = {
    "engine": "google_news",
    "q": query,
    "gl": "us",
    "hl": "en",
    "api_key": api_key
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    news_results = results["news_results"]

    return news_results


def get_ollama_client():

    # running this locally
    ollama = Ollama(
        model="qwen2:7b",
        base_url="http://localhost:11434"
    )
    return ollama


def summarise_news(query, news_results):

    ai_summary_collation = ""
    links_visited = ""
    ollama = get_ollama_client()

    # scraping only the first 10 news articles cause of token limit
    news_results = news_results[:10]

    for dic in tqdm(news_results, desc="Reading news articles"):
        url = dic["link"]
        
        headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.google.com/",  # trying to avoid bot detection
    }
        try: 
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()

            markdown_content = markdownify(response.text).strip() + "\n\n"

            ai_summary = ollama.invoke(f"summarise the following in regards to: {query}" + markdown_content)   
            ai_summary_collation += ai_summary + "\n"

            links_visited += url + "\n"

            # some news sites block bots or have a paywall, so we handle exceptions
        except requests.RequestException as e:  
            # print(f"Error fetching {url}: {e}")
            continue

    final_summary = ollama.invoke(f"You're an expert financial analyst who offers top notch advice. I'm an amateur who is \
                                  interested in the latest news regarding my stock ({query}) so respond accordingly as an expert and change your language to be so as well. \
                                  Summarise the following information into a small paragraph and tell me whether this is \
                                  an overall positive or negative: \n\n" + ai_summary_collation)
    print(links_visited)

    return final_summary


def main():
    parser = argparse.ArgumentParser(description="Summarise the latest news.")
    parser.add_argument("-q", type=str, required=True, help="Search query for news articles")
    args = parser.parse_args()

    query = args.q
    print(f"Searching for the latest news articles related to: {query}")
    news_results = google_search("latest news for" + query)

    if not news_results:
        print("No news articles found for the given query.")
        return

    summary = summarise_news(query, news_results)
    print(summary)
