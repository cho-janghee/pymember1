import requests
from datetime import datetime, timedelta

API_KEY = '4d7041427279616233375142676359'
base_url = f'http://openapi.seoul.go.kr:8088/{API_KEY}/json/CardBillShopNew/1/5/'

# 어제부터 10일간 데이터 탐색
today = datetime.today()
for i in range(100):
    date_str = (today - timedelta(days=i+1)).strftime('%Y%m%d')
    url = base_url + date_str
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        if "CardBillShopNew" in data:
            print(f"== {date_str} 데이터 있음 ==")
            print(data)
            break  # 첫 데이터가 있으면 종료
        else:
            print(f"{date_str} 데이터 없음")
    else:
        print(f"{date_str} 에러 발생")
