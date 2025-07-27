import requests
import xml.etree.ElementTree as ET

API_KEY = "4d7041427279616233375142676359"
url = f"http://openapi.seoul.go.kr:8088/{API_KEY}/xml/fcltOpenInfo_OPSI/1/5/"

response = requests.get(url)

if response.status_code == 200:
    # XML 텍스트 추출
    xml_data = response.text
    # XML 파싱
    root = ET.fromstring(xml_data)

    # XML의 <row> 항목들 출력
    for row in root.findall(".//row"):
        name = row.findtext("FCLT_NM")
        address = row.findtext("REFINE_LOTNO_ADDR")
        tel = row.findtext("TELNO")
        print(f"시설명: {name}, 주소: {address}, 전화번호: {tel}")
else:
    print("에러 발생:", response.status_code, response.text)
