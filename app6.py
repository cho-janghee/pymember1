import requests
import xml.etree.ElementTree as ET

API_KEY = "4d7041427279616233375142676359"

# 조회할 Link ID(도로코드) 목록
link_id_list = [
    "1220003800",
    "1220004100",
    "1220004300",
    "1220004500"
    # ...여기에 더 추가
]

for link_id in link_id_list:
    url = f"http://openapi.seoul.go.kr:8088/{API_KEY}/xml/TrafficInfo/1/5/{link_id}"
    response = requests.get(url)
    if response.status_code == 200:
        xml_data = response.text
        root = ET.fromstring(xml_data)
        rows = root.findall(".//row")
        if rows:
            for row in rows:
                link_id_val = row.findtext("link_id") or ""
                speed = row.findtext("prcs_spd") or ""
                trv_time = row.findtext("prcs_trv_time") or ""
                print(f"[Link ID: {link_id_val}] 평균 속도: {speed}km/h, 소요 시간: {trv_time}초")
        else:
            print(f"[Link ID: {link_id}] 데이터 없음")
    else:
        print(f"[Link ID: {link_id}] 에러 발생: {response.status_code}")

