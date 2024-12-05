# Twitter Bot Detector - SJSU CS 166 Information Security Project

## About
Our project, Twitter Bot Detector, takes a machine learning approach to identifying Twitter Bots. In conjunction with the TwiBot-22 dataset, we came up with our own set of user features to anaylyze to create our own dataset. We trained a Random Forest Classifer Machine Learning model with our dataset to make a predictions on Twitter accounts of whether they are a bot or a human. Through our intuitive web application, users can find any Twitter/X account and use our model to help them make a decision on the account status.

### User Features
We broke down our user features into four key categories (**: not used for model training):

* For each user, we analyzed 125 tweets due to rate limiting and time constraints.

#### User Information
- user_id**: id of the user
- screen_name**: screen name of the user
- is_bot: from the TwiBot-22 dataset. The target variable.
- account_age: how old the account is in days
- is_blue_verified: if the account has a blue checkmark verification
- is_verified: if the account is organizationally verified
- profile_description_sentiment: the sentiment score (-1 to 1, from transformers) of the user's profile description
- following_count: number of users the user is following
- followers_count: number of followers the user has
- following_to_followers: ratio of following_count to followers_count
- is_possibly_sensitive: 1 if the account is contains sensitive content, 0 else
- is_default_profile_image: 1 if the account has the default profile image, 0 else
- is_profile_banner: 1 if the account has a banner, 0 else
- is_profile_image_valid: 1 is the account has a valid profile image (from opencv), 0 else

#### User Activity 
- tweet_freq: total number of tweets / account_age
- parsed_owned_tweets_count**: number of tweets parsed that the user owns
- parsed_owned_text_tweets_count**: number of tweets parsed that the user owns that has text
- parsed_retweets_count**: number of tweets parsed that are retweets
- likes_freq: number of tweets liked / account_age
- media_freq: number of media posts / account_age
- followers_freq: followers_count / account_age
- following_freq: following_count / account_age

#### Tweet Analysis
- replies_to_owned: ratio of tweets that are replies to other tweets to parsed_owned_tweets
- quotes_to_owned: ratio of tweets that are quoting another tweet to parsed_owned_tweets
- retweets_to_owned: ratio of parsed_retweets_count to parsed_owned_tweets
- avg_urls: total number of urls in tweets / parsed_owned_tweets_count
- avg_hashtags: total number of hashtags in tweets / parsed_owned_tweets_count
- identical_tweet_freq: total pairs of tweets that have a 0.95 or greater similarity score (via fuzzywuzzy) / total number of tweet pairs
- avg_tweet_sentiment: summed frequency score for each tweet with text / parsed_owned_text_tweets_count

#### Tweet Engagement (scaled to per 1000 followers)
- avg_replies_per_follower: total number of replies recieved on tweets / followers_count
- avg_likes_per_follower: total number of likes recieved on tweets / followers_count
- avg_retweets_per_follower: total number of retweets recieved on tweets / followers_count

### Limitations
- No access to the Twitter/X API means we pivoted to using the Twikit web scraping library which limited the amount of data we could process.
- Though the Twibot-22 dataset is reputable benchmark dataset, we would ideally prefer to use a more modern dataset with new users as the website's user base continues to evolve.

### Tools Used

#### Web Application
- Backend: Python & Flask
- Frontend: TypeScript, Next.js, TailwindCSS

#### Machine Learning
- Python: For uts extensive machine learning libraries and tools
- Twikit: Web scraping Twitter/X data
- Pandas: Data manipulation from and to our model and datasets
- scikit-learn: Implementation, testing, and evaluation of our Random Forest Classifier
- Shap: Interpreate the results of our model for model fine tuning
- OpenCV: Image analysis
- Transformers: Sentiment analysis
- Joblib: Save and use our model

### Demo

https://github.com/user-attachments/assets/1f999f19-67ff-4e2f-a2e0-10a8462e9744


