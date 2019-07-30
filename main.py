# Document conference



# Imports

## Built-in packages
from pathlib import Path
from datetime import datetime as dt
import json

## External packages
import yaml, tweepy, progressbar

## Debug =======================================================================
from pprint import pprint
## =============================================================================

class _Setup():

    def __init__(self):
        with open('./setup.yml') as f: self.config = yaml.load(f)

        self._setup_folders()

    def __getitem__(self, i):
        return self.config[i]

    def _setup_folders(self, hashtag=None):
        hashtag_dir = Path("./__cache__") / self.config['conference']['hashtag'][1:]
        self.tweets_dir = hashtag_dir / "tweets"
        self.users_dir = hashtag_dir / "users"
        if not self.tweets_dir.is_dir(): self.tweets_dir.mkdir(parents=True)
        if not self.users_dir.is_dir(): self.users_dir.mkdir(parents=True)

class _TwitterCredentials():

    def __init__(self):
        with open('./credentials.yml') as f: self._ = yaml.load(f)

    def __getitem__(self, i):
        return self._[i]

twitter_credentials = _TwitterCredentials()

auth = tweepy.OAuthHandler(twitter_credentials['consumer_key'], twitter_credentials['consumer_secret'])
auth.set_access_token(twitter_credentials['access_token'], twitter_credentials['access_token_secret'])
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


class Conference(_Setup):
    def __init__(self):
        _Setup.__init__(self)
        # ...

    def __str__(self):
        return f"Conference({self.config['conference']['hashtag']})"


class TweetCollection(_Setup):

    def __init__(self, ids):
        _Setup.__init__(self)
        self.ids = ids
        self.tweets, self.errors = [], []
        bar = progressbar.ProgressBar(max_value=len(ids)).start() # start progressbar
        for i, id in enumerate(ids):
            bar.update(i)
            tweet = Tweet(id)
            if len(tweet._json) > 0: self.tweets.append(tweet)
            else: self.errors.append(f"Skipped tweet id {id} because its JSON was not not valid.")
        bar.finish()
        if len(self.errors) > 0:
            print("Errors:")
            for error in self.errors:
                print("-", error)

    def __getitem__(self, i):
        return self.tweets[i]

    def by(self, dateformat=None, key=None):
        _ = {}
        for tweet in self.tweets:
            if dateformat is not None: sorting=tweet.created_at.strftime(dateformat)
            if key is not None: sorting=tweet._json.get(key, None)

            if sorting not in _: _[sorting] = []
            _[sorting].append(tweet)
        return _




class Tweet(_Setup):

    def __init__(self, id, _json=None):
        _Setup.__init__(self)
        self.id = id
        self.linked_file = Path(self.tweets_dir / str(id))

        # If we don't have a file, follow this protocol
        if not self.linked_file.is_file():
            if _json is not None:
                # Manual JSON data was passed in so let's save that
                with self.linked_file.open(mode='w+') as f: json.dump(_json, f)
            else:
                # Download the tweet
                self.download(id)

        # Load the JSON from the file
        with self.linked_file.open(mode='r') as f: self._json = json.load(f)

        if len(self._json) > 0:
            # Set up shortcuts
            self.contributors = self._json['contributors']
            self.coordinates = self._json['coordinates']
            self.created_at = dt.strptime(self._json['created_at'], '%a %b %d %H:%M:%S %z %Y')
            self.display_text_range = self._json['display_text_range']
            self.entities = self._json['entities']
            self.favorite_count = self._json['favorite_count']
            self.favorited = self._json['favorited']
            self.full_text = self._json['full_text']
            self.geo = self._json['geo']
            self.in_reply_to_screen_name = self._json['in_reply_to_screen_name']
            self.in_reply_to_status_id = self._json['in_reply_to_status_id']
            self.in_reply_to_user_id = self._json['in_reply_to_user_id']
            self.is_quote_status = self._json['is_quote_status']
            self.lang = self._json['lang']
            self.place = self._json['place']

            self.retweet_count = self._json['retweet_count']
            self.retweeted = self._json['retweeted']
            self.source = self._json['source']
            self.truncated = self._json['truncated']

            try:    self.quoted_status_id = self._json['quoted_status_id']
            except: self.quoted_status_id = None # quoted status ID not found

            try:    self.quoted_status = Tweet(id=self._json['quoted_status']['id'], _json=self._json['quoted_status'])
            except: self.quoted_status = None # quoted status not found

            try: self.possibly_sensitive = self._json['possibly_sensitive']
            except: self.possibly_sensitive = None

            try: self.possibly_sensitive_appealable = self._json['possibly_sensitive_appealable']
            except: self.possibly_sensitive_appealable = None

            self.user = User(id=self._json['user']['id'], _json=self._json['user'])
        else:
            pass # we need a way to indicate that the tweet is not good...

    def download(self, id):
        # print(f"trying to download {id}")
        try:
            tweet = api.get_status(id, tweet_mode='extended')
            with self.linked_file.open(mode='w+') as f:
                json.dump(tweet._json, f)
        except tweepy.TweepError as e:
            print(f"error downloading {id}: {e}")
            with self.linked_file.open(mode='w+') as f:
                json.dump({}, f)


    def __str__(self):
        return self._json['full_text']

    def __repr__(self):
        return f"Tweet(id={self.id})"

    def __getitem__(self, i):
        return self._json[i]

class User(_Setup):

    def __init__(self, id, _json=None):
        _Setup.__init__(self)
        self.id = id
        self.linked_file = Path(self.users_dir / str(id))

        # If we don't have a file, follow this protocol
        if not self.linked_file.is_file():
            if _json is not None:
                # Manual JSON data was passed in so let's save that
                with self.linked_file.open(mode='w+') as f: json.dump(_json, f)
            else:
                # Download the tweet
                self.download(id)

        # print(f"User object! {self.linked_file}")

    def download(self, id):
        pass # print(f"trying to download {id}")

