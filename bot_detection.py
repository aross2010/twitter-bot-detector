import random
import joblib

model = joblib.load("bot_model.joblib")

def detect_bot(parsed_user):
    try:
        # TODO: FIX THE ORDER OF THE FEATURES AND MAKE SURE THEY ARE CORRECT. SHOULD BE IN THE SAME ORDER AS THE DATASET
        features = [
            parsed_user.get('account_age', 0),
            parsed_user.get('is_blue_verified', 0),
            parsed_user.get('profile_description_sentiment', 0),
            parsed_user.get('following_count', 0),
            parsed_user.get('followers_count', 0),
            parsed_user.get('following_to_followers_ratio', 0),
            parsed_user.get('tweets_count', 0),
            parsed_user.get('likes_count', 0),
            parsed_user.get('media_count', 0),
            parsed_user.get('avg_sentiment', 0),
            parsed_user.get('retweets_ratio', 0),
            parsed_user.get('freq_of_tweets', 0),
            parsed_user.get('identical_tweets_ratio', 0),
            parsed_user.get('avg_replies_per_tweet', 0),
            parsed_user.get('avg_urls_per_tweet', 0),
            parsed_user.get('avg_likes_per_tweet', 0),
            parsed_user.get('possibly_sensitive', 0),
            parsed_user.get('profile_image_url', 0),  # 1 if present, 0 otherwise
            parsed_user.get('profile_banner_url', 0),  # 1 if present, 0 otherwise
            parsed_user.get('is_profile_image_valid', 0),
            parsed_user.get('followers_to_likes_ratio', 0)
        ]

        
        features_2d = [features]

        prediction = model.predict(features_2d)
        print(f"Prediction: {prediction}")
        
        # true if bot, false if human
        return prediction[0] == 1

    except Exception as e:
        print(f"Error predicting user: {e}")
        return None