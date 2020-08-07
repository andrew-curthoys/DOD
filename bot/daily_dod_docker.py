import tweepy
from keys import *
import random
import sqlite3
from datetime import datetime
import time


class Tweet:
    def __init__(self):
        # create status for tweeting or testing
        # test = 'tweet' will send a tweet
        # test = 'test' will print contents to terminal
        self.test = 'test'

        # Connect to Twitter API
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
        self.api = tweepy.API(auth)
        self.last_tweet = self.api.user_timeline('dickordon')[0]
        self.id_dict = {}
        self.new_tweet = ""
        self.answer_tweet = ""
        self.utterer = 0

        # Connect to SQLite database
        self.conn = sqlite3.connect("../dick_or_don.db")
        self.db = self.conn.cursor()

        # Create lists of variables to put in reply with answer to last tweet
        self.dick_names = ["Dick Nix", "Tricky Dick", "the one who wasn't impeached", "Grandpa Dick"]
        self.don_names = ["Uncle Donny", "Don Drumpf", "the orange one", "Colonel Bone Spurs", "the guy who bankrupted a casino", "Fred Trump's greatest embarrassment"]

    def generate_quote_dict(self):
        # create a list of quote ids then a randomly shuffled list
        # of quote ids to "hash" the day of the year to a random id
        random.seed(7)
        quote_ids = list(range(1, 96))
        quote_id_hash = random.sample(quote_ids, len(quote_ids))

        # create a dictionary of quote ids matched with their
        # randomly shuffled id "hash"
        for id_, hash_ in zip(quote_ids, quote_id_hash):
            self.id_dict[id_] = hash_

    def get_last_tweet_utterer(self):
        last_tweet_date = self.last_tweet.created_at
        last_tweet_day_of_year = (last_tweet_date - datetime(last_tweet_date.year, 1, 1)).days + 1
        last_tweet_day_of_year_id = last_tweet_day_of_year % 95 + 1
        last_tweet_quote_id = self.id_dict[last_tweet_day_of_year_id]

        utterer = self.db.execute('''SELECT
                                    utterer
                                FROM quotes
                            WHERE quote_id = ?;''',
                                  (last_tweet_quote_id,))
        utterer = utterer.fetchone()
        self.utterer = utterer[0]

    def send_reply(self):
        # Get the ID of the last tweet to reply to
        last_tweet_id = self.last_tweet.id_str

        # Reset random seed
        random.seed()

        # Get which tweet option & name option to use
        tweet_no = random.randint(0, 1)
        name_no = random.randint(0, max(len(self.dick_names), len(self.don_names)))

        # Get the name option to use & make sure it's not out of bounds of the selected list (in case one list is longer than the other
        dick_name_no = name_no % len(self.dick_names)
        dick_name = self.dick_names[dick_name_no]
        don_name_no = name_no % len(self.don_names)
        don_name = self.don_names[don_name_no]

        # Get tweet text
        if self.utterer == 0:
            tweet_list = [f"If you guessed {dick_name}, that's a bingo!! Well done!",
                          f"If you guessed {don_name}, that is incorrect. You should feel shame!"]
            image_list = ["./images/nixon_fist.gif", "./images/nixon_shake_no.gif"]
            self.answer_tweet = tweet_list[tweet_no]
            image = image_list[tweet_no]
        else:
            tweet_list = [f"If you guessed {dick_name}, you are WRONG. Sad!",
                          f"if you guessed {don_name}, you are the the smartest person alive. The best, there are none smarter than you."]
            image_list = ["./images/don_wrong.gif", "./images/don_nod_yes.gif"]
            self.answer_tweet = tweet_list[tweet_no]
            image = image_list[tweet_no]

        if self.test == "tweet":
            # Rip tweet
            self.api.update_with_media(filename=image, status=self.answer_tweet, in_reply_to_status_id=last_tweet_id)

    def get_new_tweet(self):
        # get the day of the year, then take the mod of 95 and add 1
        # to get an id between 1 and 95 (the quote_id range in the DB)
        day_of_year = datetime.now().timetuple().tm_yday
        day_of_year_id = day_of_year % 95 + 1
        quote_id = self.id_dict[day_of_year_id]

        quote = self.db.execute('''SELECT
                                    quote
                                FROM quotes
                            WHERE quote_id = ?;''',
                                (quote_id,))
        quote = quote.fetchone()
        quote = quote[0]

        self.new_tweet = f'Who the hell said this shit -\nDick Nixon or Don Trump?\n\n"{quote}"'

    def send_new_tweet(self):
        if self.test == 'tweet':
            if len(self.new_tweet) <= 280:
                self.api.update_status(self.new_tweet)
            else:
                quote_1 = f'{self.new_tweet[:277]}...'
                quote_2 = self.new_tweet[277:]
                self.api.update_status(quote_1)
                time.sleep(5)
                tweet_1_id = self.api.user_timeline('dickordon')[0].id_str
                self.api.update_status(quote_2, in_reply_to_status_id = tweet_1_id)

        elif self.test == 'test':
            print(f'New quote length = {len(self.new_tweet)}')
            print(f'New quote = {self.new_tweet}')
            print(f'Last tweet reply = {self.answer_tweet}')
        else:
            print('Must specify a test/tweet status!')

    def close_connection(self):
        self.conn.close()


if __name__ == "__main__":
    tweet = Tweet()
    tweet.generate_quote_dict()
    tweet.get_last_tweet_utterer()
    tweet.send_reply()
    tweet.get_new_tweet()
    tweet.send_new_tweet()
    tweet.close_connection()

