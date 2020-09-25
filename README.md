# Tweet Client

Extract trending #hashtags ;-) on a user's timeline. Which user? The one whose credentials you pass as args when you execute the `tweet_client.py` script. 

So you have that script fetch the tweets and forwards them, one by one, to an Apache Spark Streaming backend script to make whatever use of them. This backend script extracts hashtags from these tweets, sends a count of the top 10 hashtags seen so far to an HBase instance. 

A `Flask` web application retrieves these top 10 hashtags and displays them graphically in a web browser. This can be used a widget wherever. Since this makes use of AJAX to poll for changes in hashtag counts, you can tweak the settings here, like how often to fetch the updates, etc.

Initially, the tweet client sent the tweets over a network socket to the backend, and the backend used a REST API to forward the hashtag counts to the Flask web front end. However, now, the tweet client sends the tweets to Kafka. The Spark Streaming backend picks them up, extracts the hashtags and writes the top 10 counts to HBase. The Flask web front end then reads these counts from HBase. 

### Setting up the environment

Before running the applications, you need to set up Apache [Spark](https://www.tutorialspoint.com/apache_spark/apache_spark_installation.htm), [Kafka](https://kafka.apache.org/quickstart) and [HBase](https://www.guru99.com/hbase-installation-guide.html). Both Kafka and HBase require Zookeeper to run. These applications in this case make use of different Zookeeper instances. In my case, these are all downloaded and extracted into the `/opt/` directory. Feel free to download and extract them anywhere within your filesystem.

#### Running HBase

Run the HBase start up script. 
```
/opt/hbase-2.2.5/bin/start-hbase.sh
```
HappyBase uses the Thrift interface to communicate with HBase. So make sure this interface is up and running.
```
/opt/hbase-2.2.5/bin/hbase-daemon.sh start thrift
```

Use `jps` to make sure both HBase and its Thrift interface are up and running correctly. You can also navigate to `http://localhost:16010` in your web browser to view the status of this HBase standalone instance.

Run the `hbase shell` and create the `hashtags` table that we shall use in the applications.

```
hbase(main):001:0> create 'hashtags', {NAME => 'hashtag'}
```

#### Running Kafka

Configure this Zookeeper instance to run on port 2182 (clientPort in `zookeeper.properties`) and then run it:
```
/opt/kafka_2.13-2.6.0/bin/zookeeper-server-start.sh config/zookeeper.properties
```

Then, run the Kafka server on the default port - 9092:
```
/opt/kafka_2.13-2.6.0/bin/kafka-server-start.sh config/server.properties
```

There's no need to create the topic we shall use as the producer creates it if it does not find it.

### Running the applications

#### Fetch tweets
Initially, the `tweet_client.py` script forwarded the tweets over a TCP Socket to the backend script. The backend script always had issues if there was nothing to read on the socket. So the order in which the scripts run mattered. 

However, now the `tweet_client.py` writes the tweets to a Kafka broker, so it doesn't matter anymore which of the two runs first.

Execute the tweet client script:
```
python tweet_client.py <CONSUMER_KEY> <CONSUMER_SECRET> <ACCESS_TOKEN> <ACCESS_SECRET>
```

#### Extract hashtags
Since it uses Apache Spark streaming while consuming from the Kafka broker, we do not run this directly, but rather submit it to a Spark cluster (even if it is a local cluster in standalone mode). So to execute the backend script:
```
spark-submit --jars lib/spark-streaming-kafka-0-8-assembly_2.11-2.4.7.jar spark_handler.py
```

You can navigate to `http://your_ip_address:4040` in your web browser to view the status of the Spark job, the executors running, etc.

#### Visualize hashtag counts
To run the `Flask` application:
```
python app.py
```

Navigate to `http://localhost:5001` in a web browser for a visualization of the hashtag counts.

### Acknowledgements

Just in case you were wondering why all of this looked awfully familiar, [here](https://www.toptal.com/apache/apache-spark-streaming-twitter) is what is the backbone of this project. 

### Further references

* [HBase Installation](https://www.guru99.com/hbase-installation-guide.html)
* [HappyBase](https://happybase.readthedocs.io/en/latest/)
* [HBase Thrift Interface](https://blog.cloudera.com/how-to-use-the-hbase-thrift-interface-part-1/)
* [Kafka with Python](https://towardsdatascience.com/kafka-python-explained-in-10-lines-of-code-800e3e07dad1)
* [Spark Streaming Kafka Integration](https://spark.apache.org/docs/2.1.0/streaming-kafka-0-8-integration.html)
* [Streaming Samples](https://github.com/apache/spark/blob/v2.1.0/examples/src/main/python/streaming/kafka_wordcount.py)
* [Flask](https://flask.palletsprojects.com/en/1.1.x/)
* [Chart.js](https://flask.palletsprojects.com/en/1.1.x/)