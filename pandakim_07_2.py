import pandas as pd

# 보기 옵션
pd.set_option('display.max_rows', None)     # 모든 행 표시
pd.set_option('display.max_columns', None)  # 모든 열 표시
pd.set_option('display.width', None)        # 줄바꿈 없이 표시

# 엑셀 불러오기
url = r"D:\파이썬_데이터분석\주식_종목별종가_예제_20250810.xlsx"
df = pd.read_excel(url, sheet_name=0)

# '거래량'이 숫자형이 아닐 경우를 대비한 변환
df['거래량'] = pd.to_numeric(df['거래량'], errors='coerce')

# pivot_table 생성
pivot_df = (
    df.pivot_table(
        values='거래량',         # 집계 대상 컬럼
        index='시장구분',        # 행(세로)
        columns='소속부',        # 열(가로)
        aggfunc='sum'           # 합계
    )
    .div(1000)                  # 천 단위로 변환
    .round(1)                   # 소수점 한 자리 반올림

)

print(pivot_df)
