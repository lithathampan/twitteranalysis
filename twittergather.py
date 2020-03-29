from twitterapi import TwitterApi
from pprint import pprint
from collections import Counter
import json
import os
import urllib
import time
import sys

MAXTWEETCOUNT = 1000
BATCHCOUNT = 100
TOPTAGCOUNT = 10
FREQUENCYTHRESHOLD = 10
RELEVANCETHRESHOLD = 0.1
FORGETAFTERNDUMP = 10

class TwitterGather:
    def __init__(self,keyword,consumer_key=None,consumer_secret=None):
        self.keyword = keyword
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret 



    def gather_tweets(self,keyword, specialflag="", maxtweetcount=MAXTWEETCOUNT, max_id=None, since_id=0,main_max_id = None):
        gatheredtweets = []
        gathered = 0
        queriedcount = BATCHCOUNT
        next_since_id = since_id
        if main_max_id:
            max_id = main_max_id
        api = TwitterApi(consumer_key=self.consumer_key,
                        consumer_secret=self.consumer_secret)
        while (gathered < maxtweetcount) and (queriedcount == BATCHCOUNT):
            if api.get_remaining_limit().remaining > 0:
                # print("Gathered so far:"+str(gathered))
                result = api.search(
                    keyword=keyword, count=BATCHCOUNT, specialflag=specialflag, max_id=max_id, since_id=since_id)
                if max_id is None or main_max_id:
                    next_since_id = result['search_metadata']['max_id']
                    #print("New Since ID:"+str(next_since_id))

                # pprint(result)
                # pprint(result['search_metadata'])
                queriedcount = len(result['statuses'])
                # pprint(len(result['statuses']))
                if queriedcount > 1:
                    next_results = result['search_metadata']['next_results']
                    max_id = int(
                        dict(urllib.parse.parse_qsl(next_results[1:]))['max_id'])
                # print(max_id)
                gathered += queriedcount
                gatheredtweets += result["statuses"]
            else:
                print("Rate Limit Exceeded.Try Again Later!!")
                pprint(api.get_remaining_limit())
                sys.stdout.flush()
                while(api.get_remaining_limit().remaining == 0):
                    print("Rate Limit Exceeded.Trying again after 30 sec")
                    time.sleep(30)
                    api = TwitterApi(consumer_key=self.consumer_key,
                                    consumer_secret=self.consumer_secret)
        next_max_id = max_id
        return {"next_since_id": next_since_id, "next_max_id": next_max_id, "gatheredtweets": gatheredtweets}


    def search_meta(self,searchword, current_meta, specialflag=""):
        if current_meta:
            for search_entry in current_meta['relevant_searchwords']:
                if search_entry['word'] == searchword and search_entry['specialflag'] == specialflag:
                    return search_entry
        return None


    def gather_data(self,metaentry, searchword, specialflag="", main_max_id=None):
        idranges = []
        dump_counter = 1
        if metaentry:
            idranges = metaentry["idranges"]
            if len(idranges) == 1:
                if idranges[0][0] > 0:
                    print("Gathering older tweets")
                    gatherresult = self.gather_tweets(
                        keyword=searchword, max_id=idranges[0][0], specialflag=specialflag)
                    gatheredtweets = gatherresult["gatheredtweets"]
                    if len(gatheredtweets) == MAXTWEETCOUNT:
                        idranges[0][0] = gatherresult["next_max_id"]
                    else:
                        idranges[0][0] = 0
                else:
                    print("Gathering latest tweets")
                    gatherresult = self.gather_tweets(
                        keyword=searchword, since_id=idranges[0][1], specialflag=specialflag)
                    gatheredtweets = gatherresult["gatheredtweets"]
                    if len(gatheredtweets) == MAXTWEETCOUNT:
                        idranges.append(
                            [gatherresult["next_max_id"], gatherresult["next_since_id"]])
                    else:
                        idranges[0][1] = gatherresult["next_since_id"]

            elif len(idranges) == 2:
                print("Bridging the gap")
                gatherresult = self.gather_tweets(
                    keyword=searchword, since_id=idranges[0][1], max_id=idranges[1][0], specialflag=specialflag)
                gatheredtweets = gatherresult["gatheredtweets"]
                if len(gatheredtweets) == MAXTWEETCOUNT:
                    idranges[1][0] = gatherresult["next_max_id"]
                else:
                    idranges[0][1] = idranges[1][1]
                    idranges.pop()
            else:
                print("Corrupt Meta")
                exit()
                # merge_idrange()
            dump_counter = metaentry["dump_counter"] + 1
        else:
            print("First Time Gather")
            if main_max_id:
                print("Gathering previous to:" + str(main_max_id))
            gatherresult = self.gather_tweets(
                keyword=searchword, main_max_id=main_max_id, specialflag=specialflag)
            gatheredtweets = gatherresult["gatheredtweets"]
            if len(gatheredtweets) == MAXTWEETCOUNT:
                idranges.append([gatherresult["next_max_id"],
                                gatherresult["next_since_id"]])
            else:
                idranges.append([0, gatherresult["next_since_id"]])
        return {'gatheredtweets': gatheredtweets, 'idranges': idranges, 'dump_counter': dump_counter}


    def dump_tweets(self,dump_counter, keyword, searchword, tweetdata):
        datafilename = "data/" + \
            keyword.replace(" ", "_")+"_"+searchword.replace(" ",
                                                            "_")+"_"+str(dump_counter)+".json"
        if not os.path.exists('data'):
            os.makedirs('data')
        if len(tweetdata) > 0:
            with open(datafilename, 'w') as datafile:
                json.dump(tweetdata, datafile)
            return datafilename
        else:
            return None


    def get_relevant_searchwords(self,keyword, current_meta):
        relevant_searchwords = []
        hashtagdump = []
        usermentiondump = []
        idranges = []
        dump_files = []
        main_max_id = None
        metaentry = self.search_meta(keyword, current_meta, "")
        if metaentry:
            totaltweets = metaentry['totaltweets']
            strength = metaentry['strength']
            dump_files = metaentry['dump_files']
            if len(metaentry['idranges']) == 2:
                main_max_id = metaentry['idranges'][1][0]
            else:
                main_max_id = metaentry['idranges'][0][0]
        else:
            strength = 1
            totaltweets = 0
        gatheredtweets = []
        '''
        if metaentry:
            next_max_id = metaentry['next_max_id']
            next_since_id = metaentry['next_since_id']
        
        pprint(metaentry)
        '''
        gather_data_result = self.gather_data(metaentry, keyword)
        gatheredtweets = gather_data_result['gatheredtweets']
        idranges = gather_data_result['idranges']
        dump_counter = gather_data_result['dump_counter']
        dump_filename = self.dump_tweets(dump_counter, keyword, keyword, gatheredtweets)
        if dump_filename:
            dump_files.append(dump_filename)
        searchwordentry = {"specialflag": "",
                        "word": keyword,
                        "relevance": 1.0,
                        "strength": (strength*(dump_counter-1)*MAXTWEETCOUNT+len(gatheredtweets))/(dump_counter*MAXTWEETCOUNT),
                        "totaltweets": totaltweets+len(gatheredtweets),
                        "idranges": idranges,
                        "dump_counter": dump_counter,
                        "dump_files": dump_files
                        }
        pprint(searchwordentry)
        relevant_searchwords.append(searchwordentry)
        main_dumpcounter = dump_counter
        main_dump_files = dump_files

        maindumptweets = []

        for dumpfilename in main_dump_files[-FORGETAFTERNDUMP:]:
            with open(dumpfilename, 'r') as dumpfile:
                maindumptweets += json.load(dumpfile)

        for tweet in maindumptweets:
            hashtagdump += tweet['entities']['hashtags']
            usermentiondump += tweet['entities']['user_mentions']
        # pprint(usermentiondump)
        hashtagset = Counter(hashtag['text'] for hashtag in hashtagdump)
        usermentionset = Counter(usermention['screen_name']
                                for usermention in usermentiondump)
        # pprint(hashtagset.most_common(10))
        print("Gathered Tweets on keyword:"+str(len(maindumptweets)))
        tophashtags = hashtagset.most_common(TOPTAGCOUNT)
        topusermentions = usermentionset.most_common(TOPTAGCOUNT)

        pprint(tophashtags)
        pprint(topusermentions)

        for hashtag, count in tophashtags:
            idranges = []
            dump_files = []
            metaentry = self.search_meta(hashtag, current_meta, specialflag='#')
            if metaentry:
                totaltweets = metaentry['totaltweets']
                strength = metaentry['strength']
                dump_files = metaentry['dump_files']
                existingrelevance = metaentry['relevance']
            else:
                strength = 1
                totaltweets = 0
                existingrelevance = 0
            if count >= FREQUENCYTHRESHOLD * min(main_dumpcounter,FORGETAFTERNDUMP):
                hashtagrelevance = 0
                gather_data_result = self.gather_data(
                    metaentry, hashtag, specialflag="#", main_max_id=main_max_id)
                gatheredtweets = gather_data_result['gatheredtweets']
                for tweet in gatheredtweets:
                    if keyword in tweet['full_text']:
                        hashtagrelevance += 1
                print("Hashtag:"+hashtag+":"+str(hashtagrelevance) +
                    "/"+str(len(gatheredtweets)))
                if len(gatheredtweets) > 0:
                    if hashtagrelevance/len(gatheredtweets) > RELEVANCETHRESHOLD:
                        idranges = gather_data_result['idranges']
                        dump_counter = gather_data_result['dump_counter']
                        dump_filename = self.dump_tweets(
                            dump_counter, keyword, '#'+hashtag, gatheredtweets)
                        if dump_filename:
                            dump_files.append(dump_filename)
                        searchwordentry = {"specialflag": "#",
                                        "word": hashtag,
                                        "relevance": (existingrelevance*totaltweets+hashtagrelevance)/(totaltweets+len(gatheredtweets)),
                                        "strength":  (strength*(dump_counter-1)*MAXTWEETCOUNT+len(gatheredtweets))/(dump_counter*MAXTWEETCOUNT),
                                        "totaltweets": totaltweets+len(gatheredtweets),
                                        "idranges": idranges,
                                        "dump_counter": dump_counter,
                                        "dump_files": dump_files
                                        }
                        relevant_searchwords.append(searchwordentry)

        for usermention, count in topusermentions:
            idranges = []
            dump_files = []
            metaentry = self.search_meta(usermention, current_meta, specialflag="@")
            if metaentry:
                totaltweets = metaentry['totaltweets']
                strength = metaentry['strength']
                dump_files = metaentry['dump_files']
                existingrelevance = metaentry['relevance']
            else:
                strength = 1
                totaltweets = 0
                existingrelevance = 0
            if count >= FREQUENCYTHRESHOLD * min(main_dumpcounter,FORGETAFTERNDUMP):
                usermentionrelevance = 0
                gather_data_result = self.gather_data(
                    metaentry, usermention, specialflag="@", main_max_id=main_max_id)
                gatheredtweets = gather_data_result["gatheredtweets"]
                for tweet in gatheredtweets:
                    if keyword in tweet['full_text']:
                        usermentionrelevance += 1
                print("UserMention:"+usermention+":"+str(usermentionrelevance) +
                    "/"+str(len(gatheredtweets)))
                if len(gatheredtweets) > 0:
                    if usermentionrelevance/len(gatheredtweets) > RELEVANCETHRESHOLD:
                        idranges = gather_data_result['idranges']
                        dump_counter = gather_data_result['dump_counter']
                        dump_filename = self.dump_tweets(
                            dump_counter, keyword, '@'+usermention, gatheredtweets)
                        if dump_filename:
                            dump_files.append(dump_filename)
                        searchwordentry = {"specialflag": "@",
                                        "word": usermention,
                                        "relevance": (existingrelevance*totaltweets+usermentionrelevance)/(totaltweets+len(gatheredtweets)),
                                        "strength": (strength*(dump_counter-1)*MAXTWEETCOUNT+len(gatheredtweets))/(dump_counter*MAXTWEETCOUNT),
                                        "totaltweets": totaltweets+len(gatheredtweets),
                                        "idranges": idranges,
                                        "dump_counter": dump_counter,
                                        "dump_files": dump_files
                                        }
                        relevant_searchwords.append(searchwordentry)
        return relevant_searchwords


    def process(self):

        metafilename = "meta/"+self.keyword.replace(" ", "_")+".meta"

        current_meta = None
        if os.path.isfile(metafilename):
            with open(metafilename, 'r') as metafile:
                current_meta = json.load(metafile)

        relevant_searchwords = self.get_relevant_searchwords(
            keyword=self.keyword, current_meta=current_meta)
        searchwordlist = [searchword['specialflag']+searchword['word']
                        for searchword in relevant_searchwords]

        if current_meta:
            for curr_searchword in current_meta['relevant_searchwords']:
                if curr_searchword['specialflag']+curr_searchword['word'] not in searchwordlist:
                    relevant_searchwords.append(curr_searchword)

        metadata = {
            "metagmttime": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
            "metakeyword": self.keyword,
            "relevant_searchwords": relevant_searchwords
        }
        pprint(metadata)
        if not os.path.exists('meta'):
            os.makedirs('meta')
        with open(metafilename, 'w') as metafile:
            json.dump(metadata, metafile)

