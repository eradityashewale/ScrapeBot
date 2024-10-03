from twikit import Client, TooManyRequests
import csv
from configparser import ConfigParser
import asyncio
from datetime import datetime

MINIMUM_TWEETS = 10
QUERY = 'CHATBOT'

# Load configuration
config = ConfigParser()
config.read('config.ini')
username = config["X"]['username']
password = config["X"]['password']
email = config["X"]['email']

# Create CSV file and write headers
with open('tweets.csv', 'w', newline="", encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['No', 'Username', 'Text', 'Created At', 'Retweets', 'Likes'])

# Authenticate to x.com
client = Client(language='en-US')
client.load_cookies('cookies.json')
tweet_count = 0 

async def main():
    global tweet_count  # Declare tweet_count as global
    
    await client.login(auth_info_1=username, auth_info_2=email, password=password)
    
    # Await the search_tweet coroutine
    tweets = await client.search_tweet(QUERY, 'Top')

    while tweet_count < MINIMUM_TWEETS:
        if not tweets or len(tweets) == 0:
            print(f'{datetime.now()} - Getting tweets....')
            tweets = await client.search_tweet(QUERY, product='Top')
        else:
            print(f'{datetime.now()} - Getting next tweets...')
            tweets = await tweets.next()  # Await this call

        if not tweets:
            print(f'{datetime.now()} - No more tweets found')
            break

        for tweet in tweets:
            tweet_count += 1
            tweet_data = [tweet_count, tweet.user.name, tweet.text, tweet.created_at, tweet.retweet_count, tweet.favorite_count]

            # Write tweet data to CSV
            with open('tweets.csv', 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(tweet_data)

        print(f'{datetime.now()} - Got {tweet_count} tweets')


# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
