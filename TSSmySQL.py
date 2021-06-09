import mysql.connector
from mysql.connector import Error
import os
import json
import praw
import time
import tweepy
from datetime import datetime
from pytz import timezone
from unidecode import unidecode
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import config


analyzer = SentimentIntensityAnalyzer()

track = ['Tsla']

consumer_key = config.consumer_key
consumer_secret = config.consumer_secret
access_token = config.access_token
access_token_secret = config.access_token_secret
password = config.password


def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset


#### We will be adding to the ib db instead ##########
######################################################

#gets the time from the main database 
def getTime():
    date = []
    try:
        con = mysql.connector.connect(
        host = 'localhost',
        database='twitterdb', 
        user='root', 
        password = config.password)

        cursor = con.cursor()
        query = "select * from TwitterSent"
        cursor.execute(query)
        # get all records
        db = cursor.fetchall()

        df = pd.DataFrame(db)

        date.append(df[0].iloc[-1])
        date.append(df[0].iloc[-2])


    except mysql.connector.Error as e:
        print("Error reading data from MySQL table", e)

    cursor.close()
    con.close()

    return date


def connect(timestamp_ms, sentiment):
	"""
	connect to MySQL database and insert twitter data
	"""
	try:
		con = mysql.connector.connect(
		host = 'localhost',
		database='twitterdb', 
		user='root', 
		password = password)
		print("You are connected to mySQL")
		

		if con.is_connected():
			"""
			Insert twitter data
			"""
			cursor = con.cursor()
			# twitter
			query = "INSERT INTO TwitterSent (timestamp_ms, sentiment) VALUES (%s, %s)"
			cursor.execute(query, (timestamp_ms, sentiment))
			con.commit()
			
			
	except Error as e:
	
		print(e)

	cursor.close()
	con.close()

	return


#will add a list class that will allow us to modify it from the outside

class MyList(object):

  def __init__(self):
    self.word_list = []

  def append(self, sent):
  	self.word_list.append(sent)

  def clear(self):
  	self.word_list = []

  def show(self):
  	print(self.word_list)

  	return 


# Tweepy class to access Twitter API
class Streamlistener(tweepy.StreamListener):
	

	def on_connect(self):
		print("You are connected to the Twitter API")


	def on_error(self):
		if status_code != 200:
			print("error found")
			# returning false disconnects the stream
			return False

	"""
	This method reads in tweet data as Json
	and extracts the data we want.
	"""
	def on_data(self,data):
		
		myList = MyList()

		try:
			data = json.loads(data)

			if 'truncated' not in data:
				return True
			if data['truncated']:
				tweet = unidecode(data['extended_tweet']['full_text'])
			else:
				tweet = unidecode(data['text'])

			#Takes in string stream data and converts it into a different format
			timestamp_ms = datetime.strftime(datetime.strptime(data['created_at'], '%a %b %d %H:%M:%S +0000 %Y'), '%Y-%m-%d %H:%M:%S')
			#converts it back into a datetime object to pass it through datetime_from_utc_to_local
			timestamp_ms = datetime.strptime(timestamp_ms, '%Y-%m-%d %H:%M:%S')
			#run it through the created method
			timestamp_ms = datetime_from_utc_to_local(timestamp_ms)


			tweet = data['text']

			# add in a part where it will only add the combined sentiment to the mysql db

			# check if that the minute changes then
			# if it changes, then we combine all of our data and then package it into a mysql db
			# and then push it off to the main db
			# clear the list that stores it

			# if it doesnt change, we keep appending to the list


			myList.append("hello")
			myList.append("yeur")
			myList.show()


			vs = analyzer.polarity_scores(tweet)
			sentiment = vs['compound']



			#insert data just collected into MySQL database
			connect(timestamp_ms, sentiment)
			print("Tweet collected at: {} ".format(str(timestamp_ms)))
		except Error as e:
			print(e)

def main():

	# authentification so we can access twitter
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api =tweepy.API(auth, wait_on_rate_limit=True)

	# create instance of Streamlistener
	listener = Streamlistener(api = api)
	stream = tweepy.Stream(auth, listener = listener)

	#track = ['nba', 'cavs', 'celtics', 'basketball']
	# choose what we want to filter by
	stream.filter(track = track, languages = ['en'])


if __name__== '__main__':
	main()