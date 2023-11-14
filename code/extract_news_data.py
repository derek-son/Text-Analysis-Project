from math import ceil
from newsapi import NewsApiClient
from text_analysis import compile_stats, create_sentiment_score
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from os import path, makedirs
import csv





def get_num_pages(query, news_api):
    """
    Returns total number of result pages to iterate through
    """
    news_data = news_api.get_everything(
        q=query,
        language="en",
        sort_by="popularity",
    )

    result_pages = ceil(news_data["totalResults"] / 100)

    return result_pages


def get_news_data(news_api, query: str, result_pages: int):
    """
    Uses python client library to pull top headline/general search data on news
    Can only do analysis on 1 page (100 results) due to paywall limitations
    """
    # for page in range(1, result_pages+1):
    for page in range(1, 2): # Cannot page through all results without paying more
        data = news_api.get_everything(
            q=query,
            # searchIn="content",  # title/description/content
            # sources="us",
            # domains= "cnn.com, nytimes.com, foxnews.com, washingtonpost.com, cbs.com, nbc.com, businessinsider.com, npr.org, wired.com, bbc.com, reuters.com, apnews.com",
            # exclude_domains=,
            # from=,
            # to=,
            language="en",
            sort_by="popularity",
            page=page,
        )
        if page == 1:
            news_data = data["articles"]
        else:
            news_data.extend(data["articles"])


    # Clean article text of noise before combining
    for article in news_data:
        article['content'] = article['content'].replace(' chars]', '')
        article['content'] = article['content'].replace('<ul><li>', '')
        article['content'] = article['content'].replace('</li><li>', '')
        article["text_data"] = " ".join(
            (article["title"], article["content"], article["description"])
        )
    return news_data


def create_query_directory(query):
    """
    Creates directory for query outputs for more accessibility
    """
    base_path = f"C:/Users/dson1/Documents/GitHub/Text-Analysis-Project/output"
    new_path = path.join(base_path, query)
    if not path.isdir(new_path):
        makedirs(new_path)
    return new_path

def generate_text_data_figures(query: str, news_data: list, n: int, file_path: str):
    """
    Generate histogram of top n words & wordcloud of text data of news query in output folder
    """
    all_text_data = ". ".join(article['text_data'] for article in news_data)
    
    # create & display histogram:
    sum_stats = compile_stats(all_text_data, n=n)
    words = [item[0] for item in sum_stats["sum_stats"]["top_n"]]
    counts = [item[1] for item in sum_stats["sum_stats"]["top_n"]]

    plt.bar(words, counts, color="blue")
    plt.xlabel("Words")
    plt.ylabel("Count")
    plt.title(f"Top {n} Word Counts")
    plt.savefig(path.join(file_path, f'{query}_histogram.png'))
    plt.show()


    # create & display wordcloud:
    wordcloud = WordCloud(max_font_size=40).generate(all_text_data)
    
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(path.join(file_path, f'{query}_wordcloud.png'))
    plt.show()
    return


def track_and_rank_sources(news_data: list):
    """
    creates a list of all sources returned by API sorted based on avgerage article sentiment
    """
    sources = {}
    for article in news_data:
        news_org = article["source"]["name"]
        article['sentiments'] = create_sentiment_score(article["text_data"])
        sentiment = article["sentiments"]["compound"]

        if news_org not in sources:
            sources[news_org] = {"count": 0, "avg_sentiment": 0}

        sources[news_org]["count"] += 1
        sources[news_org]["avg_sentiment"] += sentiment

    for news_org in sources:
        sources[news_org]["avg_sentiment"] /= sources[news_org]["count"]

    sorted_sources = sorted(
        sources.items(), key=lambda x: x[1]["avg_sentiment"], reverse=True
    )
    print(sorted_sources)
    return sorted_sources


def save_news_data_as_csv(news_data, csv_filename):
    """
    Save the news data to a CSV file using keys as headers
    """
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "source",
            "text_data",
            "sentiment",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for article in news_data:
            source = article["source"]["name"]
            text_data = article.get("text_data", "")
            sentiment = (
                article.get("stats", {}).get("sentiments", {}).get("compound", 0)
            )

            writer.writerow(
                {
                    "source": source,
                    "text_data": text_data,
                    "sentiment": sentiment,
                }
            )


def save_sources_as_csv(sorted_sources, csv_filename):
    """
    Save the sources ranked by sentiment to a CSV file. Made with ChatGPT
    """
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["source", "count", "avg_sentiment"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for source, data in sorted_sources:
            writer.writerow(
                {
                    "source": source,
                    "count": data["count"],
                    "avg_sentiment": data["avg_sentiment"],
                }
            )


def main():
    query = input("Input news query: ")
    news_api = NewsApiClient(api_key="04b295bbbd4240bfa8672f81bbadac5d")
    
    news_data = get_news_data(query=query, news_api=news_api, result_pages=get_num_pages(query=query, news_api=news_api))
    base_path = create_query_directory(query=query)
    generate_text_data_figures(news_data=news_data, n=12, query=query, file_path=base_path)

    # Sort sources by sentiment
    sorted_sources = track_and_rank_sources(news_data)
    print("Sources by sentiment: ", sorted_sources)

    # Creates CSV of sources ranked by average sentiment of query
    query = query.strip('"')
    sources_csv = path.join(base_path, f"sources_data_{query.replace(' ', '_')}.csv")
    save_sources_as_csv(sorted_sources, sources_csv)
    print(f"Sources data saved as {sources_csv}.")

    # Saves a csv copy of news data in case of need for future reference
    news_data_csv = path.join(base_path, f"news_data_{query.replace(' ', '_')}.csv")
    save_news_data_as_csv(news_data, news_data_csv)
    print(f"News data saved as {news_data_csv}.")


if __name__ == "__main__":
    main()
