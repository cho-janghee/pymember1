import requests
import xml.etree.ElementTree as ET

API_KEY = "4d7041427279616233375142676359"  # 실제 키로 교체
ROAD_CODE = "1220003800"
url = f"http://openapi.seoul.go.kr:8088/{API_KEY}/xml/TrafficInfo/1/5/{ROAD_CODE}"

response = requests.get(url)

if response.status_code == 200:
    xml_data = response.text
    root = ET.fromstring(xml_data)
    for row in root.findall(".//row"):
        road_name = row.findtext("ROAD_NM") or ""
        road_st = row.findtext("ROAD_ST_NM") or ""
        road_ed = row.findtext("ROAD_ED_NM") or ""
        speed = row.findtext("SPD") or ""
        status = row.findtext("CONGESTION") or ""
        section = f"{road_st} ~ {road_ed}"
        print(f"[{road_name}] 구간: {section}, 속도: {speed}km/h, 소통상태: {status}")
else:
    print("에러 발생:", response.status_code, response.text)
