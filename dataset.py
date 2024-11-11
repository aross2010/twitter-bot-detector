import pandas as pd
import asyncio 
from main import get_client
from user import User
from datetime import datetime
import cv2
import numpy as np
import urllib.request
from fuzzywuzzy import fuzz

FIELDS = ["user_id", "screen_name", "is_bot", "account_age", "is_blue_verified", "is_verified", "profile_description", "follwing_count", "followers_count", "following_to_followers_ratio", "fast_followers_count", "normal_followers_count", "fast_to_normal_followers_ratio", "tweets_count", "parsed_tweets_count", "parsed_retweets_count", "replies_ratio", "retweets_ratio", "freq_of_tweets", "identical_tweets_ratio", "avg_replies_per_tweet", "avg_urls_per_tweet", "avg_likes_per_tweet", "possibly_sensitive", "profile_image_url", "profile_banner_url", "is_profile_image_valid", "followers_to_likes_ratio"]
TARGET_TWEETS = 100
NUM_USERS = 15

# Will parse data set and abstract key values to use for model training
async def create_dataset():

    csvs = ['./datasets/botmeter-2019-dataset.csv']
    dataset = pd.DataFrame(columns=FIELDS)
    client = get_client()

    for csv in csvs:
        df = pd.read_csv(csv)

        if 'id' not in df.columns or 'label' not in df.columns: continue

        counter = 0

        for _, row in df.iterrows():
            if counter == NUM_USERS: break
            user_id = row['id']
            label = row['label']
            if not user_id or not label: continue
            res = await add_to_dataset(user_id[1:], label, client, dataset)
            if res == "INVALID USER": continue
            counter += 1
            print(f"Added user {user_id} to dataset. Sleeping for 2 minutes...")
            await asyncio.sleep(120) # sleep for 60 seconds to avoid rate limiting
    
    dataset.to_csv('dataset.csv', index=False)

    print("Dataset created successfully.")
        

async def add_to_dataset(user_id: str, label: str, client, dataset: pd.DataFrame): 
    try:
        user = await client.get_user_by_id(user_id)
    except Exception as e:
        print(f"Error fetching user with ID {user_id}: {e}")
        return "INVALID USER"

    if not user: 
        print(f"User with ID {user_id} not found.")
        return "INVALID USER"
    
    row = await parse_user(user, label)
    dataset.loc[len(dataset)] = row

    return "SUCCESS"

# preprocesses user data to be used in the dataset
async def parse_user(user: User, label):
    age = get_age(user.created_at)
    num_tweets_parsed, num_retweets_parsed, num_tweet_pairs, likes,  replies, reply_tweets, urls, identical_tweets_count = 0, 0, 0, 0, 0, 0, 0, 0

    try:
        # analyze profile picture with openCV
        is_profile_image_valid = analyze_profile_image(user.profile_image_url)
    except Exception as e:
        print(f"Error analyzing profile image for user {user.id}: {e}")
        return
    
    tweets = []

    print(f"Fetching tweets for user {user.id}...")

    res = None

    try:
        # get user tweets (up to ~200)
        res = await user.get_tweets('Tweets', count=TARGET_TWEETS)
        while res and len(tweets) < TARGET_TWEETS:
            tweets += res
            print(f"Retrieved {len(tweets)} tweets for user {user.id}.")
            res = await res.next()
            # await asyncio.sleep(15) # sleep for 15 between pages to avoid rate limiting
    except Exception as e:
        if 'Rate limit exceeded' in str(e): 
            print(f"Rate limit exceeded for user {user.id}. Sleeping for 15 minutes...")
            await asyncio.sleep(901) # sleep for 15 minutes to reset rate limit
            while res and len(tweets) < 500:
                res = await res.next()
                if res: tweets += res
        else: 
            print(f"Error fetching tweets for user {user.id}: {e}")
            return


    tweets_analyzed = []
    print(f"Analyzing tweets for user {user.id} with {len(tweets)} tweets...")
    
    for tweet in tweets:
        if tweet.retweeted_tweet: 
            num_retweets_parsed += 1
            continue
        num_tweets_parsed += 1
        if tweet.in_reply_to: reply_tweets += 1
        likes += tweet.favorite_count
        replies += tweet.reply_count
        urls += len(tweet.urls)
        identical_tweets_count += analyze_tweet_similarity(tweet.text, tweets_analyzed, num_tweet_pairs)

    print(f"Finished analyzing tweets for user {user.id}.")

    return {
        'user_id': user.id,
        'screen_name': user.screen_name,
        'is_bot': 1 if label == 'bot' else 0,
        'account_age': age,
        'is_blue_verified': 1 if user.is_blue_verified else 0,
        'is_verified': 1 if user.verified else 0,
        'profile_description': user.description if user.description else '',
        'follwing_count': user.following_count,
        'followers_count': user.followers_count,
        'following_to_followers_ratio': user.following_count if user.followers_count == 0 else round(user.following_count / user.followers_count, 4),
        'fast_followers_count': user.fast_followers_count,
        'normal_followers_count': user.normal_followers_count,
        'fast_to_normal_followers_ratio': user.fast_followers_count if user.normal_followers_count == 0 else round(user.fast_followers_count / user.normal_followers_count, 4 ),
        'tweets_count': user.statuses_count,
        'parsed_tweets_count': num_tweets_parsed,
        'parsed_retweets_count': num_retweets_parsed,
        'replies_ratio': 0 if num_tweets_parsed == 0 else reply_tweets / num_tweets_parsed,
        'retweets_ratio': 0 if num_tweets_parsed == 0 else round(num_retweets_parsed / (num_tweets_parsed + num_retweets_parsed), 4),
        'freq_of_tweets': round(user.statuses_count / age, 4), # tweets per year
        'identical_tweets_ratio': 0 if num_tweet_pairs == 0 else round(identical_tweets_count / num_tweet_pairs,4), 
        'avg_replies_per_tweet': 0 if num_tweets_parsed == 0 else round(replies / num_tweets_parsed, 4),
        'avg_urls_per_tweet': 0 if num_tweets_parsed == 0 else round(urls / num_tweets_parsed, 4),
        'avg_likes_per_tweet': 0 if num_tweets_parsed == 0 else round(likes / num_tweets_parsed, 4),
        'possibly_sensitive': 1 if user.possibly_sensitive else 0,
        'profile_image_url': user.profile_image_url if user.profile_image_url else '',
        'profile_banner_url': user.profile_banner_url if user.profile_banner_url else '',
        'is_profile_image_valid': 1 if is_profile_image_valid else 0,
        'followers_to_likes_ratio': 0 if likes == 0 or num_tweets_parsed == 0 else round(user.followers_count / (likes / num_tweets_parsed), 4) # followers to likes ratio for 
    }

# returns the age in years to three decimal places
def get_age(created_at: str):
    date = datetime.strptime(created_at, '%a %b %d %H:%M:%S %z %Y')
    now = datetime.now(date.tzinfo)
    delta = now - date
    age = delta.days / 365.25
    return round(age, 3)

def analyze_profile_image(url: str):
    image = load_image(url)
    if image is None or not image.any(): return 0

    gray_scale_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray_scale_img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    is_face_detected = len(faces) > 0

    resolution = image.shape[:2] # (height, width)
    is_high_quality = False if resolution[0] < 100 or resolution[1] < 100 else True

    return 1 if is_face_detected or is_high_quality else 0
    
def load_image(url: str):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    request = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(request)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image

def analyze_tweet_similarity(tweet_text: str, tweets_analyzed: list, num_tweet_pairs: int, similarity_score_test_mark=95):
    if not tweet_text: return False

    identical_tweets_count = 0

    for tweet in tweets_analyzed:
        num_tweet_pairs += 1
        similarity_score = fuzz.ratio(tweet_text, tweet)
        if similarity_score >= similarity_score_test_mark: 
            identical_tweets_count += 1
            print(f"Similarity score: {similarity_score} for tweet: {tweet_text} and {tweet}")
    tweets_analyzed.append(tweet_text)
    
    return identical_tweets_count

asyncio.run(create_dataset())






