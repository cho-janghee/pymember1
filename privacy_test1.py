import tkinter as tk
from tkinter import filedialog
import glob
import os
import re

# chardet 설치 필요: pip install chardet
import chardet

def select_folder():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askdirectory(title="분석할 폴더를 선택하세요")

def is_text_file(filename):
    text_exts = {'.txt', '.log', '.csv', '.xml', '.json', '.ini', '.conf'}
    _, ext = os.path.splitext(filename)
    return ext.lower() in text_exts

def try_open_lines(filename):
    encodings = ['utf-8', 'euc-kr', 'cp949']
    for enc in encodings:
        try:
            with open(filename, encoding=enc) as f:
                return list(f), enc, False
        except UnicodeDecodeError:
            continue
    # chardet로 감지 시도 (1MB까지만 샘플)
    try:
        with open(filename, 'rb') as f:
            rawdata = f.read(1024*1024)
        detected = chardet.detect(rawdata)
        detected_enc = detected.get('encoding')
        if detected_enc:
            try:
                with open(filename, encoding=detected_enc) as f:
                    return list(f), detected_enc, False
            except Exception:
                pass
    except Exception:
        pass
    # 그래도 안되면 utf-8 errors=ignore로라도 읽음
    try:
        with open(filename, encoding='utf-8', errors='ignore') as f:
            return list(f), "utf-8 (errors=ignore)", True  # True면 일부 누락 가능
    except Exception:
        pass
    return None, None, None  # 완전히 불가

def scan_folder(folder):
    patterns = {
        "주민등록번호": re.compile(r'\d{6}-\d{7}'),
        "휴대폰번호": re.compile(r'01[016789]-\d{3,4}-\d{4}'),
        "이메일": re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
    }
    all_files = glob.glob(os.path.join(folder, "**", "*"), recursive=True)
    file_list = [f for f in all_files if os.path.isfile(f) and is_text_file(f)]
    if not file_list:
        print("선택한 폴더에 검사할 텍스트 파일이 없습니다.")
    else:
        print(f"총 {len(file_list)}개의 텍스트 파일을 검사합니다.")
    results = []
    for filename in file_list:
        lines, encoding_used, possibly_lossy = try_open_lines(filename)
        if lines is None:
            print(f"[SKIP] {filename} : 읽을 수 없는 파일(완전 PASS)")
            continue
        if possibly_lossy:
            print(f"[경고] {filename}: 일부 문자가 누락될 수 있습니다 (encoding={encoding_used})")
        for lineno, line in enumerate(lines, 1):
            for name, pattern in patterns.items():
                for match in pattern.finditer(line):
                    results.append({
                        "file": filename,
                        "line": lineno,
                        "type": name,
                        "content": match.group(),
                        "full_line": line.strip(),
                        "encoding": encoding_used,
                        "possibly_lossy": possibly_lossy
                    })
    return results

if __name__ == "__main__":
    folder = select_folder()
    if folder:
        print(f"선택한 폴더: {folder}")
        results = scan_folder(folder)
        if results:
            for result in results:
                loss_msg = " [일부 문자가 누락될 수 있음]" if result.get('possibly_lossy') else ""
                print(f"[{result['file']}:{result['line']}줄][{result['encoding']}]"
                      f"[{result['type']}] {result['content']}: {result['full_line']}{loss_msg}")
        else:
            print("검사 대상 텍스트 파일은 있으나, 개인정보 패턴이 검출되지 않았습니다.")
    else:
        print("폴더를 선택하지 않았습니다.")
