import pandas as pd
import asyncio 
from main import get_client
from user import User
from datetime import datetime
import cv2
import numpy as np
import urllib.request
from fuzzywuzzy import fuzz

FIELDS = ['user_id', 'is_bot', 'account_age', 'is_blue_verified', 'is_verified', 'profile_description', 'follwing_count', 'followers_count', 'following_to_followers_ratio', 'fast_followers_count', 'normal_followers_count', 'fast_to_normal_followers_ratio', 'tweets_count', 'retweets_count', 'freq_of_tweets', 'identical_tweets_count', 'tweets_to_reply_ratio', 'possibly_sensitive', 'profile_image_url', 'profile_banner_url', 'is_profile_image_valid', 'followers_to_engagement_ratio', 'followers_to_likes_ratio']

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
            if counter == 10: break
            user_id = row['id']
            label = row['label']
            if not user_id or not label: continue
            await add_to_dataset(user_id[1:], label, client, dataset)
            counter += 1
    
    dataset.to_csv('test_dataset.csv', index=False)
        

async def add_to_dataset(user_id: str, label: str, client, dataset: pd.DataFrame): 
    try:
        user = await client.get_user_by_id(user_id)
        if not user: 
            print(f"User with ID {user_id} not found.")
            return
        row = parse_user(user, label)
        dataset.loc[len(dataset)] = row

    except Exception as e:
        print(f"Error fetching user with ID {user_id}: {e}")
        return

# preprocesses user data to be used in the dataset
async def parse_user(user: User, label):
    age = get_age(user.created_at)
    retweets, num_tweets_parsed, likes, replies, reply_tweets, urls, identical_tweets_count = 0, 0, 0, 0, 0, 0, 0

    # analyze profile picture with openCV
    is_profile_image_valid = analyze_profile_image(user.profile_image_url)
    
    # get user tweets (up to 250)
    tweets = await user.get_tweets(count=250)

    tweets_analyzed = []
    
    for tweet in tweets:
        num_tweets_parsed += 1
        if tweet.in_reply_to: reply_tweets += 1
        if tweet.retweeted_tweet: retweets += 1
        likes += tweet.favorite_count
        views += tweet.view_count
        replies += tweet.reply_count
        urls += len(tweet.urls)
        is_identical = analyze_tweet_similarity(tweet.text, tweets_analyzed)
        if is_identical: identical_tweets_count += 1
        

    return {
        'user_id': user.id,
        'is_bot': 1 if label == 'bot' else 0,
        'account_age': age,
        'is_blue_verified': 1 if user.is_blue_verified else 0,
        'is_verified': 1 if user.verified else 0,
        'profile_description': user.description,
        'follwing_count': user.following_count,
        'followers_count': user.followers_count,
        'following_to_followers_ratio': user.following_count / user.followers_count,
        'fast_followers_count': user.fast_followers_count,
        'normal_followers_count': user.normal_followers_count,
        'fast_to_normal_followers_ratio': user.fast_followers_count / user.normal_followers_count,
        'tweets_count': user.statuses_count,
        'replies_ratio': reply_tweets / num_tweets_parsed,
        'retweets_ratio': retweets / num_tweets_parsed,
        'freq_of_tweets': round(user.statuses_count / age, 4), # tweets per year
        'identical_tweets_count_ratio': identical_tweets_count / num_tweets_parsed, 
        'replies_to_tweet_ratio': replies / num_tweets_parsed,
        'urls_to_tweet_ratio': urls / num_tweets_parsed,
        'possibly_sensitive': 1 if user.possibly_sensitive else 0,
        'profile_image_url': user.profile_image_url,
        'profile_banner_url': user.profile_banner_url,
        'is_profile_image_valid': 1 if is_profile_image_valid else 0,
        'followers_to_views_ratio': user.followers_count / (views / num_tweets_parsed) , # followers to views ratio for
        'followers_to_likes_ratio': user.followers_count / (likes / num_tweets_parsed) # followers to likes ratio for 
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
    if not image: return 0

    gray_scale_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray_scale_img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    is_face_detected = len(faces) > 0

    resolution = image.shape[:2] # (height, width)
    is_high_quality = False if resolution[0] < 100 or resolution[1] < 100 else True

    return 1 if is_face_detected or is_high_quality else 0
    
def load_image(url: str):
    resp = urllib.request.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image

def analyze_tweet_similarity(tweet_text: str, tweets_analyzed: list, similarity_score=95):
    if not tweet_text: return False
    tweets_analyzed.append(tweet_text)

    is_identical = False

    for tweet in tweets_analyzed:
        similarity_score = fuzz.ratio(tweet_text, tweet)
        if similarity_score >= similarity_score: 
            is_identical = True
            break
    
    return is_identical

asyncio.run(create_dataset())






