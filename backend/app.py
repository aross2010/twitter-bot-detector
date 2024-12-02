from flask import Flask, request, jsonify, render_template
from helpers import get_client
from user import User
from dataset import analyze_user_data
from predict import make_prediction
import asyncio
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    user_input = request.get_json()
    screen_name = user_input.get('screen_name')

    #single event loop
    result = asyncio.run(process_prediction(screen_name))
    return jsonify(result)

async def process_prediction(screen_name):
    try:
        bot_status = await make_prediction(screen_name)
        print(f"Bot status: {bot_status}")

        serialized_result = {
            "prediction": bot_status['prediction'],
            "probability": float(bot_status['probability']),  #converted np.float64 to Python float
            "top_features": {
                key: value.tolist() if isinstance(value, pd.Series) else value
                for key, value in bot_status['top_features'].items()  
            }
        }

        return serialized_result
    
    except Exception as e:
        print(f"Exception caught: {e}")
        return {"error": str(e)}


@app.route('/test', methods=['GET'])
def test():
    print("Test route hit.")
    return jsonify({"message": "Success"})

if __name__ == '__main__':
    app.run(debug=True)
