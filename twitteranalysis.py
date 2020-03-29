import json
import os
import math
import glob
import time
import re
import numpy as np
from collections import Counter 
import matplotlib.pyplot as plt
from pprint import pprint
from wordcloud import WordCloud
from bs4 import BeautifulSoup


MAJORKEYTHRESHOLD = 0.95
FILETWEETLIMIT = 10000
class TwitterAnalysis:
    def __init__(self,keyword):
        self.keyword = keyword
       
    def analyse_data(self):
        hashtagset= {}
        locationset= {}
        hashtagdump=[]
        usermentiondump=[]
        sourcedump = []
        tweetdata = []
        placedump =[]
        for filename in glob.glob("prepped/"+self.keyword.replace(" ", "_")+"_major*"):
            print("Loading"+filename)
            with open(filename, 'r') as json_file: 
                tweetdata += json.load(json_file)

        print(len(tweetdata))  
        for tweet in tweetdata:
            hashtagdump +=tweet['entities']['hashtags']
            usermentiondump += tweet['entities']['user_mentions']
            if tweet['place'] is not None :
                placedump.append(tweet['place']) 
            soup = BeautifulSoup(tweet['source'],features="html.parser")
            tag=soup.a
            sourcedump.append(tag.string)
        #pprint(placedump)
        #pprint(sourceset)
        hashtagset = Counter(hashtag['text'] for hashtag in hashtagdump)
        usermentionset = Counter(usermention['name'] for usermention in usermentiondump)
        sourceset = Counter(source for source in sourcedump)

        userset = Counter(tweet['user']['screen_name'] for tweet in tweetdata)
        locationset = Counter(tweet['user']['location'] for tweet in tweetdata)
        placeset = Counter(place['full_name'] for place in placedump)
        tweetdateset= Counter(time.strftime('%m-%d', time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y')) for tweet in tweetdata)
        locationset.pop('')
        tweettextset = " ".join(re.sub(re.compile(r'http\S+|#\S+|@\S+|\bRT\S+'),"",tweet["full_text"])  for tweet in tweetdata)
        '''
        print(min(tweetdateset.keys()))
        idx = pd.date_range(min(tweetdateset.keys()), max(tweetdateset.keys()))

        s = pd.Series(tweetdateset)
        s.index = pd.DatetimeIndex(s.index)

        s = s.reindex(idx, fill_value=0)
        print(s)
        '''

        fig, ax1 = plt.subplots()
        ax1.barh(*zip(*hashtagset.most_common(50)),align='center')
        ax1.set_xlabel('Number of Tweets')
        ax1.set_title('Top HashTags')
        plt.show()

        fig, ax1 = plt.subplots()
        ax1.barh(*zip(*placeset.most_common(50)),align='center')
        ax1.set_xlabel('Number of Tweets')
        ax1.set_title('Top Tagged Locations')
        plt.show()

        fig, ax1 = plt.subplots()
        ax1.barh(*zip(*locationset.most_common(50)),align='center')
        ax1.set_xlabel('Number of Tweets')
        ax1.set_title('Top Profile Locations')
        plt.show()

        fig, ax1 = plt.subplots()
        ax1.barh(*zip(*userset.most_common(50)),align='center')
        ax1.set_xlabel('Number of Tweets')
        ax1.set_title('Top Users')
        plt.show()

        fig, ax1 = plt.subplots()
        ax1.barh(*zip(*sourceset.most_common(10)),align='center')
        ax1.set_xlabel('Number of Tweets')
        ax1.set_title('Top Sources')
        plt.show()


        fig, ax1 = plt.subplots()
        ax1.plot(*zip(*sorted(tweetdateset.items())))
        ax1.xaxis.set_ticks(np.arange(1,len(tweetdateset),len(tweetdateset)/10))
        #ax1.yaxis.set_ticks(np.arange(1,20,1))
        ax1.set_xlabel('Number of Tweets')
        ax1.set_title('Date')
        plt.show()
        plt.figure()

        # Create the wordcloud object
        wordcloud = WordCloud(width=480, height=480, margin=0,max_words=100).generate_from_frequencies(hashtagset)
        
        # Display the generated image:
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.title("HashTags")
        plt.axis("off")
        plt.margins(x=0, y=0)
        plt.show()
        plt.figure()

        # Create the wordcloud object
        wordcloud = WordCloud(width=480, height=480, margin=0,max_words=100).generate_from_frequencies(usermentionset)
        
        # Display the generated image:
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.title("User Mentions")
        plt.axis("off")
        plt.margins(x=0, y=0)
        plt.show()
        plt.figure()


        # Create the wordcloud object
        wordcloud = WordCloud(width=480, height=480, margin=0,max_words=50).generate(tweettextset)
        
        # Display the generated image:
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.title("Words in Tweet")
        plt.axis("off")
        plt.margins(x=0, y=0)
        plt.show()