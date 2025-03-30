import os
import re
import sys

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Удаляем многострочные комментарии в виде строк документации
    content = re.sub(r'""".*?"""', '', content, flags=re.DOTALL)
    content = re.sub(r"'''.*?'''", '', content, flags=re.DOTALL)
    
    # Обработка построчно для удаления однострочных комментариев
    lines = content.split('\n')
    processed_lines = []
    for line in lines:
        # Удаляем комментарии, начинающиеся с # в середине строки или в начале строки
        line = re.sub(r'#.*$', '', line)
        # Если строка не пустая или содержит не только пробелы
        if line.strip():
            processed_lines.append(line)
    
    # Убираем лишние пустые строки (оставляем не более одной)
    result = []
    prev_empty = False
    for line in processed_lines:
        if line.strip():
            result.append(line)
            prev_empty = False
        elif not prev_empty:
            result.append(line)
            prev_empty = True
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(result))
    
    print(f"Обработан файл: {file_path}")

def find_python_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                yield os.path.join(root, file)

def main():
    if len(sys.argv) > 1:
        directories = sys.argv[1:]
    else:
        directories = ['.']
    
    for directory in directories:
        for file_path in find_python_files(directory):
            process_file(file_path)

if __name__ == '__main__':
    main() 