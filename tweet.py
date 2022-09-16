from os import environ
from datetime import datetime, timedelta
import gspread
from requests_oauthlib import OAuth1Session
import time
from dotenv import load_dotenv
load_dotenv()
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONSUMER_KEY = environ['CONSUMER_KEY']
CONSUMER_SECRET = environ['CONSUMER_SECRET']
ACCESS_TOKEN = environ['ACCESS_TOKEN']
ACCESS_SECRET = environ['ACCESS_SECRET']

# Make the request
oauth = OAuth1Session(
    CONSUMER_KEY,
    client_secret=CONSUMER_SECRET,
    resource_owner_key=ACCESS_TOKEN,
    resource_owner_secret=ACCESS_SECRET,
)

gc = gspread.service_account(filename='credentials.json')
sh = gc.open_by_key('1UwnTNNGgdgjezTiPXfjOOnRq1HAl2fCT49LSfyefyrg')
worksheet = sh.sheet1

INTERVAL = int(environ['INTERVAL'])
DEBUG = environ['DEBUG'] == '1'

def main():
    while True:
        tweet_records = worksheet.get_all_records()
        current_time = datetime.utcnow() + timedelta(hours=2)
        logger.info(f'{len(tweet_records)} tweets found at {current_time.time()}')
        for idx, tweet in enumerate(tweet_records, start=2):
            msg = tweet['message']
            time_str = tweet['time']
            done = tweet['done']
            date_time_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
            if not done:
                now_time_cet = datetime.utcnow() + timedelta(hours=2)
                if date_time_obj < now_time_cet:
                    logger.info('this should be tweeted')
                    try:
                        #if not DEBUG
                        payload = {"text": msg}
                        # Making the request
                        response = oauth.post(
                                    "https://api.twitter.com/2/tweets",
                                    json=payload,
                                    )

                        #response = auth.create_tweet(text=payload)
                        #api.update_status(msg)
                        worksheet.update_cell(idx, 3, 1) # update done=1
                    except Exception as e:
                        logger.warning(f'exception during tweet! {e}')

        time.sleep(INTERVAL)

if __name__ == '__main__':
    main()
