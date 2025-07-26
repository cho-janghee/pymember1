from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import avg

spark = SparkSession.builder.appName("PySpark Practice").getOrCreate()

# 데이터 생성
students = [
    Row(id=1, name="밍키", age=20, dept="컴퓨터"),
    Row(id=2, name="홍길동", age=22, dept="전자"),
    Row(id=3, name="이몽룡", age=21, dept="컴퓨터"),
    Row(id=4, name="성춘향", age=23, dept="기계")
]
scores = [
    Row(student_id=1, subject="수학", score=85),
    Row(student_id=1, subject="영어", score=95),
    Row(student_id=2, subject="수학", score=80),
    Row(student_id=3, subject="영어", score=78),
    Row(student_id=4, subject="수학", score=90)
]
students_df = spark.createDataFrame(students)
scores_df = spark.createDataFrame(scores)
students_df.show()
scores_df.show()

# SQL 쿼리
students_df.createOrReplaceTempView("students")
scores_df.createOrReplaceTempView("scores")
result = spark.sql("SELECT * FROM students WHERE dept = '컴퓨터'")
result.show()

# 집계
students_df.groupBy("dept").agg(avg("age").alias("avg_age")).show()

# 조인
join_df = students_df.join(scores_df, students_df.id == scores_df.student_id, "inner")
join_df.select("name", "subject", "score").show()

# 파일 저장
#join_df.write.mode("overwrite").parquet("output/join_result.parquet")
join_df.write.mode("overwrite").csv("output/join_result.csv", header=True)
print("저장 완료!")

# 저장된 파일 읽기
parquet_df = spark.read.parquet("output/join_result.parquet")
csv_df = spark.read.csv("output/join_result.csv", header=True, inferSchema=True)
print("Parquet에서 읽은 데이터:")
parquet_df.show()
print("CSV에서 읽은 데이터:")
csv_df.show()
