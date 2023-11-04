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
    Remove punctuation from text data and count each unique word
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
    print("Stop words removed: ", stop_word_count)
    return hist

def compute_summary_stats(hist: dict, n = 10):
    """
    return summary statistics of text data
    """
  
    count = sum(hist.values())
    unique_count = len(hist.items())
    top_n = sorted(hist.items(), key = lambda x: x[1], reverse=True)[:n-1]
    characters = 0
    for word in hist.keys():
        characters += len(word)
    word_density = characters/count
    sentiment = SentimentIntensityAnalyzer().polarity_scores(article['text_to_analyze'])

    return count, unique_count, top_n, characters, sentiment
    # print("Total word count: ", count)
    # print("Unique count: ", unique_count)
    # print(f"Word density: {word_density:.2f}")
    # print("10 most frequent: ")
    # for word, count in top_n:
    #     print(f"{word}: {count}")

    

def main():
    all_data = {
    "author": "Kris Holt",
    "content": "Goldman Sachs, Apple's banking partner for its credit card and high-yield savings account, is seemingly having doubts about those products. According to The Wall Street Journal, Goldman is looking to… [+2148 chars]'",
    "description": "Goldman Sachs, Apple's banking partner for its credit card and high-yield savings account, isseemingly having doubts about those products. According to The Wall Street Journal, Goldman is looking to get out of the consumer lending business, which could have …",
    "publishedAt": "2023-10-16T20:40:14Z",
    "source": {"id": "engadget", "name": "Engadget"},
    "title": "Goldman Sachs might be trying to offload Apple's credit card and savings accounts",
    "url": "https://www.engadget.com/goldman-sachs-might-be-trying-to-offload-apples-credit-card-and-savings-accounts-204014759.html",
    "urlToImage": "https://s.yimg.com/ny/api/res/1.2/NsD3DTcwSckP79ST_JAA2Q--/YXBwaWQ9aGlnaGxhbmRlcjt3PTEyMDA7aD04MDA-/https://s.yimg.com/os/creatr-images/2019-03/28edea50-5005-11e9-8cff-3ae401badce9",
}
    data = all_data.get("description", 0)
    compute_summary_stats(create_histogram(data, remove_stop=True))
    # pprint.pprint(hist)



if __name__ == "__main__":
    main()
