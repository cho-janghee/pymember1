import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os

def select_excel_file(title="엑셀 파일 선택"):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title=title,
        filetypes=[("Excel files", "*.xlsx;*.xls"), ("모든 파일", "*.*")]
    )
    root.destroy()
    return file_path

def main():
    # 1. A파일(계보 엑셀) 선택: 안내 메시지
    print("Step 1: CI 목록파일을 선택하세요 (예: 계보 파일)")
    a_path = select_excel_file("CI 목록파일을 선택하세요")
    if not a_path:
        print("A파일을 선택하지 않았습니다.")
        return

    # 2. B파일(CI 정보) 선택: 안내 메시지
    print("Step 2: CI명과 상세내용 파일을 선택하세요 (예: CI 상세 정보 파일)")
    b_path = select_excel_file("CI명과 상세내용 파일을 선택하세요")
    if not b_path:
        print("B파일을 선택하지 않았습니다.")
        return

    # 3. 파일 읽기
    try:
        a_df = pd.read_excel(a_path)
        b_df = pd.read_excel(b_path)
    except Exception as e:
        messagebox.showerror("오류", f"엑셀 파일 열기 실패\n{e}")
        return

    # 4. B파일 컬럼명 표준화 및 중복 CI는 첫번째만 사용
    b_df.columns = [c.strip() for c in b_df.columns]
    b_df_unique = b_df.drop_duplicates(subset=['CI'])

    # 중복된 CI가 있다면 로그로 출력(선택사항)
    dupes = b_df[b_df.duplicated(subset=['CI'], keep=False)]
    if not dupes.empty:
        print("중복된 CI 값(첫 번째 값만 사용):\n", dupes[['CI', 'CI명']])

    ci_map = b_df_unique.set_index('CI').to_dict(orient='index')  # CI를 key, 나머지 row를 value로

    # 5. Level_1 오른쪽에 3개 컬럼 삽입
    if 'Level_1' not in a_df.columns or 'Level_2' not in a_df.columns:
        messagebox.showerror("오류", "A파일에 Level_1 또는 Level_2 컬럼이 없습니다.")
        return

    insert_pos_1 = a_df.columns.get_loc('Level_1') + 1  # Level_1 바로 오른쪽
    def get_binfo(val, key):
        if pd.isna(val): return ""
        rec = ci_map.get(val, {})
        return rec.get(key, "")

    a_df.insert(insert_pos_1, "Level_1_CI명", a_df['Level_1'].map(lambda x: get_binfo(x, 'CI명')))
    a_df.insert(insert_pos_1+1, "Level_1_내용", a_df['Level_1'].map(lambda x: get_binfo(x, '내용')))
    a_df.insert(insert_pos_1+2, "Level_1_상세", a_df['Level_1'].map(lambda x: get_binfo(x, '상세')))

    # 6. Level_2 오른쪽에 Name 컬럼 삽입
    insert_pos_2 = a_df.columns.get_loc('Level_2') + 1  # Level_2 바로 오른쪽
    a_df.insert(insert_pos_2, "Level_2_Name", a_df['Level_2'].map(lambda x: get_binfo(x, 'CI명')))

    # 7. 저장
    out_path = os.path.splitext(a_path)[0] + "_with_ciinfo.xlsx"
    a_df.to_excel(out_path, index=False)

    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("완료", f"결과 엑셀이 저장되었습니다!\n\n{out_path}")
    root.destroy()
    print(f"저장 완료: {out_path}")

if __name__ == "__main__":
    main()
