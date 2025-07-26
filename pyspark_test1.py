import os
os.environ["JAVA_HOME"] = "C:\Program Files\Java\jdk-11"
os.environ["HADOOP_HOME"] = "C:/hadoop"

from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("test").getOrCreate()
df = spark.createDataFrame([(1,"Alice"),(2,"Bob")],["id","name"])
df.show()


from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Practice").getOrCreate()

data = [("밍키", 100), ("홍길동", 95)]
columns = ["name", "score"]

df = spark.createDataFrame(data, columns)
df.show()
