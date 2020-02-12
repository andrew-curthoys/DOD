import tweepy
from keys import *
import random
import sqlite3
from datetime import datetime
import time

# create status for tweeting or testing
# test = 'tweet' will send a tweet
# test = 'test' will print contents to terminal
test = 'tweet'


def connect_to_twitter():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)
    return api

def get_quote():
    # create a list of quote ids then a randomly shuffled list
    # of quote ids to "hash" the day of the year to a random id
    random.seed(7)
    quote_ids = list(range(1, 95))
    quote_id_hash = random.sample(quote_ids, len(quote_ids))

    # create a dictionary of quote ids matched with their
    # randomly shuffled id "hash"
    id_dict = {}
    for id_, hash_ in zip(quote_ids, quote_id_hash):
        id_dict[id_] = hash_

    # get the day of the year, then take the mod of 95 and add 1
    # to get an id between 1 and 95 (the quote_id range in the DB)
    day_of_year = datetime.now().timetuple().tm_yday
    day_of_year_id = day_of_year % 95 + 1
    quote_id = id_dict[day_of_year_id]

    # Connect to SQLite database
    conn = sqlite3.connect("../dick_or_don.db")
    db = conn.cursor()

    quote = db.execute('''SELECT
                                quote
                            FROM quotes
                        WHERE quote_id = ?;''',
                            (quote_id,))
    quote = quote.fetchone()
    quote = quote[0]
    conn.close()

    quote = f'Who the hell said this shit -\nDick Nixon or Don Trump?\n\n"{quote}"'
    return quote


def send_tweet(api, quote):
    api.update_status(quote)


if __name__ == "__main__":
    quote = get_quote()
    if test == 'tweet':
        api = connect_to_twitter()
        if len(quote) <= 280:
            send_tweet(api, quote)
        else:
            quote_1 = f'{quote[:277]}...'
            quote_2 = quote[277:]
            send_tweet(api, quote_1)
            time.sleep(5)
            tweet_1_id = api.user_timeline('dickordon')[0].id
            api.update_status(quote_2, in_reply_to_status_id = tweet_1_id)
    elif test == 'test':
        print(len(quote))
        print(quote)
    else:
        print('Must specify a test/tweet status!')