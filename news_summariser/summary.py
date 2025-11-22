import requests
from markdownify import markdownify
from serpapi import GoogleSearch
from langchain_community.llms import Ollama
import argparse
from tqdm import tqdm
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from concurrent.futures import ThreadPoolExecutor, as_completed



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

    def process_single_article(dic):
        """Fetch + markdownify + local summary for ONE article."""
        # Find correct link
        try:
            url = dic["link"]
        except:
            if "stories" in dic:
                url = dic["stories"][0]["link"]
            else:
                return None, None  # skip this item

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/115.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.google.com/",
        }

        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()

            markdown_content = markdownify(response.text).strip() + "\n\n"

            # Summarise with ollama (this will run in the worker thread)
            ai_summary = ollama.invoke(
                f"summarise the following in regards to: {query}\n\n{markdown_content}"
            )

            return ai_summary, url

        except Exception:
            print("Error processing article:", url)
            return None, None
        
    summaries = []
    urls_visited_list = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_news = {
            executor.submit(process_single_article, dic): dic
            for dic in news_results
        }

        # tqdm over completed futures
        for future in tqdm(as_completed(future_to_news), total=len(news_results), desc="Reading news articles"):
            result, url = future.result()

            if result:
                summaries.append(result)
            if url:
                urls_visited_list.append(url)

    # Collate thread results
    ai_summary_collation = "\n".join(summaries)
    links_visited = "\n".join(urls_visited_list)


    prompt = f"""
        You are a senior financial analyst with expertise in equity research, market trends, and investment risk assessment.
        Your style is professional, concise, and optimised for a non-expert investor.

        TASK:
        1. Read the provided information about the stock: {query}.
        2. Summarise the key points in a short, clear paragraph.
        3. Provide a verdict (positive / negative / neutral) and briefly justify it.

        INFORMATION TO ANALYSE:
        {ai_summary_collation}
        """

    final_summary = ollama.invoke(prompt)
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
