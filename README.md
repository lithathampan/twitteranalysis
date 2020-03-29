# twitteranalysis
Python application to gather and analyse twitter data based on keyword

## Prerequisites

* A Twitter API Account
* Python 3.8 or higher

## Setting up the Environment


* Run following to install the dependencies

```bash
pip install -r requirements.txt
```

*  (Optional) In Linux, Run the following for setting up the environment variable. This can be written as a shell script to be executed prior to running the data gather. In Windows, use set command to perform the same action. These environment variables are optional as the same can be passed as parameters while running the application.



```bash
export TWITTERKEY=<YourConsumerKey>
export TWITTERSECRET=<YouConsurmerSecret>
```

## Usage

```bash
python twitterapp.py [-h] [--consumer_key CONSUMER_KEY] [--consumer_secret CONSUMER_SECRET] {gather,prepare,analyze} keyword  

positional arguments:
  {gather,prepare,analyze}  Command
  keyword                   Keyword to gather data 

optional arguments:
  -h, --help            show this help message and exit

  --consumer_key CONSUMER_KEY
                        consumer_key used for API authentication
  --consumer_secret CONSUMER_SECRET
                        consumer_secret used for API authentication
```

## Development Envrionment

A virtual environment is created using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) to keep the specific python version and modules.

```bash
mkvirtualenv -p python3.8 twitteranalysis
```


