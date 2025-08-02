import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, scrolledtext
import pandas as pd
import os
import pyperclip

# 파일 선택 다이얼로그
def select_ci_file():
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("안내", "CI 목록 파일을 선택하세요")
    file_path = filedialog.askopenfilename(
        title="CI 목록 파일을 선택하세요",
        filetypes=[("Excel files", "*.xls *.xlsx"), ("CSV files", "*.csv"), ("모든 파일", "*.*")]
    )
    root.destroy()
    return file_path

# 인코딩 자동 판별 Excel/CSV 읽기
def read_file_with_encoding(filepath):
    ext = os.path.splitext(filepath)[-1].lower()
    if ext in ['.xls', '.xlsx']:
        df = pd.read_excel(filepath)
        return df, 'Excel'
    else:
        encodings = ['utf-8-sig', 'utf-8', 'cp949', 'euc-kr', 'latin1']
        for enc in encodings:
            try:
                df = pd.read_csv(filepath, encoding=enc)
                return df, enc
            except Exception:
                continue
        raise UnicodeDecodeError("모든 인코딩 시도 실패! 수동으로 확인 필요.")

# CI ID 입력 다이얼로그
def input_ci_id():
    root = tk.Tk()
    root.withdraw()
    ci_id = simpledialog.askstring("CI ID 입력", "검색할 CI ID를 입력하세요")
    root.destroy()
    return ci_id

# 전체 트리 탐색 (상위→하위로), 경로 중 ci_id 포함하는 path만 추출
def find_all_paths(tree, node_info, start, path, ci_id, result):
    path = path + [start]
    # leaf node
    if start not in tree or not tree[start]:
        if ci_id in path:
            result.append(path)
        return
    for child in tree[start]:
        find_all_paths(tree, node_info, child, path, ci_id, result)

def make_ci_path(df, ci_id):
    df.columns = [c.strip() for c in df.columns]

    # 컬럼 자동 매핑
    colmap = {}
    for col in df.columns:
        if '상위 CI ID' in col: colmap['parent_id'] = col
        elif '하위 CI ID' in col: colmap['child_id'] = col
        elif '상위 CI명' in col: colmap['parent_name'] = col
        elif '하위 CI명' in col: colmap['child_name'] = col
        elif '상위 CI 영문명' in col: colmap['parent_name_en'] = col
        elif '하위 CI 영문명' in col: colmap['child_name_en'] = col

    # 트리 만들기
    from collections import defaultdict
    tree = defaultdict(list)
    node_info = {}
    parents = set()
    children = set()
    for _, row in df.iterrows():
        parent_id = str(row[colmap['parent_id']]).strip()
        child_id = str(row[colmap['child_id']]).strip()
        tree[parent_id].append(child_id)
        parents.add(parent_id)
        children.add(child_id)
        node_info[parent_id] = (str(row[colmap['parent_name']]), str(row[colmap['parent_name_en']]))
        node_info[child_id] = (str(row[colmap['child_name']]), str(row[colmap['child_name_en']]))

    roots = list(parents - children)
    if not roots:
        roots = list(parents)  # 예외 상황 시

    # 모든 root에서 DFS, ci_id 포함한 path만
    result_paths = []
    for root in roots:
        find_all_paths(tree, node_info, root, [], ci_id, result_paths)

    if not result_paths:
        raise Exception(f"'{ci_id}'를 포함한 경로를 찾을 수 없습니다.")

    # 여러 경로가 나올 수도 있으니 모두 출력 (여러개면 줄바꿈)
    result_strs = []
    for path in result_paths:
        nodestr = []
        for nid in path:
            kor, eng = node_info.get(nid, ("", ""))
            nodestr.append(f"{nid}({kor}, {eng})")
        result_strs.append(" → ".join(nodestr))
    return "\n".join(result_strs)

# 텍스트 복사 함수
def copy_to_clipboard(text):
    pyperclip.copy(text)
    messagebox.showinfo("복사 완료", "텍스트가 클립보드에 복사되었습니다!")

# 메인 실행
def main():
    file_path = select_ci_file()
    if not file_path:
        return

    try:
        df, enc_used = read_file_with_encoding(file_path)
    except Exception as e:
        messagebox.showerror("오류", f"파일 열기 실패: {e}")
        return

    ci_id = input_ci_id()
    if not ci_id:
        return

    try:
        result_str = make_ci_path(df, ci_id.strip())
    except Exception as e:
        messagebox.showerror("오류", f"CI 경로 생성 실패: {e}")
        return

    win = tk.Tk()
    win.title("CI 경로 출력 및 복사")
    win.geometry("900x350")

    text_box = scrolledtext.ScrolledText(win, width=120, height=8, font=("맑은 고딕", 11))
    text_box.insert(tk.END, result_str)
    text_box.pack(padx=10, pady=15, fill=tk.BOTH, expand=True)

    def on_copy():
        copy_to_clipboard(result_str)

    btn_frame = tk.Frame(win)
    btn_frame.pack(anchor='se', padx=20, pady=5)

    copy_btn = tk.Button(btn_frame, text="텍스트 복사", command=on_copy)
    copy_btn.pack(side=tk.LEFT, padx=8)

    close_btn = tk.Button(btn_frame, text="닫기", command=win.destroy)
    close_btn.pack(side=tk.LEFT, padx=8)

    win.mainloop()

if __name__ == "__main__":
    main()
