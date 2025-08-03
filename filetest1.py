import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, scrolledtext
import pandas as pd
import os
import pyperclip

# 파일 선택
def select_file(root):
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="파일을 선택하세요",
        filetypes=[("Excel files", "*.xls *.xlsx"), ("CSV files", "*.csv"), ("모든 파일", "*.*")]
    )
    return file_path

def main():
    root = tk.Tk()
    file_path = select_file(root)
    if not file_path:
        root.destroy()
        return

    messagebox.showinfo("파일경로", file_path)
    root.destroy()

if __name__ == "__main__":
    main()
