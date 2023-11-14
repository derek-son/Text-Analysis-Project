import pprint
import sys
from unicodedata import category
from nltk.sentiment.vader import SentimentIntensityAnalyzer


def remove_stop_words(words: str):
    """
    Removes words that do not provide insights
    """
    with open("data/stopwords.txt") as f:
        stop_words = []
        for line in f:
            stop_word = line.strip().lower()
            stop_words.append(stop_word)
        return stop_words


def create_histogram(data: str, remove_stop: bool):
    """
    Removes punctuation from text data and returns histogram of unique words
    """
    hist = {}
    strippables = "".join(
        [chr(i) for i in range(sys.maxunicode) if category(chr(i)).startswith("P")]
    )
    data = data.split(" ")
    stop_words = remove_stop_words(words=data)
    stop_word_count = 0

    for word in data:
        word = word.strip(strippables).lower()
        if remove_stop:
            try:
                stop_words.index(word)
                stop_word_count += 1
            except ValueError:
                hist[word] = hist.get(word, 0) + 1
        else:
            hist[word] = hist.get(word, 0) + 1
    del hist['']
    return hist, stop_word_count


def create_sentiment_score(text: str):
    """
    Return sentiment score (positive/neutral/negative) of analyzed text
    """
    sentiment = SentimentIntensityAnalyzer().polarity_scores(text)
    return sentiment


def sort_by_sentiment(data: dict, sort_by: str):
    """
    returns avg sentiment of all text data and text data entry by sorted by specified positive/neutral/negative score
    """
    entry_by_sentiment = sorted(
        data, key=lambda x: x["sentiment"][sort_by], reverse=True
    )

    sentiments = []
    for sentiment in data["sentiment"][sort_by]:
        sentiments.append(sentiment)
        avg_sentiment = sum(sentiments) / len(sentiments)

    n = 3
    for top_and_bottom_n in data[-n : n - 1]:
        print(f"Rank:", n)
        pprint.pprint(top_and_bottom_n)
    return avg_sentiment, entry_by_sentiment


def compute_summary_stats(hist: dict, stop_word_count: int, n: int):
    """
    return summary statistics of text data
    """
    sum_stats = {}
    sum_stats["count"] = sum(hist.values())
    sum_stats["unique_count"] = len(hist.items())
    sum_stats["stop_words_removed"] = stop_word_count
    sum_stats["top_n"] = sorted(hist.items(), key=lambda x: x[1], reverse=True)[: n - 1]
    characters = 0
    for word in hist.keys():
        characters += len(word)
    sum_stats["word_density"] = round(characters / sum_stats["count"], ndigits=3)

    return sum_stats


def compile_stats(text: str, n: int):
    """
    Analyzes text and returns top n word count histogram and sentiments
    """
    all_stats = {}
    hist, stop_word_count = create_histogram(text, remove_stop=True)
    all_stats["sum_stats"] = compute_summary_stats(
        hist=hist, stop_word_count=stop_word_count, n=n
    )
    all_stats["sentiments"] = create_sentiment_score(text)
    return all_stats


def create_navigation_params(data: dict):
    """
    returns menu used to navigate in and out of each data entry
    """
    output = {}
    ids = []
    for key, value in data.items():
        output[key.lower()] = compile_stats(value)
        ids.append(key.lower())

    return ids, output


def explore_text(ids, output):
    """
    Displays menu ids to and accepts user input to navigate data
    """
    print(f"Text data entries:\n", ids)
    while True:
        user_input = input(
            "\nEnter id of text data entry to see its associated stats (Type 'STOP!' to stop program): "
        ).lower()
        if user_input == "STOP!":
            break
        else:
            pprint.pprint(output[user_input])


if __name__ == "__main__":
    text_entries = {
        "author": "Kris Holt",
        "content": "Goldman Sachs, Apple's banking partner for its credit card and high-yield savings account, is seemingly having doubts about those products. According to The Wall Street Journal, Goldman is looking to… [+2148 chars]'",
        "description": "Goldman Sachs, Apple's banking partner for its credit card and high-yield savings account, isseemingly having doubts about those products. According to The Wall Street Journal, Goldman is looking to get out of the consumer lending business, which could have …",
        "title": "Goldman Sachs might be trying to offload Apple's credit card and savings accounts",
    }
    explore_text(*create_navigation_params(text_entries))
