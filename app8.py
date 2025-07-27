import sqlite3
import requests
import xml.etree.ElementTree as ET

API_KEY = "4d7041427279616233375142676359"  # 실제 서울시 오픈API 키

# 1. DB에서 Link ID 전체 읽기
conn = sqlite3.connect("links.db")
cur = conn.cursor()
cur.execute("SELECT link_id, road_name, start_node_name, end_node_name FROM link")
links = cur.fetchall()
conn.close()

# 2. 각 Link ID별로 실시간 교통정보 조회
for link_id, road_name, start_name, end_name in links:
    url = f"http://openapi.seoul.go.kr:8088/{API_KEY}/xml/TrafficInfo/1/5/{link_id}"
    response = requests.get(url)
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        rows = root.findall(".//row")
        if rows:
            for row in rows:
                speed = row.findtext("prcs_spd") or ""
                trv_time = row.findtext("prcs_trv_time") or ""
                print(f"{road_name}({link_id}) {start_name}~{end_name}: 속도 {speed}km/h, 소요 {trv_time}초")
        else:
            print(f"{road_name}({link_id}) {start_name}~{end_name}: 데이터 없음")
    else:
        print(f"{road_name}({link_id}) {start_name}~{end_name}: 에러 발생: {response.status_code}")

