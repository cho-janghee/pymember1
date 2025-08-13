import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os
from collections import defaultdict

# =========================
# 1) "연결(계보)" 엣지 엑셀 선택/읽기
#    - 시트에 A_ID, B_ID 컬럼 필요
# =========================
def select_edge_excel():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="연결(계보) 엑셀 선택 (A_ID, B_ID 포함)",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    root.destroy()
    return file_path

def read_edges_excel(xl_path):
    df = pd.read_excel(xl_path)
    df.columns = [str(c).strip() for c in df.columns]
    if 'A_ID' not in df.columns or 'B_ID' not in df.columns:
        raise KeyError("엑셀에 'A_ID', 'B_ID' 컬럼이 필요")
    return df

# =========================
# 2) ID 메타정보 엑셀 선택/읽기
#    - 시트에 ID(키), 한글명/영문명/대중소분류/업무구분/상태/등록일시
# =========================
def select_meta_excel():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="ID 메타정보 엑셀 파일",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    root.destroy()
    return file_path

def read_id_metadata_excel(xl_path):
    df = pd.read_excel(xl_path)
    df.columns = [str(c).strip() for c in df.columns]

    # ID 컬럼 탐색
    key_col = None
    candidates = ['ID', 'id']
    for c in candidates:
        if c in df.columns:
            key_col = c
            break
    if key_col is None:
        raise KeyError("메타 엑셀에서 ID 컬럼 없음")

    # 필요한 메타필드
    meta_fields = ['한글명', '영문명', '대분류명', '중분류명', '소분류명', '업무구분', '상태', '등록일시']
    for f in meta_fields:
        if f not in df.columns:
            df[f] = ""

    # ID -> 메타정보 매핑
    meta = {}
    for _, row in df.iterrows():
        key = str(row[key_col]).strip()
        meta[key] = {f: ("" if pd.isna(row[f]) else row[f]) for f in meta_fields}

    return meta, meta_fields

# =========================
# 3) 경로 생성
# =========================
def build_paths_from_edges(df_edges):
    df_edges.columns = [str(c).strip() for c in df_edges.columns]
    edges = list(zip(df_edges['A_ID'], df_edges['B_ID']))

    tree = defaultdict(list)
    for a, b in edges:
        a_s, b_s = str(a).strip(), str(b).strip()
        tree[a_s].append(b_s)

    parents = set(df_edges['A_ID'].map(lambda x: str(x).strip()))
    children = set(df_edges['B_ID'].map(lambda x: str(x).strip()))
    roots = parents - children  # 루트 후보

    def find_paths(node, path):
        if node not in tree or not tree[node]:
            return [path]
        paths = []
        for child in tree[node]:
            if child in path:            # 사이클 방지
                paths.append(path + [child])
                continue
            paths += find_paths(child, path + [child])
        return paths

    all_paths = []
    for r in roots:
        all_paths += find_paths(r, [r])

    return all_paths

# =========================
# 4) Level_n 옆에 메타 끼워넣기
# =========================
def interleave_with_metadata(df_paths, meta_map, meta_fields):
    level_cols = list(df_paths.columns)
    for c in level_cols:
        df_paths[c] = df_paths[c].astype(str)

    # Level_n_필드 추가
    for lv in level_cols:
        for f in meta_fields:
            new_col = f"{lv}_{f}"
            df_paths[new_col] = df_paths[lv].map(lambda x: meta_map.get(x, {}).get(f, ""))

    # 출력 순서: Level_1, Level_1_*, Level_2, Level_2_*, ...
    out_cols = []
    for lv in level_cols:
        out_cols.append(lv)
        out_cols.extend([f"{lv}_{f}" for f in meta_fields])

    return df_paths[out_cols]

# =========================
# 5) 메인
# =========================
def main():
    # (1) 엑셀 선택/읽기
    edge_xl = select_edge_excel()
    if not edge_xl:
        print("연결 엑셀을 선택 필요!!")
        return
    try:
        df_edges = read_edges_excel(edge_xl)
    except Exception as e:
        messagebox.showerror("오류", f"연결(계보) 엑셀 읽기 실패\n{e}")
        return

    # (2) 경로(계보)
    try:
        all_paths = build_paths_from_edges(df_edges)
    except Exception as e:
        messagebox.showerror("오류", f"경로 계산 실패\n{e}")
        return

    if not all_paths:
        messagebox.showwarning("안내", "경로 없음")
        return

    max_depth = max(len(p) for p in all_paths)
    level_cols = [f"Level_{i+1}" for i in range(max_depth)]
    df_paths = pd.DataFrame([p + [''] * (max_depth - len(p)) for p in all_paths], columns=level_cols)

    # (3) 메타 엑셀 선택/읽기
    meta_xl = select_meta_excel()
    if not meta_xl:
        print("메타정보 엑셀을 선택하세요.")
        return
    try:
        id_meta_map, meta_fields = read_id_metadata_excel(meta_xl)
    except Exception as e:
        messagebox.showerror("오류", f"메타정보 엑셀 읽기 실패\n{e}")
        return

    # (4) 메타
    try:
        df_final = interleave_with_metadata(df_paths.copy(), id_meta_map, meta_fields)
    except Exception as e:
        messagebox.showerror("오류", f"메타정보 결합 실패\n{e}")
        return

    # (5) 저장
    base = os.path.splitext(edge_xl)[0]
    out_xl = base + "_paths.xlsx"
    try:
        df_final.to_excel(out_xl, index=False)
    except Exception as e:
        messagebox.showerror("오류", f"엑셀 저장 실패\n{e}")
        return

    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(
        "작업 완료",
        "최종 엑셀 저장이 완료!\n\n"
        f"{out_xl}\n\n"
        f"(추출 컬럼: {', '.join(df_final.columns[:min(8, len(df_final.columns))])} ...)"
    )
    root.destroy()

if __name__ == "__main__":
    main()
