
from dotenv import load_dotenv 
import os
from twikit import Client
from user import User
from datetime import datetime
import cv2
import numpy as np
import urllib.request
from fuzzywuzzy import fuzz

# returns a Twikit client
def get_client():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    envars = os.path.join(dir_path, '.env')
    load_dotenv(envars)

    client = Client('en-US')
    client.load_cookies('cookies.json')
    return client

# returns the age in number of days
def get_age(created_at: str):
    date = datetime.strptime(created_at, '%a %b %d %H:%M:%S %z %Y')
    now = datetime.now(date.tzinfo)
    delta = now - date
    age_in_days = delta.days
    return age_in_days

# returns 1 if the profile image is valid, 0 otherwise
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
    
# loads an image from a URL
def load_image(url: str):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    request = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(request)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image

# returns the number of identical tweet pairs and the total number of pairs
def analyze_tweets_similarity(tweets: list, similarity_score_test_mark=95):
    identical_tweet_pairs, num_pairs = 0, 0
    tweets_analyzed = set()

    for tweet in tweets:
        if not tweet.text: continue # skip tweets without text
        normalized_tweet = tweet.text.lower().strip()
        # check for fuzzy matches
        for other_tweet in tweets_analyzed:
            num_pairs += 1
            similarity_score = fuzz.ratio(normalized_tweet, other_tweet)
            if similarity_score >= similarity_score_test_mark: 
                identical_tweet_pairs += 1
        tweets_analyzed.add(normalized_tweet)

    return identical_tweet_pairs, num_pairs

# returns the sentiment score of a text from -1 to 1
def get_sentiment_score(text: str, sentiment_analyzer):

    result = sentiment_analyzer(text)
    label_scores = {res['label']: res['score'] for res in result}

    # map the labels to weights: LABEL_0 -> -1, LABEL_1 -> 0, LABEL_2 -> +1
    weights = {'LABEL_0': -1, 'LABEL_1': 0, 'LABEL_2': 1}

    return sum(weights[label] * score for label, score in label_scores.items()) # score between -1 and 1 - negative, neutral, positive

features_dict = {
    'account_age': 'Account Age',
    'is_blue_verified': 'Blue Verification Status',
    'profile_description_sentiment': 'Profile Description Sentiment',
    'following_count': 'Following Count',
    'followers_count': 'Followers Count',
    'following_to_followers': 'Following to Followers Ratio',
    'is_possibly_sensitive': 'Possibly Sensitive Content',
    'is_default_profile_image': 'Default Profile Image',
    'is_profile_banner': 'Profile Banner',
    'is_profile_image_valid': 'Profile Image Validity',
    'tweet_freq': 'Tweet Frequency',
    'likes_freq': 'Likes Frequency',
    'media_freq': 'Posted Video or Photo Frequency',
    'followers_freq': 'Followers Gained Per Day',
    'following_freq': 'Accounts Followed Per Day',
    'replies_to_owned': 'Replies to Owned Tweets Ratio',
    'quotes_to_owned': 'Quotes to Owned Tweets Ratio',
    'retweets_to_owned': 'Retweets to Owned Tweets Ratio',
    'avg_urls': 'Average URLs Per Tweet',
    'avg_hashtags': 'Average Hashtags Per Tweet',
    'identical_tweet_freq': 'Identical Tweet Frequency',
    'avg_tweet_sentiment': 'Average Tweet Sentiment',
    'avg_replies_per_follower': 'Average Replies On a Tweet Per 1,000 Followers',
    'avg_likes_per_follower': 'Average Likes On a Tweet Per 1,000 Followers',
    'avg_retweets_per_follower': 'Average Retweets On a Tweet Per 1,000 Followers'
}
