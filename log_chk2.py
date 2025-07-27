import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import glob
import os
import re
import chardet


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
    file_list = [f for f in all_files if os.path.isfile(f) and is_text_file(f)]
    detected_files = set()
    results = []
    for filename in file_list:
        lines, encoding_used = try_open_lines(filename)
        if lines is None:
            continue
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
            detected_files.add(filename)
    return detected_files, results


def prompt_masking():
    root = tk.Tk()
    root.withdraw()
    result = messagebox.askyesno("치환 확인", "검출된 시스템 정보를 모두 Null로 치환 하시겠습니까?\n(Y: 마스킹 실행 / N: 취소)")
    root.destroy()
    return result


def mask_files(results, patterns):
    # 파일별로 묶기
    from collections import defaultdict
    file_matches = defaultdict(list)
    for res in results:
        file_matches[res['file']].append(res)
    masked_file_list = []

    for filename, matches in file_matches.items():
        # 한 파일 내 여러줄, 여러 패턴이 있을 수 있으니 전부 마스킹
        lines, encoding_used = try_open_lines(filename)
        if lines is None:
            continue  # 예외 방지

        # 마스킹할 라인/패턴 정보로 변환
        # {라인번호: [(패턴, 치환값), ...]} 식으로 구성
        line_map = defaultdict(list)
        for match in matches:
            line_map[match['line'] - 1].append(match['pattern'])

        # 라인별 마스킹
        new_lines = []
        for idx, line in enumerate(lines):
            # 이 줄에 마스킹할 패턴이 있으면 반복해서 Null 치환
            if idx in line_map:
                for pattern in line_map[idx]:
                    line = pattern.sub("", line)
            new_lines.append(line)

        # 저장
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
        print(f"선택한 폴더: {folder}")
        detected_files, results = scan_folder(folder, patterns)
        if results:
            print(f"\n=== 시스템 정보 검출된 파일: {len(detected_files)}개 ===")
            for i, f in enumerate(sorted(detected_files), 1):
                print(f"  {i}. {f}")
            print(f"\n=== 검출 상세 내역 ({len(results)}건) ===")
            for result in results:
                print(f"[{result['file']}:{result['line']}줄][{result['encoding']}]"
                      f"[{result['type']}] {result['content']}: {result['full_line']}")

            # --- 치환 확인 프롬프트
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
