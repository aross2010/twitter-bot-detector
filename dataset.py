import pandas as pd
import asyncio 
from helpers import get_client
from user import User
from transformers import pipeline
import torch
from helpers import get_client, get_age, analyze_profile_image, load_image, analyze_tweets_similarity, get_sentiment_score

device = torch.device("cuda" if torch.cuda.is_available() else "cpu") # disregard this if you're running on mac

FIELDS = ["user_id", "screen_name", "is_bot", "account_age", "is_blue_verified", "is_verified", "profile_description_sentiment", "following_count", "followers_count", "following_to_followers", "is_possibly_sensitive", "is_default_profile_image", "is_profile_banner", "is_profile_image_valid", "tweet_freq", "parsed_owned_tweets_count", "parsed_owned_text_tweets_count", "parsed_retweets_count", "likes_freq", "media_freq", "followers_freq", "following_freq", "replies_to_owned", "quotes_to_owned", "retweets_to_owned", "avg_urls", "avg_hashtags", "identical_tweet_freq", "avg_tweet_sentiment", "avg_replies_per_follower", "avg_likes_per_follower", "avg_retweets_per_follower"]
TARGET_TWEETS = 125
MIN_TWEETS = 0
NUM_USERS = 2500
ADDING_TO_DATASET = True

# Will parse data set and abstract key values to use for model training
async def create_dataset():

    csvs = ['twibot-22-dataset.csv']
    client = get_client()

    last_user_id = None # add here the last user ID in the dataset to avoid duplicates

    try:
        df = pd.read_csv('dataset.csv')  
        last_user_id = int(df['user_id'].iloc[-1]) # get the last user ID in the dataset
        print(f"Last user ID in dataset: {last_user_id}")
    except:
        df = pd.DataFrame(columns=FIELDS)
        df.to_csv('dataset.csv', index=False)  # create the dataset file at the start
        print("Dataset file created.")

    for csv in csvs:
        df_reading = pd.read_csv(csv)

        if 'id' not in df_reading.columns or 'label' not in df_reading.columns: continue

        users_in_ds = pd.read_csv('dataset.csv').shape[0]

        humans = 0
        bots = 0

        for _, row in df_reading.iterrows():
            if users_in_ds == NUM_USERS: break
            user_id = row['id']
            label = row['label']
            if humans > bots and label == 'human' or bots > humans and label == 'bot': # balance the dataset
                print(f"Skipping user {user_id} with label {label} to balance the dataset.")
                continue
            if last_user_id != None: # skip users already in the dataset if adding onto existing dataset
                if int(user_id[1:]) == last_user_id:
                    last_user_id = None
                continue
            if not user_id or not label: continue # skip non-existent users
            res = await add_user_to_dataset(user_id[1:], label, client)
            if res == "INVALID USER": continue
            users_in_ds = pd.read_csv('dataset.csv').shape[0]
            print(f"Added user {user_id} ({users_in_ds}) to dataset.")
            if label == 'bot': bots += 1
            else: humans += 1
        
async def add_user_to_dataset(user_id: str, label: str, client): 
    try:
        user = await client.get_user_by_id(user_id)
    except Exception as e:
        print(f"Error fetching user with ID {user_id}: {e}")
        return "INVALID USER"

    if not user: 
        print(f"User with ID {user_id} not found.")
        return "INVALID USER"
    
    row = await analyze_user_data(user, label, True)
    if not row: 
        print(f"User with ID {user_id} has less than {MIN_TWEETS} tweets.")
        return "INVALID USER"
    df_row = pd.DataFrame([row])  
    df_row.to_csv('dataset.csv', mode='a', header=False, index=False)  # append row to dataset file

    return "SUCCESS"

# preprocesses user data to be used in the dataset
async def analyze_user_data(user: User, label, seeding_data=False):
    age = get_age(user.created_at)
    parsed_owned_tweets_count, parsed_owned_text_tweets_count, parsed_retweets_count, likes_count, replies_count, retweets_count, reply_tweets_count, urls_count, hashtags_count, quotes_tweet_count =  0, 0, 0, 0, 0, 0, 0, 0, 0, 0

    try:
        # analyze profile picture with openCV
        is_profile_image_valid = analyze_profile_image(user.profile_image_url)
    except Exception as e:
        print(f"Error analyzing profile image for user {user.id}: {e}")
        return
    
    tweets = []

    print(f"Fetching tweets for user {user.id}...")

    finished = False
    while not finished:
        try:
            res = await user.get_tweets('Tweets', count=TARGET_TWEETS)
            if seeding_data: await asyncio.sleep(22) # sleep every request to avoid rate limit
            while res and len(tweets) < TARGET_TWEETS:
                tweets += res
                res = await res.next()
                if seeding_data: await asyncio.sleep(22)
            finished = True
        except Exception as e:
            if 'Rate limit exceeded' in str(e): 
                print(f"Rate limit exceeded for user {user.id}. Sleeping for 15 minutes...")
                await asyncio.sleep(900) # sleep for 15 minutes to reset rate limit
            else: 
                print(f"Error fetching tweets for user {user.id}: {e}")
                return
    
    if len(tweets) <= MIN_TWEETS: 
        print(f"User {user.id} has less than {MIN_TWEETS} tweets.")
        return False # User is private or has zero tweets - not relevant for dataset

    # print(f"Analyzing tweets for user {user.id} with {len(tweets)} tweets...")

    sentiment_analyzer = pipeline('sentiment-analysis', model='cardiffnlp/twitter-roberta-base-sentiment', device=device, max_length=512, truncation=True)
    sentiment = 0

    tweets = tweets[:TARGET_TWEETS] # limit to 125 tweets
    
    for tweet in tweets:
        if tweet.retweeted_tweet: 
            parsed_retweets_count += 1
            continue
        if tweet.text:
            sentiment += get_sentiment_score(tweet.text, sentiment_analyzer)
            parsed_owned_text_tweets_count += 1
        parsed_owned_tweets_count += 1
        if tweet.in_reply_to: reply_tweets_count += 1
        hashtags_count += len(tweet.hashtags)
        likes_count += tweet.favorite_count
        replies_count += tweet.reply_count
        retweets_count += tweet.retweet_count
        urls_count += len(tweet.urls)
        if tweet.is_quote_status: quotes_tweet_count += 1
    
    identical_tweet_pairs, num_tweet_pairs = analyze_tweets_similarity(tweets)

    # print(f"Finished analyzing tweets for user {user.id}.")

    # 33 features
    return {
        # User Information
        'user_id': user.id,
        'screen_name': user.screen_name,
        'is_bot': 1 if label == 'bot' else 0,
        'account_age': age, 
        'is_blue_verified': 1 if user.is_blue_verified else 0,
        'is_verified': 1 if user.verified else 0,
        'profile_description_sentiment': round(get_sentiment_score(user.description, sentiment_analyzer), 3) if user.description else None,
        'following_count': user.following_count,
        'followers_count': user.followers_count,
        'following_to_followers': user.following_count if user.followers_count == 0 else round(user.following_count / user.followers_count, 3),
        'is_possibly_sensitive': 1 if user.possibly_sensitive else 0,
        'is_default_profile_image': 1 if user.default_profile_image else 0,
        'is_profile_banner': 1 if user.profile_banner_url else 0,
        'is_profile_image_valid': 1 if is_profile_image_valid else 0,
         # User Activity
        'tweet_freq': round(user.statuses_count / age, 3), 
        'parsed_owned_tweets_count': parsed_owned_tweets_count,
        'parsed_owned_text_tweets_count': parsed_owned_text_tweets_count,
        'parsed_retweets_count': parsed_retweets_count,
        'likes_freq': round(likes_count / age, 3),
        'media_freq': round(user.media_count / age, 3),
        'followers_freq': round(user.followers_count / age, 3),
        'following_freq': round(user.following_count / age, 3),
        # Tweet Analysis
        'replies_to_owned': 0 if parsed_owned_tweets_count == 0 else round(reply_tweets_count / parsed_owned_tweets_count, 3),
        'quotes_to_owned': 0 if parsed_owned_tweets_count == 0 else round(quotes_tweet_count / parsed_owned_tweets_count, 3),
        'retweets_to_owned': 0 if parsed_owned_tweets_count == 0 else round(parsed_retweets_count / parsed_owned_tweets_count, 3),
        'avg_urls': 0 if parsed_owned_tweets_count == 0 else round(urls_count / parsed_owned_tweets_count, 3),
        'avg_hashtags': 0 if parsed_owned_tweets_count == 0 else round(hashtags_count / parsed_owned_tweets_count, 3),
        'identical_tweet_freq': 0 if num_tweet_pairs == 0 else round(identical_tweet_pairs / num_tweet_pairs, 3), 
        'avg_tweet_sentiment': 0 if parsed_owned_text_tweets_count == 0 else round(sentiment / parsed_owned_text_tweets_count, 3),
        # Tweet Engagement
        'avg_replies_per_follower': replies_count if parsed_owned_tweets_count == 0 or user.followers_count == 0 else round(replies_count / parsed_owned_tweets_count / user.followers_count * 1000, 3),
        'avg_likes_per_follower': likes_count if parsed_owned_tweets_count == 0 or user.followers_count == 0 else round(likes_count / parsed_owned_tweets_count / user.followers_count * 1000, 3),
        'avg_retweets_per_follower': retweets_count if parsed_owned_tweets_count == 0 or user.followers_count == 0 else round(retweets_count / parsed_owned_tweets_count / user.followers_count * 1000, 3),
    }


if __name__ == "__main__":
    asyncio.run(create_dataset())


