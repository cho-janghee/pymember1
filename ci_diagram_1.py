import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import pygraphviz as pgv
from PIL import Image

def select_excel_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="엑셀(경로) 파일 선택",
        filetypes=[("Excel files", "*.xlsx;*.xls"), ("All files", "*.*")]
    )
    root.destroy()
    return file_path

def main():
    excel_path = select_excel_file()
    if not excel_path:
        print("파일을 선택하지 않았습니다.")
        return

    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        messagebox.showerror("오류", f"엑셀 파일 열기 실패\n{e}")
        return

    G = pgv.AGraph(directed=True)
    for _, row in df.iterrows():
        levels = [str(x).strip() for x in row if pd.notna(x) and str(x).strip() != ""]
        for parent, child in zip(levels, levels[1:]):
            # shape=box 옵션
            G.add_node(parent, shape="box", style="rounded,filled", fillcolor="#e3f2fd", fontname="Malgun Gothic")
            G.add_node(child, shape="box", style="rounded,filled", fillcolor="#e3f2fd", fontname="Malgun Gothic")
            G.add_edge(parent, child)

    # 그래프 레이아웃 및 이미지 파일로 출력
    G.layout(prog="dot")
    png_path = excel_path.rsplit(".", 1)[0] + "_orgchart.png"
    G.draw(png_path)

    # 이미지 미리 보기 (PIL)
    img = Image.open(png_path)
    img.show()
    print(f"조직도(박스형) 이미지로 저장: {png_path}")

if __name__ == "__main__":
    main()
