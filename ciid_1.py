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

# === 인코딩 자동 판별 CSV 읽기 ===
def read_csv_with_encoding(filepath, encodings=None):
    if encodings is None:
        encodings = ['utf-8-sig', 'utf-8', 'cp949', 'euc-kr', 'latin1']
    for enc in encodings:
        try:
            df = pd.read_csv(filepath, encoding=enc)
            return df, enc
        except Exception:
            continue
    raise UnicodeDecodeError("모든 인코딩 시도 실패! 수동으로 확인 필요.")

def main():
    csv_path = select_csv_file()
    if not csv_path:
        print("파일을 선택하지 않았습니다.")
        return

    # 인코딩 자동 판별하여 CSV 읽기
    try:
        df, enc_used = read_csv_with_encoding(csv_path)
    except Exception as e:
        messagebox.showerror("오류", f"CSV 파일 열기 실패\n{e}")
        return

    df.columns = [c.strip() for c in df.columns]
    edges = list(zip(df['A_ID'], df['B_ID']))

    from collections import defaultdict
    tree = defaultdict(list)
    for a, b in edges:
        tree[a].append(b)

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

    max_depth = max(len(p) for p in all_paths)
    col_names = [f"Level_{i+1}" for i in range(max_depth)]
    df_paths = pd.DataFrame([p + [''] * (max_depth - len(p)) for p in all_paths], columns=col_names)
    excel_path = os.path.splitext(csv_path)[0] + '_paths.xlsx'
    df_paths.to_excel(excel_path, index=False)
    print(f"연결고리(계보) 엑셀 저장: {excel_path}")

    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("작업 완료", f"계보 엑셀 저장이 완료되었습니다!\n\n{excel_path}\n\n(인코딩: {enc_used})")
    root.destroy()

if __name__ == "__main__":
    main()
