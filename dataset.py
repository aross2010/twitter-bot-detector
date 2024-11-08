import pandas as pd
import asyncio 
from main import get_client
from user import User
from datetime import datetime

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
def parse_user(user: User, label):
    age = get_age(user.created_at)
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
        'retweets_count': 0, # to be implemented when iterating through tweets
        'freq_of_tweets': round(user.statuses_count / age, 4), # tweets per year
        'identical_tweets_count': 0, # to be implemented when iterating through tweets with fuzzywuzzy
        'tweets_to_reply_ratio': 0, # to be implemented when iterating through tweets
        'possibly_sensitive': 1 if user.possibly_sensitive else 0,
        'profile_image_url': user.profile_image_url,
        'profile_banner_url': user.profile_banner_url,
        'is_profile_image_valid': 0, # to be implemented when checking image validity with openCV
        'followers_to_engagement_ratio': 0, # to be implemented when iterating through tweets
        'followers_to_likes_ratio': 0, # to be implemented when iterating through tweets
    }

# returns the age in years to three decimal places
def get_age(created_at: str):
    date = datetime.strptime(created_at, '%a %b %d %H:%M:%S %z %Y')
    now = datetime.now(date.tzinfo)
    delta = now - date
    age = delta.days / 365.25
    return round(age, 3)

    

asyncio.run(create_dataset())






