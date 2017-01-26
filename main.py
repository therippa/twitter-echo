from bs4 import BeautifulSoup
from tinydb import TinyDB, Query
import urllib2
import twitter
import config
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=15)  # increasing this may have twitter rate-limit you
def check_tweets():
    db = TinyDB('db.json')

    api = twitter.Api(
            consumer_key=config.consumer_key,
            consumer_secret=config.consumer_secret,
            access_token_key=config.access_token_key,
            access_token_secret=config.access_token_secret,
    )

    url = "https://twitter.com/%s" % config.handle

    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page.read(), "html.parser")

    tweets = soup.find_all("div", class_="original-tweet")[:15]  # increasing this may have twitter rate-limit you
    tweets.reverse()
    existing = Query()

    for tweet in tweets:
        try:
            tweet.find("span", class_="tweet-poi-geo-text").extract()  # remove unnecessary geolocation element
        except:
            pass
        try:
            tweet.find("a", class_="u-hidden").extract()  # remove unnecessary element
        except:
            pass

        tweet_text = tweet.find("p", class_="tweet-text").get_text()[:140]  # parse 140 character if tweet is too long
        tweet_id = tweet.attrs["data-tweet-id"]
        print tweet_id
        if db.search(existing.id == tweet_id):
            print "already exists"
        else:
            print "tweeting " + tweet_id
            try:
                api.PostUpdate(tweet_text)
                db.insert({'id': tweet_id})
            except Exception, e:
                print tweet_text
                print "tweet failed: " + str(e)
        print "------------------"

sched.start()
