#!/usr/bin/env python3
import os
import re

def fix_indentation(file_path):
    """파일의 들여쓰기를 수정합니다."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    for line in lines:
        # 빈 줄은 그대로
        if line.strip() == '':
            fixed_lines.append(line)
            continue
            
        # 들여쓰기 레벨 계산
        stripped = line.lstrip()
        if not stripped:
            fixed_lines.append(line)
            continue
            
        # 원래 들여쓰기 공백 개수 계산
        indent_count = len(line) - len(stripped)
        
        # 8 또는 12 스페이스를 4의 배수로 조정
        if indent_count >= 12:
            new_indent = 12  # 3단계 들여쓰기
        elif indent_count >= 8:
            new_indent = 8   # 2단계 들여쓰기
        elif indent_count >= 4:
            new_indent = 4   # 1단계 들여쓰기
        else:
            new_indent = 0   # 들여쓰기 없음
            
        fixed_line = ' ' * new_indent + stripped
        fixed_lines.append(fixed_line)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)

# 파일들 수정
files_to_fix = [
    '/home/ksw6895/Projects/test250703/modules/gemini_client.py',
    '/home/ksw6895/Projects/test250703/modules/report_generator.py'
]

for file_path in files_to_fix:
    print(f"Fixing {file_path}...")
    fix_indentation(file_path)
    print(f"Fixed {file_path}")

print("All files fixed!")