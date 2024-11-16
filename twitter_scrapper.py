import asyncio
from datetime import datetime
from db_connection import get_db_connection
from twikit import Client
from random import randint
from configparser import ConfigParser
import traceback

MINIMUM_TWEETS = 5
QUERY = 'eth'

# Create a database connection
db_conn = get_db_connection()
db_conn.autocommit = True  # Optional: ensures automatic commit after each transaction
cursor = db_conn.cursor()

# Load configuration
config = ConfigParser()
config.read('config.ini')
username = config["X"]['username']
password = config["X"]['password']
email = config["X"]['email']

client = Client(language='en-US')
client.load_cookies('cookies.json')
tweet_count = 0

async def get_tweets(tweets):
    if not tweets or len(tweets) == 0:
        print(f'{datetime.now()} - Getting tweets....')
        tweets = await client.search_tweet(QUERY, product='Top')
    else:
        wait_time = randint(5, 10)
        print(f'{datetime.now()} - Getting next tweets after {wait_time} seconds....')
        await asyncio.sleep(wait_time)
        print(f'{datetime.now()} - Getting next tweets...')
        tweets = await tweets.next()
    return tweets

async def insert_user(username):
    try:
        if username:
            cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            print(f"User lookup result: {result}")  # Debugging print

            if result:
                return result[0]  # User found, return the user_id
            else:
                cursor.execute("INSERT INTO users (username) VALUES (%s) RETURNING user_id", (username,))
                user_id = cursor.fetchone()[0]
                db_conn.commit()
                print(f"Inserted new user with user_id: {user_id}")  # Debugging print
                return user_id
    except Exception as e:
        print(f"Error in insert_user: {e}")
        traceback.print_exc()

async def main():
    global tweet_count
    await client.login(auth_info_1=username, auth_info_2=email, password=password)
    
    tweets = await client.search_tweet(QUERY, 'Top')

    while tweet_count < MINIMUM_TWEETS:
        tweets = await get_tweets(tweets)
        print(tweets)

        if not tweets:
            print(f'{datetime.now()} - No more tweets found')
            break

        for tweet in tweets:
            tweet_count += 1

            # Ensure tweet.user.name and tweet.created_at are valid
            user_id = await insert_user(tweet.user.name) if tweet.user and tweet.user.name else None

            # If the user_id is None, skip the tweet to avoid database errors
            if not user_id:
                print(f"Skipping tweet due to missing user_id: {tweet.text}")
                continue
            user_data = [
                tweet.user.screen_name,
                tweet.user.profile_img_url,
                tweet.user.profile_baneer_url, 
                tweet.user.users_url, 
                tweet.user.bio, 
                tweet.user.description, 
                tweet.user.is_bule_verified, 
                tweet.user.location, 
                tweet.user.followers_count, 
                tweet.user.tweet_count, 
            ]
            tweet_data = [
                tweet_count, 
                user_id, 
                tweet.text, 
                tweet.created_at, 
                tweet.retweet_count, 
                tweet.favorite_count,
                tweet.joined
            ]

            try:
                cursor.execute(
                    """
                    UPDATE users
                    SET screen_name = %s, profile_img_url = %s, profile_baneer_url = %s, users_url = %s, bio = %s, description = %s, 
                    is_bule_verified = %s, location = %s, following_count = %s, followers_count = %s, tweets_count = %s, joined = %s
                    WHERE user_id = %s
                    """, user_data
                ), 

                cursor.execute(
                    """
                    INSERT INTO tweets (tweet_id, user_id, content, created_at, retweet_count, like_count)
                    VALUES (%s, %s, %s, %s, %s, %s);
                    """,
                    tweet_data
                )
                db_conn.commit()  # Commit the tweet data to the database
                print(f"Tweet {tweet_count} inserted successfully.")  # Debugging print

            except Exception as e:
                print(f"Error inserting tweet {tweet_count}: {e}")
                traceback.print_exc()

        print(f'{datetime.now()} - Got {tweet_count} tweets')

    cursor.close()
    db_conn.close()

if __name__ == "__main__":
    asyncio.run(main())
