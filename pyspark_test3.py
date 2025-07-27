from pyspark.sql import SparkSession, Row, functions as F
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
import matplotlib.pyplot as plt

import pandas as pd
import numpy as np

spark = SparkSession.builder.appName("Advanced SQL Practice").getOrCreate()

# 예제 데이터 준비
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
    Row(student_id=4, subject="수학", score=90),
    Row(student_id=2, subject="영어", score=88),
    Row(student_id=3, subject="수학", score=70),
    Row(student_id=4, subject="영어", score=91)
]

students_df = spark.createDataFrame(students)
scores_df = spark.createDataFrame(scores)

students_df.createOrReplaceTempView("students")
scores_df.createOrReplaceTempView("scores")

# 1) 학생별 전체 평균 점수 SQL
result1 = spark.sql("""
    SELECT s.name, AVG(sc.score) as avg_score
    FROM students s
    JOIN scores sc ON s.id = sc.student_id
    GROUP BY s.name
    ORDER BY avg_score DESC
""")
result1.show()

# 2) 과목별 최고점 학생
result2 = spark.sql("""
    SELECT sc.subject, s.name, sc.score
    FROM students s
    JOIN scores sc ON s.id = sc.student_id
    WHERE (sc.subject, sc.score) IN (
        SELECT subject, MAX(score) FROM scores GROUP BY subject
    )
""")
result2.show()

def score_grade(score):
    if score >= 90:
        return "우수"
    elif score >= 80:
        return "보통"
    else:
        return "미달"

# UDF 등록
grade_udf = udf(score_grade, StringType())
#
# # 점수 데이터프레임에 등급 컬럼 추가
scores_with_grade = scores_df.withColumn("grade", grade_udf(scores_df.score))
scores_with_grade.show()
#
# 10만 행짜리 샘플 데이터 생성
N = 100000
df = pd.DataFrame({
    "id": np.arange(1, N+1),
    "name": np.random.choice(["밍키", "홍길동", "이몽룡", "성춘향"], size=N),
    "score": np.random.randint(50, 101, size=N),
    "subject": np.random.choice(["수학", "영어", "과학"], size=N)
})
df.to_csv("big_scores.csv", index=False, encoding="utf-8-sig")  # 한글깨짐 방지
#
# PySpark에서 불러오기
big_scores_df = spark.read.csv("big_scores.csv", header=True, inferSchema=True)
big_scores_df.show(5)
print("총 행 개수:", big_scores_df.count())

# Parquet로 저장
big_scores_df.write.mode("overwrite").parquet("big_scores.parquet")

# Parquet 파일 불러오기
parquet_df = spark.read.parquet("big_scores.parquet")
parquet_df.show(5)

# 학생별 평균 점수 계산
avg_df = big_scores_df.groupBy("name").agg(F.avg("score").alias("avg_score"))
avg_df.show()

# pandas로 변환
avg_pd = avg_df.toPandas()
print(avg_pd)

plt.bar(avg_pd["name"], avg_pd["avg_score"])
plt.title("학생별 평균 점수")
plt.xlabel("이름")
plt.ylabel("평균 점수")
plt.show()
