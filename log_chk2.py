import tkinter as tk
from tkinter import filedialog, messagebox
import glob
import os
import re
import chardet
import sys

def select_folder():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askdirectory(title="분석할 폴더를 선택하세요")

def is_text_file(filename):
    try:
        with open(filename, 'rb') as f:
            sample = f.read(1024)
            if b'\x00' in sample or sample[:2] in [b'MZ', b'PK', b'\xFF\xD8', b'\x89P']:
                return False
            if sample[:4] == b'%PDF':
                return False
            nontext = sum(1 for b in sample if b > 127 and b != 0xA and b != 0xD)
            if len(sample) > 0 and nontext / len(sample) > 0.3:
                return False
    except Exception:
        return False
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
        except Exception:
            continue
    try:
        with open(filename, 'rb') as f:
            rawdata = f.read(1024 * 1024)
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
    return None, None

def scan_folder(folder, patterns):
    all_files = glob.glob(os.path.join(folder, "**", "*"), recursive=True)
    file_list = [f for f in all_files if os.path.isfile(f)]
    detected_files = set()
    results = []
    scan_log = []  # (파일, 상태, 인코딩)
    for idx, filename in enumerate(file_list, 1):
        file_status = ""
        encoding_used = None

        # 1. 바이너리/비텍스트 파일 여부
        if not is_text_file(filename):
            file_status = "................."
            sys.stdout.write(f"\r[{idx}/{len(file_list)}] {filename}  ... {file_status}                     \n")
            sys.stdout.flush()
            scan_log.append((filename, file_status, None))
            continue

        # 2. 텍스트 파일이라면, 인코딩 탐색
        lines, encoding_used = try_open_lines(filename)
        if lines is None:
            file_status = "................"
            sys.stdout.write(f"\r[{idx}/{len(file_list)}] {filename}  ... {file_status}                     \n")
            sys.stdout.flush()
            scan_log.append((filename, file_status, None))
            continue

        # 3. 패턴 검색
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
                        "encoding": encoding_used,
                        "pattern": pattern
                    })
                    file_flag = True
        if file_flag:
            file_status = "검사완료 (패턴검출)"
            detected_files.add(filename)
        else:
            file_status = "검사완료 (패턴없음)"
        sys.stdout.write(f"\r[{idx}/{len(file_list)}] {filename}  ... {file_status}                     \n")
        sys.stdout.flush()
        scan_log.append((filename, file_status, encoding_used))

    return detected_files, results, scan_log

def prompt_masking():
    root = tk.Tk()
    root.withdraw()
    result = messagebox.askyesno("치환 확인", "검출된 시스템 정보를 모두 Null로 치환 하시겠습니까?\n(Y: 마스킹 실행 / N: 취소)")
    root.destroy()
    return result

def mask_files(results, patterns):
    from collections import defaultdict
    file_matches = defaultdict(list)
    for res in results:
        file_matches[res['file']].append(res)
    masked_file_list = []

    for filename, matches in file_matches.items():
        lines, encoding_used = try_open_lines(filename)
        if lines is None:
            continue

        line_map = defaultdict(list)
        for match in matches:
            line_map[match['line'] - 1].append(match['pattern'])

        new_lines = []
        for idx, line in enumerate(lines):
            if idx in line_map:
                for pattern in line_map[idx]:
                    line = pattern.sub("", line)
            new_lines.append(line)

        dir_name = os.path.dirname(filename)
        base_name = os.path.basename(filename)
        masked_name = os.path.join(dir_name, "masked_" + base_name)
        with open(masked_name, "w", encoding=encoding_used, errors="ignore") as mf:
            mf.writelines(new_lines)
        masked_file_list.append((base_name, "masked_" + base_name))
    return masked_file_list

if __name__ == "__main__":
    patterns = {
        "IP주소": re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
        "비밀번호(PASS)": re.compile(r'\b(?:pass(word)?|pwd|passwd)\b[\s:;=,\'"]*\S+', re.IGNORECASE),
    }
    folder = select_folder()
    if folder:
        print(f"선택한 폴더: {folder}\n")
        detected_files, results, scan_log = scan_folder(folder, patterns)

        print("\n--- 전체 검사 결과 요약 ---")
        for i, (filename, status, enc) in enumerate(scan_log, 1):
            enc_info = f"[{enc}]" if enc else ""
            print(f"{i:4d}. {filename}   ... {status} {enc_info}")

        if results:
            print(f"\n=== 시스템 정보 검출된 파일: {len(detected_files)}개 ===")
            for i, f in enumerate(sorted(detected_files), 1):
                print(f"  {i}. {f}")
            print(f"\n=== 검출 상세 내역 ({len(results)}건) ===")
            for result in results:
                print(f"[{result['file']}:{result['line']}줄][{result['encoding']}]"
                      f"[{result['type']}] {result['content']}: {result['full_line']}")

            if prompt_masking():
                masked_files = mask_files(results, patterns)
                print("\n=== 치환(마스킹)된 파일 리스트 ===")
                for orig, masked in masked_files:
                    print(f"{orig} -> {masked}")
            else:
                print("치환(마스킹) 작업을 취소했습니다.")
        else:
            print("검사 대상 텍스트 파일은 있으나, 시스템 정보 패턴은 검출되지 않았습니다.")
    else:
        print("폴더를 선택하지 않았습니다.")
