# Tweet Client

Extract trending #hashtags (;-) on the user's timeline. Which user? The one who credentials you pass to the `tweet_client.py` file. 

So you have that script fetch the tweets and forwards them, one by one, to a backend script to make whatever use of them. The backend script then extracts hashtags from these tweets, sends a count of the top 10 hashtags seen so far to an HBase database. 

A simple `Flask` web application is then used to retrieve the top 10 hashtags and view them graphically in a web browser. This can be used a widget wherever. Since this makes use of AJAX to poll for changes in hashtag counts, you can tweak the settings here, like how often to fetch the updates, etc.

### Running the applications

Initially, the `tweet_client.py` script forwarded the tweets over a TCP Socket to the backend script. The backend script always had issues if there was nothing to read on the socket. So the order in which the scripts run mattered. 

However, now the `tweet_client.py` writes the tweets to a Kafka broker, so it doesn't matter anymore which of the two runs first.

Execute the tweet client script:
```
python tweet_client.py <CONSUMER_KEY> <CONSUMER_SECRET> <ACCESS_TOKEN> <ACCESS_SECRET>
```

Since it uses Apache Spark streaming while consuming from the Kafka broker, we do not run this directly, but rather submit it to a Spark cluster (even if it is a local cluster in standalone mode). So to execute the backend script:
```
spark-submit --jars lib/spark-streaming-kafka-0-8-assembly_2.11-2.4.7.jar spark_handler.py
```


### Acknoledgement

Just in case you were wondering why all of this looked awfully familiar, [here](https://www.toptal.com/apache/apache-spark-streaming-twitter) is what is the backbone of this project. 

### Further references

* [HBase Installation](https://www.guru99.com/hbase-installation-guide.html)
* [HappyBase](https://happybase.readthedocs.io/en/latest/)
* [HBase Thrift Interface](https://blog.cloudera.com/how-to-use-the-hbase-thrift-interface-part-1/)
* [Kafka with Python](https://towardsdatascience.com/kafka-python-explained-in-10-lines-of-code-800e3e07dad1)
* [Spark Streaming Kafka Integration](https://spark.apache.org/docs/2.1.0/streaming-kafka-0-8-integration.html)
* [Streaming Samples](https://github.com/apache/spark/blob/v2.1.0/examples/src/main/python/streaming/kafka_wordcount.py)
