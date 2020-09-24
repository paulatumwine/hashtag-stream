from pyspark import SparkConf, SparkContext
from pyspark.streaming import StreamingContext
from pyspark.sql import Row, SQLContext
import sys
import requests
import happybase
from kafka import KafkaConsumer
from json import loads

batch_size = 10
host = "localhost"
table_name = "hashtags"
kafka_host = "localhost:9092"


def aggregate_tags_count(new_values, total_sum):
    return sum(new_values) + (total_sum or 0)


def get_sql_context_instance(spark_context):
    if ('sqlContextSingletonInstance' not in globals()):
        globals()['sqlContextSingletonInstance'] = SQLContext(spark_context)
    return globals()['sqlContextSingletonInstance']


def process_rdd(time, rdd):
    print("----------- %s -----------" % str(time))
    try:
        sql_context = get_sql_context_instance(rdd.context)
        row_rdd = rdd.map(lambda w: Row(hashtag=w[0], hashtag_count=w[1]))
        hashtags_df = sql_context.createDataFrame(row_rdd)
        hashtags_df.registerTempTable("hashtags")
        hashtag_counts_df = sql_context.sql(
            "select hashtag, hashtag_count from hashtags order by hashtag_count desc limit 10")
        hashtag_counts_df.show()
        # send_df_to_dashboard(hashtag_counts_df)
        save_to_hbase(hashtag_counts_df)
    except:
        e = sys.exc_info()[1]
        print("ERROR: %s" % e)


def send_df_to_dashboard(df):
    top_tags = [str(t.hashtag) for t in df.select("hashtag").collect()]
    tags_count = [p.hashtag_count for p in df.select("hashtag_count").collect()]
    url = 'http://localhost:5001/updateData'
    request_data = {'label': str(top_tags), 'data': str(tags_count)}
    response = requests.post(url, data=request_data)


def connect_to_hbase():
    conn = happybase.Connection(host=host)
    conn.open()
    # conn.create_table(table_name)
    table = conn.table(table_name)
    return conn, table


def save_to_hbase(df):
    connection, table = connect_to_hbase()
    try:
        row_key = 0
        for h in df.collect():
            print("DEBUG: key: %s, value: %s" % (h.hashtag, h.hashtag_count))
            table.put(str(row_key), {"hashtag:name": str(h.hashtag), "hashtag:count": str(h.hashtag_count)})
            row_key += 1
    except:
        e = sys.exc_info()[1]
        print("ERROR: %s" % e)


consumer = KafkaConsumer(
    "hashtags",
    bootstrap_servers=[kafka_host],
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="my-group",
    value_deserializer=lambda x: loads(x.decode("utf-8")))

conf = SparkConf()
conf.setAppName("SparkHandler")
sc = SparkContext(conf=conf)
sc.setLogLevel("ERROR")
ssc = StreamingContext(sc, 2)
ssc.checkpoint("handler-checkpoints")

# dataStream = ssc.socketTextStream("localhost",9009)
for message in consumer:
    print("DEBUG: received - " + message.value)
    try:
        words = message.value.split(" ")
        hashtags = filter(lambda w: '#' in w, words)
        hashtag_counts = map(lambda x: (x, 1), hashtag_counts)
        tags_totals = hashtags.updateStateByKey(aggregate_tags_count)
        tags_totals.foreachRDD(process_rdd)
    except:
        e = sys.exc_info()
        print("ERROR: %s" % e[1])

# ssc.start()
# ssc.awaitTermination()
