# pip install praw pandas requests

import pandas as pd

def load_tickers():
    nasdaq = pd.read_csv("nasdaq_.csv")
    nyse = pd.read_csv("nyse.csv")

    # Make sure the column name is correct; use 'Symbol' or 'ACT Symbol'
    if 'Symbol' in nasdaq.columns:
        nasdaq_tickers = set(nasdaq['Symbol'].str.upper())
    else:
        nasdaq_tickers = set(nasdaq['ACT Symbol'].str.upper())

    if 'Symbol' in nyse.columns:
        nyse_tickers = set(nyse['Symbol'].str.upper())
    else:
        nyse_tickers = set(nyse['ACT Symbol'].str.upper())

    all_tickers = nasdaq_tickers.union(nyse_tickers)
    return all_tickers

# Load and print count
valid_tickers = load_tickers()
print(f"Loaded {len(valid_tickers)} valid tickers.")

import praw
import re
from collections import Counter
import time

reddit = praw.Reddit(
    client_id="Lk7amzjYlHw4NZN4jVeMOA",
    client_secret="4Xv7mFZcXHbcvUkQG98tMau-BvEFFg",
    user_agent="WSB_Sentiment_Bot/1.0 by Defiant-Fee-533",
    check_for_async=False
)

subreddits = ['wallstreetbets', 'stocks', 'investing']
post_limit = 200  # number of posts to scan per subreddit

# Regex to extract uppercase words 1-5 letters (possible ticker symbols)
ticker_candidate_pattern = re.compile(r'\b[A-Z]{1,5}\b')

def find_trending_tickers():
    all_candidates = []

    for subreddit_name in subreddits:
        print(f"Scanning r/{subreddit_name}...")
        subreddit = reddit.subreddit(subreddit_name)
        for post in subreddit.hot(limit=post_limit):
            text = post.title.upper()
            candidates = ticker_candidate_pattern.findall(text)
            all_candidates.extend(candidates)
            time.sleep(0.1)  # polite pause to avoid rate limit

    # Filter candidates by whether they are valid tickers
    filtered = [t for t in all_candidates if t in valid_tickers]

    # Count frequencies and get top 20 trending tickers
    counter = Counter(filtered)
    top_20 = counter.most_common(20)

    print("\nTop 20 trending tickers detected on Reddit:")
    for ticker, count in top_20:
        print(f"{ticker}: {count} mentions")

    return [t[0] for t in top_20]

def get_posts_for_ticker(ticker, max_posts=15):
    posts = []
    query = f'title:{ticker} OR selftext:{ticker}'

    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)
        for post in subreddit.search(query, sort='new', limit=max_posts):
            posts.append({
                'ticker': ticker,
                'post_id': post.id,
                'title': post.title,
                'selftext': post.selftext,
                'url': post.url,
                'created_utc': post.created_utc,
                'score': post.score,
                'num_comments': post.num_comments,
                'subreddit': subreddit_name
            })
            if len(posts) >= max_posts:
                break
        if len(posts) >= max_posts:
            break
    return posts

if __name__ == "__main__":
    valid_tickers = load_tickers()
    trending_tickers = find_trending_tickers()

    all_posts = []
    for ticker in trending_tickers:
        print(f"\nFetching posts for {ticker}...")
        posts = get_posts_for_ticker(ticker)
        all_posts.extend(posts)
        print(f"Fetched {len(posts)} posts for {ticker}")
        time.sleep(1)
    # Convert the list of posts to a DataFrame
    df = pd.DataFrame(all_posts)
    # Save the DataFrame to a CSV file
    output_file = "reddit_trending_tickers_posts.csv"
    df.to_csv(output_file, index=False)
    print(f"\nSaved extracted data to '{output_file}'")

# pip install yfinance

import yfinance as yf
import pandas as pd

def get_sp500_tickers():
    # Fetch S&P 500 tickers
    sp500 = yf.Ticker("^GSPC")

    # yfinance does not have a direct method for tickers list,
    # but there's a popular workaround to get the list via Wikipedia
    sp500_table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    sp500_df = sp500_table[0]

    # Get the Symbol column as a list
    tickers = sp500_df['Symbol'].tolist()
    # Make uppercase for consistency
    tickers = [t.upper() for t in tickers]

    return tickers

# Example usage
valid_tickers = get_sp500_tickers()
print(valid_tickers[:10])  # print first 10 tickers

valid_tickers

import praw
import re
from collections import Counter
import time
import csv

# Reddit API setup
reddit = praw.Reddit(
    client_id="Lk7amzjYlHw4NZN4jVeMOA",
    client_secret="4Xv7mFZcXHbcvUkQG98tMau-BvEFFg",
    user_agent="WSB_Sentiment_Bot/1.0 by Defiant-Fee-533",
    check_for_async=False
)

subreddits = ['wallstreetbets', 'stocks', 'investing']
post_limit = 200  # number of posts to scan per subreddit

# Regex to extract uppercase ticker symbols, allowing optional dot (like BRK.B)
ticker_candidate_pattern = re.compile(r'\b[A-Z]{1,5}(?:\.[A-Z])?\b')


def find_trending_tickers():
    all_candidates = []

    for subreddit_name in subreddits:
        print(f"Scanning r/{subreddit_name}...")
        subreddit = reddit.subreddit(subreddit_name)
        for post in subreddit.hot(limit=post_limit):
            text = post.title.upper()
            candidates = ticker_candidate_pattern.findall(text)
            all_candidates.extend(candidates)
            time.sleep(0.1)  # polite pause to avoid rate limit

    # Filter candidates by whether they are valid tickers
    filtered = [t for t in all_candidates if t in valid_tickers]

    # Count frequencies and get top 20 trending tickers
    counter = Counter(filtered)
    top_20 = counter.most_common(20)

    print("\nTop 20 trending tickers detected on Reddit:")
    for ticker, count in top_20:
        print(f"{ticker}: {count} mentions")

    return [t[0] for t in top_20]

def get_posts_for_ticker(ticker, max_posts=15):
    posts = []
    query = f'title:{ticker} OR selftext:{ticker}'

    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)
        for post in subreddit.search(query, sort='new', limit=max_posts):
            posts.append({
                'ticker': ticker,
                'post_id': post.id,
                'title': post.title,
                'selftext': post.selftext,
                'url': post.url,
                'created_utc': post.created_utc,
                'score': post.score,
                'num_comments': post.num_comments,
                'subreddit': subreddit_name
            })
            if len(posts) >= max_posts:
                break
        if len(posts) >= max_posts:
            break
    return posts

def save_posts_to_csv(posts, filename='reddit_stock_posts.csv'):
    if not posts:
        print("No posts to save.")
        return

    keys = posts[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(posts)

    print(f"Saved {len(posts)} posts to {filename}")

if __name__ == "__main__":
    trending_tickers = find_trending_tickers()

    all_posts = []
    for ticker in trending_tickers:
        print(f"\nFetching posts for {ticker}...")
        posts = get_posts_for_ticker(ticker)
        all_posts.extend(posts)
        print(f"Fetched {len(posts)} posts for {ticker}")
        time.sleep(1)

    save_posts_to_csv(all_posts)

"""# Twitter Data extrection

"""

# pip install tweepy

"""bearer token = AAAAAAAAAAAAAAAAAAAAAGFZ1AEAAAAAx6XJqIZPEnWdIo7363qjxnKMJRw%3Dh6eozzD6VSNZrQtsMjORlNNTbifqLbPkcn3kI947DxDwhKwSrA


"""

import tweepy
import time
import pandas as pd
import csv
import os

# === Twitter API credentials ===
API_KEY = 'ZsxpTSFXfDH2L31F7qvIDKJD6'
API_SECRET = 'BVPWkgfCW3Fk7hltibqlzl1Q6H0yEYcjd2pQ5Bo7Av7PwipEoh'
ACCESS_TOKEN = '1884820631235284992-MkKo0o6XYZjs1ACtSo0yVfeKOsctkF'
ACCESS_TOKEN_SECRET = 'hOPjcxDvElqf0ORtzxiurlcVKxa6IYY1yhrJlB5TOZ4Ik'

# === Set up Tweepy with OAuth 1.0a ===
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

# === Your custom ticker list (from 13F / Congressional data) ===
custom_tickers = ['NVDA', 'AAPL', 'MSFT']  # Replace with your actual list

# === Count mentions for a single ticker ===
def count_ticker_mentions(ticker, max_tweets=50):
    query = f"{ticker} -filter:retweets"
    count = 0
    try:
        for tweet in tweepy.Cursor(api.search_tweets, q=query, lang="en", tweet_mode="extended").items(max_tweets):
            text = tweet.full_text.upper()
            if ticker in text:
                count += 1
            time.sleep(0.1)
    except Exception as e:
        print(f"Error fetching tweets for {ticker}: {e}")
    return count

# === Get top trending tickers from your custom list ===
def get_top_trending_tickers(ticker_list, max_tweets=50, top_n=10):
    ticker_counts = {}
    for i, ticker in enumerate(ticker_list):
        print(f"[{i+1}/{len(ticker_list)}] Checking mentions for {ticker}")
        count = count_ticker_mentions(ticker, max_tweets=max_tweets)
        ticker_counts[ticker] = count
        time.sleep(1)
    sorted_tickers = sorted(ticker_counts.items(), key=lambda x: x[1], reverse=True)
    top_tickers = [ticker for ticker, count in sorted_tickers[:top_n] if count > 0]
    print("\nTop trending tickers:")
    for t, c in sorted_tickers[:top_n]:
        print(f"{t}: {c} mentions")
    return top_tickers

# === Fetch tweets and save to CSV ===
def fetch_tweets_for_ticker(ticker, max_results=30):
    query = f"{ticker} -filter:retweets"
    tweets = []
    try:
        for tweet in tweepy.Cursor(api.search_tweets, q=query, lang="en", tweet_mode="extended").items(max_results):
            tweets.append({
                'ticker': ticker,
                'created_at': tweet.created_at,
                'text': tweet.full_text,
                'author_id': tweet.user.id_str,
                'username': tweet.user.screen_name
            })
            time.sleep(0.1)
    except Exception as e:
        print(f"Error fetching tweets for {ticker}: {e}")
    return tweets

# === Main execution ===
if __name__ == "__main__":
    print("Using custom ticker list...")
    top_tickers = get_top_trending_tickers(custom_tickers, max_tweets=50, top_n=len(custom_tickers))

    all_tweets = []
    print("\nFetching tweets for top tickers...")
    for i, ticker in enumerate(top_tickers):
        print(f"[{i+1}/{len(top_tickers)}] Fetching tweets for {ticker}")
        tweets = fetch_tweets_for_ticker(ticker, max_results=30)
        all_tweets.extend(tweets)

    # Save to CSV
    df = pd.DataFrame(all_tweets)
    df.to_csv("custom_ticker_tweets.csv", index=False)
    print("\n✅ Tweets saved to custom_ticker_tweets.csv")

import requests
import time
import pandas as pd

# Replace with your Bearer Token
BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAGFZ1AEAAAAAL8bD8zRNUbjNiWLS%2FtU1Ep%2Ft4JI%3DBe629d62CSC9G4HD53zDE6OTGHr9RanAS886TRgP0J4vU92G3B'

headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

# === Your custom ticker list ===
custom_tickers = ['NVDA', 'AAPL', 'MSFT']

def search_recent_tweets(ticker, max_results=10):
    query = f"{ticker} -is:retweet lang:en"
    url = f"https://api.twitter.com/2/tweets/search/recent?query={query}&max_results={max_results}&tweet.fields=created_at,author_id"

    for attempt in range(3):  # retry logic
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            tweets = response.json().get("data", [])
            return [{
                'ticker': ticker,
                'created_at': t['created_at'],
                'text': t['text'],
                'author_id': t['author_id']
            } for t in tweets]

        elif response.status_code == 429:
            wait_time = 60  # seconds
            print(f"Rate limit hit for {ticker}. Waiting {wait_time} seconds before retrying...")
            time.sleep(wait_time)
        else:
            print(f"Error fetching tweets for {ticker}: {response.status_code} - {response.text}")
            return []

    print(f"Failed to fetch tweets for {ticker} after retries.")
    return []

# === Main ===
all_tweets = []

for ticker in custom_tickers:
    print(f"Fetching tweets for {ticker}...")
    tweets = search_recent_tweets(ticker, max_results=10)
    all_tweets.extend(tweets)
    time.sleep(5)  # Wait between requests to avoid 429

# Save to CSV
df = pd.DataFrame(all_tweets)
df.to_csv("custom_ticker_tweets_v2.csv", index=False)
print("\n✅ Tweets saved to custom_ticker_tweets_v2.csv")

"""# Merging NASDAQ, NYSE, S&P 500 into all stocks

"""

import pandas as pd

# Load each dataset
nasdaq_df = pd.read_csv("nasdaq_.csv")
nyse_df = pd.read_csv("nyse.csv")
sp500_df = pd.read_csv("s&P500.csv")

# Standardize column names
nasdaq_df = nasdaq_df.rename(columns={"Symbol": "Symbol", "Security Name": "Company Name"})
nyse_df = nyse_df.rename(columns={"ACT Symbol": "Symbol", "Company Name": "Company Name"})
sp500_df = sp500_df.rename(columns={"Symbol": "Symbol", "Security": "Company Name"})

# Add exchange label
nasdaq_df["Exchange"] = "NASDAQ"
nyse_df["Exchange"] = "NYSE"
sp500_df["Exchange"] = "S&P 500"

# Select common columns
nasdaq_df = nasdaq_df[["Symbol", "Company Name", "Exchange"]]
nyse_df = nyse_df[["Symbol", "Company Name", "Exchange"]]
sp500_df = sp500_df[["Symbol", "Company Name", "Exchange"]]

# Combine all into one DataFrame
all_stocks_df = pd.concat([nasdaq_df, nyse_df, sp500_df], ignore_index=True)

# Drop duplicate tickers (some overlap between indices)
all_stocks_df = all_stocks_df.drop_duplicates(subset="Symbol", keep="first")

# Save to CSV
all_stocks_df.to_csv("all_stocks.csv", index=False)

print("✅ Merged file saved as 'all_stocks.csv'")

duplicate_rows = all_stocks_df[all_stocks_df.duplicated()]
print(f"\n🧾 Duplicate rows: {len(duplicate_rows)}")

df_cleaned = all_stocks_df.dropna(subset=["Symbol", "Company Name"])

df_cleaned.to_csv("all_stocks_cleaned.csv")

"""## Normalizing the all stocks data

"""

import pandas as pd
import re

# Load your CSV
df = pd.read_csv("all_stocks_cleaned.csv")

# Define a cleaning function
def clean_company_name(name):
    name = name.upper().strip()  # Uppercase + trim
    # Remove common suffixes using regex
    name = re.sub(r"\b(INC|INC\.|CORP|CORPORATION|LTD|LLC|PLC|CO|CO\.)\b", "", name)
    name = re.sub(r"\s+", " ", name)  # Remove extra spaces
    return name.strip()

# Apply to "Company Name"
df["Cleaned Name"] = df["Company Name"].apply(clean_company_name)

# Save the result
df.to_csv("all_stocks_cleaned_normalized.csv", index=False)
print("✅ Saved: all_stocks_cleaned_normalized.csv with normalized company names.")

"""## AAdding the master fuzzy search

"""

import pandas as pd
from rapidfuzz import process, fuzz

# Load your master list with cleaned & normalized names
master_df = pd.read_csv("all_stocks_cleaned_normalized.csv")

# Assuming master_df has a column "Cleaned Name"
master_names = master_df["Cleaned Name"].tolist()

# Load your target list (e.g. from 13F/congressional data) also cleaned similarly
target_df = pd.read_csv("your_13f_or_congressional_data.csv")

# Make sure target names are cleaned & normalized similarly:
def clean_name(name):
    import re
    name = str(name).upper().strip()
    name = re.sub(r"\b(INC|INC\.|CORP|CORPORATION|LTD|LLC|PLC|CO|CO\.)\b", "", name)
    name = re.sub(r"\s+", " ", name)
    return name.strip()

target_df["Cleaned Name"] = target_df["Company Name"].apply(clean_name)

# Function to get best fuzzy match
def get_best_match(name, choices, scorer=fuzz.token_sort_ratio, score_cutoff=80):
    match = process.extractOne(name, choices, scorer=scorer, score_cutoff=score_cutoff)
    if match:
        return match  # (matched_name, score, index)
    else:
        return ("No Match", 0, None)

# Apply fuzzy matching
matches = []
for name in target_df["Cleaned Name"]:
    match = get_best_match(name, master_names)
    matches.append(match)

# Create DataFrame of matches
matches_df = pd.DataFrame(matches, columns=["Best Match", "Score", "Master Index"])

# Combine with original target data
result_df = pd.concat([target_df.reset_index(drop=True), matches_df], axis=1)

# Optional: Join back master stock data for matched rows
result_df = result_df.merge(master_df, left_on="Master Index", right_index=True, how="left", suffixes=('', '_Master'))

# Save results
result_df.to_csv("matched_13f_with_master.csv", index=False)
print("✅ Saved matched results to matched_13f_with_master.csv")