# import json
# import urllib.request
import pprint
from newsapi import NewsApiClient
import text_analysis as ta


def get_news_data(query):
    """
    Uses python client library to pull top headline/general search data on news
    """
    newsapi = NewsApiClient(api_key="04b295bbbd4240bfa8672f81bbadac5d")

    all_articles = newsapi.get_everything(
        q=query,
        # searchIn="content",  # title/description/content
        # sources="us",
        # # domains=,
        # exclude_domains=,
        # from=,
        # to=,
        language="en",
        sort_by="popularity",
        # pagesize=20,
    )
    # combines relevant text for analysis
    for article in all_articles["articles"]:
        article["text_data"] = (
            article["title"] + " " + article["content"] + article["description"]
        )

    return all_articles


def analyze_articles(all_articles: dict):
    for article in all_articles["articles"]:
        article["sum_stats"] = ta.compute_summary_stats(
            ta.create_histogram(data=article["text_data"], remove_stop=True)
        )
    return all_articles



def main():
    query = input("Input news query: ")
    all_articles = get_news_data(query=query)

    for article in all_articles["articles"]:
        ta.explore_text(article)

    articles_by_sentiment = sorted(
        all_articles["articles"], key=lambda x: x["sentiment"], reverse=True
    )

    n = 3
    for top_and_bottom_n in articles_by_sentiment[-n : n - 1]:
        pprint.pprint(top_and_bottom_n)


if __name__ == "__main__":
    main()


"""
for each news article
combine title, content, and description as one large text data

run sentiment analysis
works better for news sites where the sentiment of the text, based on other real people is more relevant than in books/wiki articles.
Plus the character limit make it so that computing word frequencies for analysis is less relevant on an individual article basis, and a search
query term would be over represented in the resulting ranked word counts
"""
