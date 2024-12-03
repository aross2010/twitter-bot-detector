import asyncio
from helpers import get_client, get_age, analyze_profile_image, get_sentiment_score, analyze_tweets_similarity, features_dict
from transformers import pipeline
import torch
import pandas as pd
import joblib
import shap

TARGET_TWEETS = 125
device = torch.device("cuda" if torch.cuda.is_available() else "cpu") 
# function that makes prediction
# retuns prediction (human | bot | invalid), probability of prediction,
# and top three user features that contributed to the prediction w/ their values
# prediction can be invalid if the user is private (unable to access data) 
# or has no tweets (not enough data)
async def make_prediction(screen_name: str):
    client = get_client()
    user = await client.get_user_by_screen_name(screen_name)
    if not user: return {"prediction": "invalid", "probability": 0, "features": [], "error": "User not found."} 

    parsed_owned_tweets_count, parsed_owned_text_tweets_count, parsed_retweets_count, likes_count, replies_count, retweets_count, reply_tweets_count, urls_count, hashtags_count, quotes_tweet_count, sentiment =  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    age = get_age(user.created_at)

    try:
        # analyze profile picture with openCV
        is_profile_image_valid = analyze_profile_image(user.profile_image_url)
    except Exception as e:
        print(f"Error analyzing profile image for user {user.id}: {e}")
        return

    tweets = []

    finished = False
    while not finished:
        try:
            res = await user.get_tweets('Tweets', count=TARGET_TWEETS)
            while res and len(tweets) < TARGET_TWEETS:
                tweets += res
                res = await res.next()
            finished = True
        except Exception as e:
            if 'Rate limit exceeded' in str(e): 
                return {"prediction": "invalid", "probability": 0, "features": [], "error": "Server rate limit exceeded. Try again in 15 minutes."}
    
    if len(tweets) <= 0: 
        return {"prediction": "invalid", "probability": 0, "features": [], "error": "User is either private or has no tweets to analyze."}

    sentiment_analyzer = pipeline('sentiment-analysis', model='cardiffnlp/twitter-roberta-base-sentiment', device=device, max_length=512, truncation=True)
    tweets = tweets[:TARGET_TWEETS]

    for tweet in tweets:
        if tweet.retweeted_tweet: 
            parsed_retweets_count += 1
            continue
        if tweet.text:
            sentiment += get_sentiment_score(tweet.text, sentiment_analyzer)
            parsed_owned_text_tweets_count += 1
        if tweet.in_reply_to: reply_tweets_count += 1
        if tweet.is_quote_status: quotes_tweet_count += 1
        parsed_owned_tweets_count += 1
        hashtags_count += len(tweet.hashtags)
        likes_count += tweet.favorite_count
        replies_count += tweet.reply_count
        retweets_count += tweet.retweet_count
        urls_count += len(tweet.urls)

    identical_tweet_pairs, num_tweet_pairs = analyze_tweets_similarity(tweets)

    features = {
        'account_age': age,
        'is_blue_verified': user.is_blue_verified,
        'profile_description_sentiment': round(get_sentiment_score(user.description, sentiment_analyzer), 3) if user.description else 0,
        'following_count': user.following_count,
        'followers_count': user.followers_count,
        'following_to_followers': round(user.following_count / user.followers_count, 3) if user.followers_count > 0 else 0,
        'is_possibly_sensitive': 1 if user.possibly_sensitive else 0,
        'is_default_profile_image': 1 if user.default_profile_image else 0,
        'is_profile_banner': 1 if user.profile_banner_url else 0,
        'is_profile_image_valid': 1 if is_profile_image_valid else 0,
        'tweet_freq': round(user.statuses_count / age, 3) if age > 0 else 0,
        'likes_freq': round(likes_count / age, 3) if age > 0 else 0,
        'media_freq': round(user.media_count / age, 3) if age > 0 else 0,
        'followers_freq': round(user.followers_count / age, 3) if age > 0 else 0,
        'following_freq': round(user.following_count / age, 3) if age > 0 else 0,
        'replies_to_owned': round(reply_tweets_count / parsed_owned_tweets_count, 3) if parsed_owned_tweets_count > 0 else 0,
        'quotes_to_owned': round(quotes_tweet_count / parsed_owned_tweets_count, 3) if parsed_owned_tweets_count > 0 else 0,
        'retweets_to_owned': round(retweets_count / parsed_owned_tweets_count, 3) if parsed_owned_tweets_count > 0 else 0,
        'avg_urls': round(urls_count / parsed_owned_tweets_count, 3) if parsed_owned_tweets_count > 0 else 0,
        'avg_hashtags': round(hashtags_count / parsed_owned_tweets_count, 3) if parsed_owned_tweets_count > 0 else 0,
        'identical_tweet_freq': round(identical_tweet_pairs / num_tweet_pairs, 3) if num_tweet_pairs > 0 else 0,
        'avg_tweet_sentiment': round(sentiment / parsed_owned_text_tweets_count, 3) if parsed_owned_text_tweets_count > 0 else 0,
        'avg_replies_per_follower': round(replies_count / parsed_owned_tweets_count / user.followers_count * 1000, 3) if user.followers_count > 0 and parsed_owned_tweets_count > 0 else 0,
        'avg_likes_per_follower': round(likes_count / parsed_owned_tweets_count / user.followers_count * 1000, 3) if user.followers_count > 0 and parsed_owned_tweets_count > 0 else 0,
        'avg_retweets_per_follower': round(retweets_count / parsed_owned_tweets_count / user.followers_count * 1000, 3) if user.followers_count > 0 and parsed_owned_tweets_count > 0 else 0,
    }

    user_df = pd.DataFrame(features, index=[0])

    model = joblib.load('model.joblib')
    prediction = model.predict(user_df.values)
    probabilities = model.predict_proba(user_df.values)

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(user_df)
    feature_names = user_df.columns.tolist()

    feature_contributions = list(zip(feature_names, shap_values[0][:, 0 if prediction[0] == 0 else 1]))
    feature_contributions.sort(key=lambda x: abs(x[1]), reverse=True)
    top_features = {features_dict[feature]: features[feature] for feature, _ in feature_contributions[:3]}

    return {
        'prediction': 'bot' if prediction[0] == 1 else 'human',
        'probability': float(probabilities[0][1]) if prediction[0] == 1 else float(probabilities[0][0]),
        'top_features': top_features
    }

if __name__ == '__main__':
    screen_name = 'DKVaishnav96' # DKVaishnav96 for example
    print(asyncio.run(make_prediction(screen_name)))
    