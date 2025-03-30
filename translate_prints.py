import os
import re
import sys

# Словарь замен для сообщений в print
TRANSLATIONS = {
    # RabbitMQ сообщения
    "Спроба підключення до RabbitMQ": "Спроба підключення до RabbitMQ",
    "Успішне підключення до RabbitMQ": "Успішне підключення до RabbitMQ",
    "Помилка підключення до RabbitMQ": "Помилка підключення до RabbitMQ",
    "Спроба": "Спроба",
    "Не вдалося підключитися до RabbitMQ після": "Не вдалося підключитися до RabbitMQ після",
    "спроб": "спроб",
    "Неможливо відправити повідомлення: немає з'єднання з RabbitMQ": "Неможливо відправити повідомлення: немає з'єднання з RabbitMQ",
    "Помилка відправки повідомлення": "Помилка відправки повідомлення",
    "Неможливо отримувати повідомлення: немає з'єднання з RabbitMQ": "Неможливо отримувати повідомлення: немає з'єднання з RabbitMQ",
    "Очікування повідомлень з черги": "Очікування повідомлень з черги",
    "Для виходу натисніть CTRL+C": "Для виходу натисніть CTRL+C",
    "Помилка отримання повідомлень": "Помилка отримання повідомлень",
    "Помилка обробки повідомлення": "Помилка обробки повідомлення", 
    
    # API сообщения
    "Запуск API-сервера на порту": "Запуск API-сервера на порту",
    
    # Billing сообщения
    "Отримано результат для лічильника": "Отримано результат для лічильника",
    "Новий лічильник": "Новий лічильник",
    "Споживання (день)": "Споживання (день)",
    "Споживання (ніч)": "Споживання (ніч)",
    "Вартість (день)": "Вартість (день)",
    "Вартість (ніч)": "Вартість (ніч)",
    "Загальна вартість": "Загальна вартість",
    "Помилка обробки результату": "Помилка обробки результату"
}

def translate_prints(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Заменяем сообщения в функциях print
    for ru, uk in TRANSLATIONS.items():
        # Ищем print с этой строкой внутри и заменяем
        pattern = f'print\\(.*?{re.escape(ru)}.*?\\)'
        for match in re.finditer(pattern, content):
            original = match.group(0)
            translated = original.replace(ru, uk)
            content = content.replace(original, translated)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
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
            translate_prints(file_path)

if __name__ == '__main__':
    main() 