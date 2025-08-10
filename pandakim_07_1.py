import pandas as pd
import numpy as np
import os

# 저장 경로 설정
save_path = r"D:\파이썬_데이터분석\판매원장_데이터_1_20250810.xlsx"

# 샘플 데이터
np.random.seed(42)
products = [
    '종합어묵 (300g)', '유기농떡튀밥 (40g)', '염장다시마 (400g)',
    '간편미역국 (10g*5)', '구운김 (10매)', '김가루 (50g)',
    '멸치가루 (120g)', '다시팩 (20g*10)', '미소된장 (500g)',
    '게맛살 (178g)', '생선가스 (300g)', '오징어채 (200g)',
    '쌀과자 (100g)', '감자칩 (110g)', '옥수수수프 (250g)'
]
branches = ['강남점','강북점','분당점','수원점','옥길점']

def make_sheet(multiplier: int):
    base = np.random.randint(150_000, 2_500_000, size=(len(products), len(branches)))
    df = pd.DataFrame(base, columns=branches)
    df.insert(0, '제품', products)
    for col in branches:
        df[col] = (df[col] * (1 + 0.02 * multiplier)).astype(int)
    return df

# 시트별 데이터 생성
sheets = {
    '2023년': make_sheet(0),
    '2024년': make_sheet(1),
    '2025년': make_sheet(2),
}

# 폴더 없으면 생성
os.makedirs(os.path.dirname(save_path), exist_ok=True)

# 엑셀 파일 저장
with pd.ExcelWriter(save_path, engine='xlsxwriter') as writer:
    for sheet_name, sheet_df in sheets.items():
        sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"엑셀 파일 생성 완료: {save_path}")
