from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

# 예시: 점수에 따라 "우수", "보통", "미달" 등급화
def score_grade(score):
    if score >= 90:
        return "우수"
    elif score >= 80:
        return "보통"
    else:
        return "미달"

# UDF 등록
grade_udf = udf(score_grade, StringType())

# 점수 데이터프레임에 등급 컬럼 추가
scores_with_grade = scores_df.withColumn("grade", grade_udf(scores_df.score))
scores_with_grade.show()
