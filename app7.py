import csv
import sqlite3

# CSV 파일명 (다운로드 받은 파일로 교체)
csv_file = "C:/Users/jsams/seoul_linkid.csv"

# DB 연결
conn = sqlite3.connect("links.db")
cur = conn.cursor()

# 테이블 생성
cur.execute("""
CREATE TABLE IF NOT EXISTS link (
    link_id TEXT PRIMARY KEY,
    start_node_id TEXT,
    end_node_id TEXT,
    start_node_name TEXT,
    end_node_name TEXT,
    road_name TEXT,
    map_distance TEXT,   -- 실수도 문자열로 받는 게 SQLite에서 더 안전
    link_cnt INTEGER,
    std_yn TEXT,
    region_code TEXT,
    region_name TEXT,
    grade_code TEXT,
    grade_code_name TEXT,
    grade_yn TEXT
)
""")

with open(csv_file, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    print(reader.fieldnames)  # <- 컬럼명 리스트 출력!
    for row in reader:
        print(row)  # 샘플 row 확인 (처음 1~2줄만 print해봐도 OK)
        break

# CSV 읽어서 DB 저장
with open(csv_file, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        cur.execute("""
            INSERT OR IGNORE INTO link (
                link_id,start_node_id,end_node_id,start_node_name,end_node_name,
                road_name,map_distance,link_cnt,std_yn,region_code,region_name,
                grade_code,grade_code_name,grade_yn)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["\ufeff링크ID"],  # BOM이 붙은 한글 컬럼명
            row["시작노드ID"],
            row["종료노드ID"],
            row["시작노드명"],
            row["종료노드명"],
            row["도로명"],
            row["지도거리"],
            row["표준링크수"],
            row["기본도로여부"],
            row["권역코드"],
            row["권역코드명"],
            row["소통등급구분코드"],
            row["소통등급구분코드명"],
            row["소통제공여부"]
        ))

conn.commit()
conn.close()

