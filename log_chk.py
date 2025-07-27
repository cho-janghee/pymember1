import tkinter as tk
from tkinter import filedialog
import glob
import os
import re
import chardet

def select_folder():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askdirectory(title="분석할 폴더를 선택하세요")

def is_text_file(filename):
    # 바이너리 signature 탐지: 1KB 샘플
    try:
        with open(filename, 'rb') as f:
            sample = f.read(1024)
            if b'\x00' in sample or sample[:2] in [b'MZ', b'PK', b'\xFF\xD8', b'\x89P']:  # exe, zip, jpg, png
                return False
            if sample[:4] == b'%PDF':
                return False
            # 30% 이상이 비ASCII면 바이너리 취급
            nontext = sum(1 for b in sample if b > 127 and b != 0xA and b != 0xD)
            if len(sample) > 0 and nontext / len(sample) > 0.3:
                return False
    except Exception:
        return False
    # 확장자로 1차 필터 (보수적으로 유지)
    text_exts = {'.txt', '.log', '.csv', '.xml', '.json', '.ini', '.conf'}
    _, ext = os.path.splitext(filename)
    return ext.lower() in text_exts

def try_open_lines(filename):
    encodings = ['utf-8', 'euc-kr', 'cp949']
    for enc in encodings:
        try:
            with open(filename, encoding=enc) as f:
                return list(f), enc
        except UnicodeDecodeError:
            continue
    try:
        with open(filename, 'rb') as f:
            rawdata = f.read(1024*1024)
        detected = chardet.detect(rawdata)
        detected_enc = detected.get('encoding')
        if detected_enc:
            try:
                with open(filename, encoding=detected_enc) as f:
                    return list(f), detected_enc
            except Exception:
                pass
    except Exception:
        pass
    # 검출 불가한 파일은 skip (누락 경고도 없이)
    return None, None

def scan_folder(folder):
    patterns = {
        "IP주소": re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
        "비밀번호(PASS)": re.compile(r'\b(?:pass(word)?|pwd|passwd)\b[\s:;=,\'"]*\S+', re.IGNORECASE),
    }
    all_files = glob.glob(os.path.join(folder, "**", "*"), recursive=True)
    file_list = [f for f in all_files if os.path.isfile(f) and is_text_file(f)]
    detected_files = set()
    results = []
    for filename in file_list:
        lines, encoding_used = try_open_lines(filename)
        if lines is None:
            continue  # 완전히 읽을 수 없으면 skip
        file_flag = False
        for lineno, line in enumerate(lines, 1):
            for name, pattern in patterns.items():
                for match in pattern.finditer(line):
                    results.append({
                        "file": filename,
                        "line": lineno,
                        "type": name,
                        "content": match.group(),
                        "full_line": line.strip(),
                        "encoding": encoding_used
                    })
                    file_flag = True
        if file_flag:
            detected_files.add(filename)
    return detected_files, results

if __name__ == "__main__":
    folder = select_folder()
    if folder:
        print(f"선택한 폴더: {folder}")
        detected_files, results = scan_folder(folder)
        if results:
            print(f"\n=== 시스템 정보 검출된 파일: {len(detected_files)}개 ===")
            for i, f in enumerate(sorted(detected_files), 1):
                print(f"  {i}. {f}")
            print(f"\n=== 검출 상세 내역 ({len(results)}건) ===")
            for result in results:
                print(f"[{result['file']}:{result['line']}줄][{result['encoding']}]"
                      f"[{result['type']}] {result['content']}: {result['full_line']}")
        else:
            print("검사 대상 텍스트 파일은 있으나, 시스템 정보 패턴은 검출되지 않았습니다.")
    else:
        print("폴더를 선택하지 않았습니다.")
