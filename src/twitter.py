if (__name__ == "__main__"):
	exit(1)

import json
import tweepy

api = None

def connect():
	global api
	creds = json.loads(open("./creds.json").read())
	auth = tweepy.OAuthHandler(
		creds['twitter']['consumerKey'], 
		creds['twitter']['consumerSecret']
	)
	auth.set_access_token(
		creds['twitter']['accessToken'], 
		creds['twitter']['accessTokenSecret']
	)
	api = tweepy.API(auth)
	api.verify_credentials()

def tweet(text, media=None):
	if (media):
		media = api.media_upload(media)
		return api.update_status(status=text, media_ids=[media.media_id])
	else:
		return api.update_status(status=text)