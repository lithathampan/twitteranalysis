import json
import os
import glob
from pprint import pprint


MAJORKEYTHRESHOLD = 0.95
FILETWEETLIMIT = 10000
class TwitterPrepare:
    def __init__(self,keyword):
        self.keyword = keyword

    def prepare_data(self):
        metafilename = "meta/"+self.keyword.replace(" ", "_")+".meta"
        if not os.path.exists('prepped'):
            os.makedirs('prepped')
        fulldatafilename = "prepped/"+self.keyword.replace(" ", "_")+"_full.json"
        majordatafilename = "prepped/"+self.keyword.replace(" ", "_")+"_major.json"
        tweetidlist = []
        current_meta = None
        if os.path.isfile(metafilename):
            with open(metafilename, 'r') as metafile:
                current_meta = json.load(metafile)
        else:
            raise FileNotFoundError("Meta Files Missing. Please gather some data before analysing")
        
        max_dumpcounter = max([curr_searchword['dump_counter'] for curr_searchword in current_meta['relevant_searchwords']])

        majorsearchwords = []
        for curr_searchword in current_meta['relevant_searchwords']:
            if curr_searchword['dump_counter'] >= max_dumpcounter * MAJORKEYTHRESHOLD :
                majorsearchwords.append(curr_searchword)
        pprint(majorsearchwords)
        relevant_startid = max([searchword['idranges'][0][0] for searchword in majorsearchwords])
        relevant_endid = min([searchword['idranges'][0][1] for searchword in majorsearchwords])

        print(relevant_startid)
        print(relevant_endid)
        fftweetcounter = 0
        fullfilelist = []
        mjtweetcounter = 0
        majorfilelist = []
        for preppedfile in glob.glob('prepped/'+self.keyword.replace(" ", "_")+'*'):
            print("removing"+preppedfile)
            os.remove(preppedfile)
        for curr_searchword in current_meta['relevant_searchwords']:
            for dumpfile in curr_searchword['dump_files']:
                with open(dumpfile ,'r') as filehandle:
                    print("Working with"+dumpfile)
                    tweetlist = json.load(filehandle)
                    for tweet in tweetlist:
                        if tweet['id'] not in tweetidlist:
                            fftweetcounter+=1
                            tweetidlist.append(tweet['id'])
                            fullfilelist.append(tweet)
                            if fftweetcounter % FILETWEETLIMIT == 0:
                                with open(fulldatafilename.replace('.','_'+str(int(fftweetcounter / FILETWEETLIMIT))+'.'), 'w') as fullfile:
                                    json.dump(fullfilelist,fullfile)
                                    print("Dumping "+fulldatafilename.replace('.','_'+str(int(fftweetcounter / FILETWEETLIMIT))+'.'))
                                fullfilelist = []
                            if tweet['id'] >= relevant_startid and tweet['id'] <= relevant_endid:
                                mjtweetcounter+=1
                                majorfilelist.append(tweet)
                                if mjtweetcounter % FILETWEETLIMIT == 0:
                                    with open(majordatafilename.replace('.','_'+str(int(mjtweetcounter / FILETWEETLIMIT))+'.'), 'w') as majorfile:
                                        json.dump(majorfilelist,majorfile)
                                    print("Dumping "+majordatafilename.replace('.','_'+str(int(mjtweetcounter / FILETWEETLIMIT))+'.'))
                                    majorfilelist = []
                                    
        with open(fulldatafilename.replace('.','_'+str(fftweetcounter / FILETWEETLIMIT)+'.'), 'w') as fullfile:
            json.dump(fullfilelist,fullfile)
        print("Dumping "+fulldatafilename.replace('.','_'+str(fftweetcounter / FILETWEETLIMIT)+'.'))
        with open(majordatafilename.replace('.','_'+str(mjtweetcounter / FILETWEETLIMIT)+'.'), 'w') as majorfile:
            json.dump(majorfilelist,majorfile)
        print("Dumping "+majordatafilename.replace('.','_'+str(mjtweetcounter / FILETWEETLIMIT)+'.'))