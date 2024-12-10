# 🐦 Twitter Bot Detector  
### SJSU CS 166 Information Security Project  

---

## 📖 About

Twitter Bot Detector is a machine learning-based project designed to identify Twitter/X bots. Using the **[TwiBot-22](https://twibot22.github.io/)** dataset we analyzed and engineered unique user features to create a custom dataset for training a **Random Forest Classifier** model. This model predicts whether a Twitter account is a bot or human.

Through our intuitive web application, users can search for any Twitter/X account and leverage our model to evaluate its authenticity.  

---

## 📋 Table of Contents
- [About](#about)
- [User Features](#user-features)
  - [User Information](#user-information)
  - [User Activity](#user-activity)
  - [Tweet Analysis](#tweet-analysis)
  - [Tweet Engagement](#tweet-engagement)
- [Limitations](#limitations)
- [Tools Used](#tools-used)
  - [Web Application](#web-application)
  - [Machine Learning](#machine-learning)
- [Demo](#demo)
- [Getting Started](#getting-started)
- [License](#license)

---

## 📊 User Features

For data about user's tweets, we analyzed **125 tweets** due to rate-limiting constraints. Features were divided into the following categories:

### **1. User Information**
| Feature                     | Description                                                                 |
|-----------------------------|-----------------------------------------------------------------------------|
| **user_id**                 | User's unique ID (not used for model training).                            |
| **screen_name**             | Screen name of the user (not used for model training).                     |
| **is_bot**                  | Target variable indicating if the account is a bot (from TwiBot-22).       |
| **account_age**             | Account age in days.                                                       |
| **is_blue_verified**        | Whether the account has a blue checkmark.                                  |
| **is_verified**             | Whether the account is organizationally verified.                         |
| **profile_description_sentiment** | Sentiment score (-1 to 1) of the user's profile description.           |
| **following_count**         | Number of users the account is following.                                  |
| **followers_count**         | Number of followers the account has.                                       |
| **following_to_followers**  | Ratio of following count to follower count.                                |
| **is_possibly_sensitive**   | Whether the account contains sensitive content.                            |
| **is_default_profile_image**| Whether the account has the default profile image.                        |
| **is_profile_banner**       | Whether the account has a banner.                                          |
| **is_profile_image_valid**  | Whether the account has a valid profile image (via OpenCV).               |

### **2. User Activity**
| Feature                     | Description                                                                 |
|-----------------------------|-----------------------------------------------------------------------------|
| **tweet_freq**              | Total number of tweets divided by account age.                             |
| **likes_freq**              | Number of tweets liked divided by account age.                             |
| **media_freq**              | Media posts divided by account age.                                        |
| **followers_freq**          | Followers count divided by account age.                                    |
| **following_freq**          | Following count divided by account age.                                    |

### **3. Tweet Analysis**
| Feature                     | Description                                                                 |
|-----------------------------|-----------------------------------------------------------------------------|
| **replies_to_owned**        | Ratio of replies to total owned tweets.                                     |
| **quotes_to_owned**         | Ratio of quotes to total owned tweets.                                      |
| **retweets_to_owned**       | Ratio of retweets to total owned tweets.                                    |
| **avg_urls**                | Average number of URLs per tweet.                                           |
| **avg_hashtags**            | Average number of hashtags per tweet.                                       |
| **avg_tweet_sentiment**     | Average sentiment score for all tweets.                                     |

### **4. Tweet Engagement (Scaled to Followers)**
| Feature                     | Description                                                                 |
|-----------------------------|-----------------------------------------------------------------------------|
| **avg_replies_per_follower**| Average number of replies per 1000 followers.                              |
| **avg_likes_per_follower**  | Average number of likes per 1000 followers.                                |
| **avg_retweets_per_follower**| Average number of retweets per 1000 followers.                            |

---

## ⚠️ Limitations

- **Data Constraints**: No access to the Twitter/X API led us to use the **Twikit web scraping library**, limiting the amount of data processed due to rate limiting.
- **Dataset Freshness**: The TwiBot-22 dataset, while a reputable benchmark, is nearly three years old may not reflect the evolving Twitter/X user base.

---

## 🛠 Tools Used

### Web Application
- 🐍 **Backend**: Python & Flask  
- 💻 **Frontend**: TypeScript, Next.js, TailwindCSS  

### Machine Learning
- **Python**: Extensive libraries for ML development.  
- **Twikit**: Web scraping Twitter/X data.
- **Jupyter Notebook**: Interactive environment for model visualization.
- **Pandas**: Data manipulation and processing.  
- **scikit-learn**: Implementation of Random Forest Classifier.  
- **OpenCV**: Image analysis for profile validation.  
- **Transformers**: Sentiment analysis for text data.  
- **Shap**: Model interpretation and fine-tuning.  
- **Joblib**: Saving and deploying the trained model.  

---

## 🎥 Demo



https://github.com/user-attachments/assets/3add7525-8740-4a4a-ba40-0c1dba679028



---

## 🚀 Getting Started

Clone the repository and install dependencies to run the project locally.

```bash
# Clone the repository
git clone https://github.com/aross2010/twitter-bot-detector.git

# Navigate to the project directory
cd twitter-bot-detector

# Navigate to the backend directory
cd backend

# Install dependencies (backend)
pip install -r requirements.txt

# Start the backend server
python3 app.py

# Navigate to the frontend directory
cd frontend/client-bot-detector

# Install dependencies (frontend)
npm install

# Start the frontend server
npm run dev
