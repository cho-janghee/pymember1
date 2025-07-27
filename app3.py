import requests

# 1. 본인의 인증키 입력
API_KEY = '4d7041427279616233375142676359'

# 2. 사용할 API 엔드포인트 예시 (신한카드 결제정보)
# 아래는 "CardBillShopNew" API로, 일자별 매출정보 (2023년 1월 1일 기준)
url = f'http://openapi.seoul.go.kr:8088/{API_KEY}/json/CardBillShopNew/1/5/20250726'

# 3. 데이터 요청
response = requests.get(url)

# 4. 결과 확인 (json 포맷)
if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print("에러 발생:", response.status_code, response.text)