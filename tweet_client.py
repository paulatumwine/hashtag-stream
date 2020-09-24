import sys
import requests
import requests_oauthlib
import json
from kafka import KafkaProducer
from json import dumps

"""
bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic hashtags
"""
kafka_host = "localhost:9092"

def get_tweets():
    print "DEBUG: ", str(sys.argv)
    my_auth = requests_oauthlib.OAuth1(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    url = 'https://stream.twitter.com/1.1/statuses/filter.json'
    query_data = [('language', 'en'), ('locations', '-130,-20,100,50'), ('track', '#')]
    query_url = url + '?' + '&'.join([str(t[0]) + '=' + str(t[1]) for t in query_data])
    response = requests.get(query_url, auth=my_auth, stream=True)
    print(response)
    print(query_url, response)
    return response


def send_tweets_to_spark(http_resp):
    for line in http_resp.iter_lines():
        try:
            full_tweet = json.loads(line)
            tweet_text = full_tweet['text']
            print("DEBUG: sending to Kafka - " + tweet_text)
            # tcp_connection.send(tweet_text + '\n')
            producer.send("hashtags", value=tweet_text)
        except:
            e = sys.exc_info()[1]
            print("ERROR: %s" % e)


producer = KafkaProducer(bootstrap_servers=[kafka_host],
                         value_serializer=lambda x: dumps(x).encode("utf-8"))

# TCP_IP = "localhost"
# TCP_PORT = 9009
# conn = None
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.bind((TCP_IP, TCP_PORT))
# s.listen(1)
# print("Waiting for TCP connection...")
# conn, addr = s.accept()

print("Connected! Getting tweets...")
resp = get_tweets()
send_tweets_to_spark(resp)
