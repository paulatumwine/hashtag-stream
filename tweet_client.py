import socket
import sys
import requests
import requests_oauthlib
import json


def get_tweets():
	print "DEBUG: " , str(sys.argv)
	my_auth = requests_oauthlib.OAuth1(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
	url = 'https://stream.twitter.com/1.1/statuses/filter.json'
	query_data = [('language', 'en'), ('locations', '-130,-20,100,50'), ('track','#')]
	query_url = url + '?' + '&'.join([str(t[0]) + '=' + str(t[1]) for t in query_data])
	response = requests.get(query_url, auth=my_auth, stream=True)
	print(response)
	print(query_url, response)
	return response


def send_tweets_to_spark(http_resp, tcp_connection):
	for line in http_resp.iter_lines():
		try:
			full_tweet = json.loads(line)
			tweet_text = full_tweet['text']
			print("DEBUG: " + tweet_text)
			print ("------------------------------------------")
			tcp_connection.send(tweet_text + '\n')
		except:
			e = sys.exc_info()[1]
			print("ERROR: %s" % e)


TCP_IP = "localhost"
TCP_PORT = 9009
conn = None
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
print("Waiting for TCP connection...")
conn, addr = s.accept()
print("Connected! Getting tweets...")
resp = get_tweets()
send_tweets_to_spark(resp, conn)
