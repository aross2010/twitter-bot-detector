
from dotenv import load_dotenv 
import os
from twikit import Client
import asyncio
from bot_detection import detect_bot

# main function to fetch one user and determine if they are a bot
async def main():

    client = get_client()

    user = await client.get_user_by_screen_name('AVFCOfficial')
    bot_status = detect_bot(user)

    print(f"Bot status: {bot_status}")
    
    # Print all attributes of the user object along with their values
    for attr in dir(user):
        if not attr.startswith("_"):  # Skip private or internal attributes
            try:
                value = getattr(user, attr)
                print(f"{attr}: {value}")
            except Exception as e:
                print(f"{attr}: Could not retrieve value - {e}")

def get_client():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    envars = os.path.join(dir_path, '.env')
    load_dotenv(envars)

    client = Client('en-US')
    client.load_cookies('cookies.json')
    return client

if __name__ == "__main__":
    asyncio.run(main())
    


