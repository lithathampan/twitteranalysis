import twitter
import os

class TwitterApi:
    def __init__(self,
                 consumer_key,
                 consumer_secret,
                 application_only_auth=True,
                 tweet_mode="extended"):
        if consumer_key is None:
            consumer_key = os.getenv('TWITTERKEY','NOTDEFINED')        
        if consumer_secret is None:
            consumer_secret = os.getenv('TWITTERSECRET','NOTDEFINED')
        if consumer_key=='NOTDEFINED' or consumer_secret=='NOTDEFINED':
            raise RuntimeError("Please pass Twitter API credentials as argument or environmental variable")
        
        self.api=twitter.Api(consumer_key=consumer_key,       
                               consumer_secret=consumer_secret,
                               application_only_auth=application_only_auth,
                               tweet_mode=tweet_mode)
        self.callcounter = 0

    def search(self, keyword="test", specialflag="", since_id=0, max_id=None, lang="en", count=100):
        specialflag_dict = {"@" : "%40", "#" : "%23", "" : ""}
        keyword = specialflag_dict[specialflag]+keyword
        #print("Searching:"+keyword)
        self.callcounter += 1
        max_id_string = "&max_id="+str(max_id) if max_id else ""
        return self.api.GetSearch(raw_query="q="+keyword+"&count="+str(count)+"&since_id="+str(since_id)+max_id_string+"&lang="+lang+"", return_json=True)

    def get_remaining_limit(self):
        return self.api.CheckRateLimit("https://api.twitter.com/1.1/search/tweets.json")
