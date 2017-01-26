# twitter-echo
Useful for archiving other twitter feeds from despot heads of state.  Also useful for not inflating their followers count, if that is super important to them.

## Instructions
1. Clone the repo
2. Copy **config.sample.py** to **config.py** and fill in your info [Twitter Apps](https://apps.twitter.com/) info for the various keys/secrets
3. Deploy to heroku, making sure to [scale the clock task](https://devcenter.heroku.com/articles/clock-processes-python)
