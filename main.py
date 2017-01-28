from bs4 import BeautifulSoup
import urllib2
import twitter
import config
import logging
import os
import psycopg2
import urlparse
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()
log = logging.getLogger('apscheduler.executors.default')
log.setLevel(logging.INFO)  # DEBUG
fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
h = logging.StreamHandler()
h.setFormatter(fmt)
log.addHandler(h)


@sched.scheduled_job('interval', minutes=15)  # increasing this may have twitter rate-limit you
def check_tweets():
    api = twitter.Api(
            consumer_key=config.consumer_key,
            consumer_secret=config.consumer_secret,
            access_token_key=config.access_token_key,
            access_token_secret=config.access_token_secret
    )

    urlparse.uses_netloc.append("postgres")
    url = urlparse.urlparse(os.environ["DATABASE_URL"])

    try:
        conn = psycopg2.connect(
                database=url.path[1:],
                user=url.username,
                password=url.password,
                host=url.hostname,
                port=url.port
        )
    except:
        print "Cannot connect to db"

    url = "https://twitter.com/%s" % config.handle

    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page.read(), "html.parser")

    tweets = soup.find_all("div", class_="original-tweet")[:15]  # increasing this may have twitter rate-limit you
    tweets.reverse()

    cur = conn.cursor()

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
        cur.execute("SELECT * FROM tweets where tweet_id = '%s'" % tweet_id)
        if cur.rowcount:
            print "already exists"
        else:
            print "tweeting %s" % tweet_id
            try:
                api.PostUpdate(tweet_text)
                cur.execute("INSERT INTO tweets (tweet_id) VALUES (%s)" % tweet_id)
            except Exception, e:
                print tweet_text
                print "tweet failed: " + str(e)
        print "------------------"

    conn.commit()
    cur.close()
    conn.close()

sched.start()
#check_tweets()