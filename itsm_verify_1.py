import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from datetime import datetime
import os

def check_incident(df):
    today = datetime.now().date()
    result = df.copy()

    cols = ['인시던트ID','접수구분','제목','업무구분','대분류','중분류','구성항목','내외부요인',
            '장애등급','영향범위','장애발생일시','서비스복구일시','장애복구일시','처리상태','지연사유']
    for c in cols:
        if c not in result.columns:
            raise Exception(f'필수컬럼 누락: {c}')

    def to_dt(x):
        try:
            return pd.to_datetime(x)
        except:
            return pd.NaT

    result['장애발생일시_dt'] = result['장애발생일시'].apply(to_dt)
    result['서비스복구일시_dt'] = result['서비스복구일시'].apply(to_dt)
    result['장애복구일시_dt'] = result['장애복구일시'].apply(to_dt)

    def i1(row):
        if str(row['처리상태']).strip() == "처리" and pd.notnull(row['장애발생일시_dt']):
            if (today - row['장애발생일시_dt'].date()).days > 20:
                return "초과"
        return ""

    valid_major = {
        "HW(하드웨어)"    : ["시스템", "윈도우", "VDI 지원"],
        "SW(소프트웨어)"  : ["웹와스", "DB"],
        "NW(네트워크)"    : ["네트워크"],
        "EXT(외부기관)"   : ["관제"],
        "FC(부대설비)"    : ["관제"],
        "CIR(통신회선)"   : ["기타"],
        "SEC(보안)"       : ["기타"],
        "APP(어플리케이션)": ["기타"]
    }
    def i2(row):
        gubun = str(row['접수구분']).strip()
        major = str(row['대분류']).strip()
        if gubun in valid_major and major not in valid_major[gubun]:
            return "확인"
        return ""

    def i3(row):
        grade = str(row['장애등급']).strip()
        start = row['장애발생일시_dt']
        svc   = row['서비스복구일시_dt']
        end   = row['장애복구일시_dt']
        if grade == "2등급":
            if pd.isnull(start) or pd.isnull(svc) or pd.isnull(end): return "확인"
            if not (start < svc == end): return "확인"
        elif grade == "3등급":
            if pd.isnull(start) or pd.isnull(svc) or pd.isnull(end): return "확인"
            if not (start == svc and svc < end): return "확인"
        return ""

    def i4(row):
        grade = str(row['장애등급']).strip()
        impact = row['영향범위']
        if grade in ["1등급", "2등급"]:
            if pd.isnull(impact) or str(impact).strip() == "":
                return "확인"
        return ""

    def i5(row):
        inout = str(row['내외부요인']).strip()
        grade = str(row['장애등급']).strip()
        start = row['장애발생일시_dt']
        end = row['장애복구일시_dt']
        gubun = str(row['접수구분']).strip()
        reason = row['지연사유']
        incid = str(row['인시던트ID']).strip()
        if inout == "내부요인" and grade in ["1등급", "2등급", "3등급"]:
            if pd.isnull(start) or pd.isnull(end): return "확인"
            elapsed = (end - start).total_seconds() / 60
            if gubun == "HW(하드웨어)":
                limit = 35
            elif gubun == "SW(소프트웨어)":
                limit = 70
            else:
                limit = 130
            if elapsed > limit and (
                pd.isnull(reason) or str(reason).strip() == "" or str(reason).strip().lower() == "nan"):
                return "확인"
        return ""

    result["I1 인시던트 처리상태"] = result.apply(i1, axis=1)
    result["I2 접수구분 정확성"] = result.apply(i2, axis=1)
    result["I3 장애복구시간의 정확성"] = result.apply(i3, axis=1)
    result["I4 구성항목 적합성"] = result.apply(i4, axis=1)
    result["I5 지연사유"] = result.apply(i5, axis=1)
    result.drop(['장애발생일시_dt','서비스복구일시_dt','장애복구일시_dt'], axis=1, inplace=True)
    return result

def select_file():
    return filedialog.askopenfilename(
        title="엑셀 파일 선택",
        filetypes=[("Excel Files", "*.xlsx;*.xls")]
    )

def run_check():
    selected = check_var.get()
    if not selected:
        messagebox.showerror("오류", "항목을 선택하세요.")
        return
    file_path = select_file()
    if not file_path:
        return
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        messagebox.showerror("엑셀 파일 오류", str(e))
        return
    try:
        if selected == "incident":
            result = check_incident(df)
            out_path = file_path.rsplit('.', 1)[0] + "_검사결과.xlsx"
            if os.path.exists(out_path):
                answer = messagebox.askyesno("파일 존재", f"{out_path}\n이미 파일이 존재합니다.\n덮어쓰시겠습니까?")
                if not answer:
                    messagebox.showinfo("저장취소", "결과파일 저장을 취소했습니다.")
                    return
            result.to_excel(out_path, index=False)
            messagebox.showinfo("완료", f"검사완료\n결과파일: {out_path}")
        elif selected == "config":
            messagebox.showinfo("구성 검사", "준비중(추후업데이트)")
        elif selected == "change":
            messagebox.showinfo("변경릴리즈 검사", "준비중(추후업데이트)")
    except Exception as e:
        messagebox.showerror("검사오류", str(e))

root = tk.Tk()
root.title("엑셀 업무자동화 검사도구")
root.resizable(False, False)
mainfrm = tk.Frame(root, padx=30, pady=25)
mainfrm.pack()

tk.Label(mainfrm, text="검사할 기준을 선택하세요", font=("맑은 고딕", 14, "bold")).pack(pady=(0, 15))
check_var = tk.StringVar(value="")  # 초기값 ""로 설정하면 비선택상태
tk.Radiobutton(mainfrm, text="인시던트",   variable=check_var, value="incident", font=("맑은 고딕",12)).pack(anchor="w")
tk.Radiobutton(mainfrm, text="구성",       variable=check_var, value="config",   font=("맑은 고딕",12)).pack(anchor="w")
tk.Radiobutton(mainfrm, text="변경릴리즈", variable=check_var, value="change",   font=("맑은 고딕",12)).pack(anchor="w")
tk.Button(mainfrm, text="엑셀 파일 선택 및 검사", command=run_check, width=24, height=2, font=("맑은 고딕",11)).pack(pady=(25,0))

root.mainloop()
