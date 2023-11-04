# import json
# import urllib.request
import pprint
from newsapi import NewsApiClient
import text_analysis as ta
from nltk.sentiment.vader import SentimentIntensityAnalyzer

news_api_key = "04b295bbbd4240bfa8672f81bbadac5d"
q = "Apple"
pageSize = 10
url = (
    f"https://newsapi.org/v2/everything?q={q}&pagesize={pageSize}&apiKey={news_api_key}"
)

# def open_news(url):
#     with urllib.request.urlopen(url) as f:
#         file_content = f.read().decode('utf-8')
#         file_data = json.loads(file_content)
#         return file_data


def open_news_alt(query):
    """
    Uses python client library to pull top headline/general search data on news
    """
    newsapi = NewsApiClient(api_key="04b295bbbd4240bfa8672f81bbadac5d")

    # top_headlines = newsapi.get_top_headlines(
    #     q=query,
    #     country="us",
    #     # category="business",
    #     # sources="",
    #     # pageSize=20,
    #     # page="",
    # )

    # /v2/everything
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
    for article in all_articles['articles']:
        article['text_to_analyze'] = article['title']+ " " +article['content'] + article['description']

    return all_articles

def analyze_articles(all_articles: dict):
    for article in all_articles['articles']:
        article['sentiment'] = SentimentIntensityAnalyzer().polarity_scores(article['text_to_analyze'])
        article['sum_stats'] = ta.compute_summary_stats(ta.create_histogram(data=article["text_to_analyze"], remove_stop=True))
    return all_articles
    
def main():
    query = input("Input news query: ")
    # data = open_news(url=url)
    all_articles = open_news_alt(query=query)
    analyze_articles(all_articles)
    pprint.pprint(all_articles)
    articles_by_sentiment = sorted(all_articles["articles"], key = lambda x: x["sentiment"], reverse=True)
    
    n = 3
    for top_and_bottom_n in articles_by_sentiment[-n:n-1]:
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