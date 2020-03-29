import argparse
from twittergather import TwitterGather
from twitteranalysis import TwitterAnalysis
from twitterprepare import TwitterPrepare
MAXTWEETCOUNT = 1000

def __main__():
    parser = argparse.ArgumentParser()

    parser.add_argument("command", help="Command",choices=["gather","prepare","analyze"])
    parser.add_argument("keyword", help="Keyword to gather data for")
    parser.add_argument(
        "--toptagcount", help="Number of latest tweets to check for toptag, multiples of 100", default=MAXTWEETCOUNT)
    parser.add_argument("--consumer_key", help="consumer_key used for API authentication", default=None)
    parser.add_argument("--consumer_secret", help="consumer_secret used for API authentication", default=None)


    args = parser.parse_args()

    if (args.command == "gather"):
        gatherobj = TwitterGather(args.keyword,consumer_key=args.consumer_key,consumer_secret=args.consumer_secret)
        gatherobj.process()
    elif (args.command == "prepare"):
        prepareobj = TwitterPrepare(args.keyword)
        prepareobj.prepare_data()
    elif (args.command == "analyze"):
        analyseobj = TwitterAnalysis(args.keyword)
        analyseobj.analyse_data()

__main__()
