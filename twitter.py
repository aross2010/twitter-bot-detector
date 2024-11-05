
from dotenv import load_dotenv 
import os
from twikit import Client
import asyncio

async def main():

    # Get full path
    dir_path = os.path.dirname(os.path.realpath(__file__))
    envars = os.path.join(dir_path, '.env')
    load_dotenv(envars)

    client = Client('en-US')
    # await client.login(auth_info_1=username, auth_info_2=email, password=password)
    # await client.save_cookies('cookies.json') # Save cookies to avoid logging in again

    client.load_cookies('cookies.json')

    user = await client.get_user_by_screen_name('AVFCOfficial')
    
    # Print all attributes of the user object along with their values
    for attr in dir(user):
        if not attr.startswith("_"):  # Skip private or internal attributes
            try:
                value = getattr(user, attr)
                print(f"{attr}: {value}")
            except Exception as e:
                print(f"{attr}: Could not retrieve value - {e}")

asyncio.run(main())
    


