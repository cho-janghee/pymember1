import os
import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk

ALLOWED_EXTS = {
    ".xlsx", ".xls", ".csv", ".txt", ".ppt", ".pptx",
    ".hwp", ".hwpx", ".doc", ".docx", ".pdf", ".md", ".rtf"
}

def select_drive():
    import string
    import ctypes
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(letter + ":\\")
        bitmask >>= 1

    root = tk.Tk()
    root.withdraw()
    drive = simpledialog.askstring("드라이브 선택", "아래 드라이브 중 하나를 입력하세요:\n" + "\n".join(drives))
    root.destroy()
    if drive and os.path.isdir(drive):
        return drive
    else:
        messagebox.showinfo("오류", "유효한 드라이브를 입력하세요.")
        return None

def select_folder_with_tree(start_drive):
    selected_folder = [None]

    def on_select(event):
        item_id = tree.selection()
        if not item_id:
            return
        node = item_id[0]
        abspath = tree.set(node, "fullpath")
        if os.path.isdir(abspath):
            selected_folder[0] = abspath
            root.quit()

    def populate_tree(parent, abspath):
        try:
            dirs = [d for d in os.listdir(abspath) if os.path.isdir(os.path.join(abspath, d))]
            dirs.sort()
            for d in dirs:
                full = os.path.join(abspath, d)
                node_id = tree.insert(parent, "end", text=d, values=[full])
                tree.insert(node_id, "end")  # 더미(+) 표시용
        except Exception:
            pass

    def open_node(event):
        node = tree.focus()
        if not node:
            return
        abspath = tree.set(node, "fullpath")
        children = tree.get_children(node)
        if children:
            first_child = children[0]
            # 더미 노드면
            if tree.item(first_child, "text") == "":
                tree.delete(first_child)
                populate_tree(node, abspath)

    root = tk.Tk()
    root.title("폴더 선택")
    tree = ttk.Treeview(root, columns=("fullpath",), displaycolumns=())
    ysb = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    tree.configure(yscroll=ysb.set)
    tree.pack(fill="both", expand=True, side="left")
    ysb.pack(fill="y", side="right")
    # 드라이브 루트
    node = tree.insert("", "end", text=start_drive, values=[start_drive])
    populate_tree(node, start_drive)
    tree.bind("<<TreeviewOpen>>", open_node)
    tree.bind("<Double-1>", on_select)
    root.mainloop()
    root.destroy()
    return selected_folder[0]

def scan_folder_nested(root_path):
    results = []
    MAX_DEPTH = 20
    header = [f'Level_{i+1}' for i in range(MAX_DEPTH)]
    header += ['파일크기(MB)', '마지막수정일']
    results.append(header)

    def walk(current_path, depth):
        try:
            entries = os.listdir(current_path)
        except Exception:
            return
        folders = []
        files = []
        for e in entries:
            full_path = os.path.join(current_path, e)
            if os.path.isdir(full_path):
                folders.append(e)
            else:
                files.append(e)
        for folder in folders:
            row = [''] * depth + [folder] + [''] * (len(header) - (depth+1))
            results.append(row)
            walk(os.path.join(current_path, folder), depth + 1)
        for file in files:
            _, ext = os.path.splitext(file)
            if ext.lower() not in ALLOWED_EXTS:
                continue
            fp = os.path.join(current_path, file)
            try:
                stat = os.stat(fp)
                mtime = datetime.fromtimestamp(stat.st_mtime)
                size_mb = round(stat.st_size / 1048576, 2)
                row = [''] * depth + [file] + [''] * (len(header) - (depth+1) - 2) + [size_mb, mtime]
                results.append(row)
            except Exception:
                continue
    walk(root_path, 0)
    return results

def save_selected_folder_tree_to_excel():
    drive = select_drive()
    if not drive:
        print("드라이브 선택 취소 또는 오류")
        return
    folder = select_folder_with_tree(drive)
    if not folder:
        print("폴더 선택 취소 또는 오류")
        return

    print(f"선택한 폴더 이하 트리 생성 시작: {folder}")
    data = scan_folder_nested(folder)
    header_len = len(data[0])
    fixed_data = [data[0]] + [r[:header_len] + ['']*(header_len-len(r)) for r in data[1:]]
    df = pd.DataFrame(fixed_data[1:], columns=fixed_data[0])

    save_path = os.path.join(folder, "업무파일_트리.xlsx")
    df.to_excel(save_path, index=False)
    print(f"엑셀 저장 완료: {save_path}")

if __name__ == "__main__":
    save_selected_folder_tree_to_excel()
