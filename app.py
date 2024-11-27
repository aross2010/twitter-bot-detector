from flask import Flask, request, jsonify, render_template
from main import get_client
from user import User
from dataset import analyze_user_data
from bot_detection import detect_bot
import asyncio

app = Flask(__name__)

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
        client = get_client()
        user = await client.get_user_by_screen_name(screen_name)
        print(f"Retrieved user: {user}")

        if not user:
            return {"error": "Invalid User"}

        parsed_user = await analyze_user_data(user, "UNKNOWN")
        print(f"Parsed user: {parsed_user}")

        bot_status = detect_bot(parsed_user)
        print(f"Bot status: {bot_status}")

        return {"bot_status": bool(bot_status)}
    
    except Exception as e:
        print(f"Exception caught: {e}")
        return {"error": str(e)}

if __name__ == '__main__':
    app.run(debug=True)
