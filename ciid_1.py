import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os

def select_csv_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="CSV 파일 선택",
        filetypes=[("CSV files", "*.csv"), ("모든 파일", "*.*")]
    )
    root.destroy()
    return file_path

def main():
    # 1. 파일 선택
    csv_path = select_csv_file()
    if not csv_path:
        print("파일을 선택하지 않았습니다.")
        return

    # 2. CSV 읽기  (ITSM CI ID 등 읽기)
    df = pd.read_csv(csv_path)
    df.columns = [c.strip() for c in df.columns]
    edges = list(zip(df['A_ID'], df['B_ID']))

    # 3. 연결관계 dict 생성
    from collections import defaultdict
    tree = defaultdict(list)
    for a, b in edges:
        tree[a].append(b)

    # 4. 계보 경로 추출
    roots = set(df['A_ID']) - set(df['B_ID'])

    def find_paths(node, path):
        if node not in tree or not tree[node]:
            return [path]
        paths = []
        for child in tree[node]:
            paths += find_paths(child, path + [child])
        return paths

    all_paths = []
    for root in roots:
        all_paths += find_paths(root, [root])

    # 5. 엑셀로 저장 -->각 경로를 가로로
    max_depth = max(len(p) for p in all_paths)
    col_names = [f"Level_{i+1}" for i in range(max_depth)]
    df_paths = pd.DataFrame([p + [''] * (max_depth - len(p)) for p in all_paths], columns=col_names)
    excel_path = os.path.splitext(csv_path)[0] + '_paths.xlsx'
    df_paths.to_excel(excel_path, index=False)
    print(f"연결고리(계보) 엑셀 저장: {excel_path}")

    # === 작업 완료 팝업 알림 ===
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("작업 완료", f"계보 엑셀 저장이 완료되었습니다!\n\n{excel_path}")
    root.destroy()

if __name__ == "__main__":
    main()
