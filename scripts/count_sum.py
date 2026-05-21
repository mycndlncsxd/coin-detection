import os
from argparse import ArgumentParser

def count_sum(input_dir):
    print(f"[LOG] Начало работы. Директория: {input_dir}")
    print(f"[LOG] Проверка существования директории: {os.path.exists(input_dir)}")
    
    input_txt_list = os.listdir(input_dir)
    print(f"[LOG] Найдено файлов в директории: {len(input_txt_list)}")
    if len(input_txt_list) > 0:
        print(f"[LOG] Первые 5 файлов: {input_txt_list[:5]}")

    list_of_classes = {
                        '0': 10,   # rub_10 = класс 0
                        '1': 5,    # rub_5 = класс 1
                        '2': 2,    # rub_2 = класс 2
                        '3': 1,    # rub_1 = класс 3
    }
    print(f"[LOG] Словарь классов: {list_of_classes}")
    
    dicts_list = []
    txt_files_processed = 0
    
    for txt in input_txt_list:
        file_path = os.path.join(input_dir, txt)
        print(f"[LOG] Обработка файла: {txt}")
        print(f"[LOG] Полный путь: {file_path}")
        
        if not os.path.isfile(file_path):
            print(f"[LOG] Пропуск (не файл): {txt}")
            continue
            
        if not txt.endswith('.txt'):
            print(f"[LOG] Пропуск (не txt): {txt}")
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = f.readlines()
                print(f"[LOG] Прочитано строк в файле {txt}: {len(data)}")
                
                summa = 0
                line_count = 0
                
                for string in data:
                    line_count += 1
                    string = string.strip()
                    if not string:
                        print(f"[LOG] Файл {txt}, строка {line_count}: пустая строка")
                        continue
                        
                    class_id = string[0]
                    print(f"[LOG] Файл {txt}, строка {line_count}: class_id='{class_id}'")
                    
                    if class_id in list_of_classes:
                        value = list_of_classes[class_id]
                        summa += value
                        print(f"[LOG]   -> добавлено {value}, текущая сумма: {summa}")
                    else:
                        print(f"[LOG]   ⚠️ класс '{class_id}' не найден в словаре")
                
                dict_txt_sum = {txt: summa}
                dicts_list.append(dict_txt_sum)
                txt_files_processed += 1
                print(f"[LOG] Файл {txt} обработан. Сумма: {summa}")
                
        except Exception as e:
            print(f"[LOG] ❌ Ошибка при обработке {txt}: {e}")
    
    print(f"[LOG] Обработано txt файлов: {txt_files_processed}")
    print(f"[LOG] Результатов в dicts_list: {len(dicts_list)}")
    
    with open('result.txt', 'w', encoding='utf-8') as f:
        for dict_item in dicts_list:
            for key, value in dict_item.items():
                output_line = f"{key}: {value}\n"
                f.write(output_line)
                print(f"Сумма на {key}: {value}")
    
    print(f"[LOG] Результат сохранен в result.txt")
    print(f"[LOG] Работа завершена")

if __name__ == "__main__":
    print("[LOG] Запуск скрипта")
    parser = ArgumentParser()
    parser.add_argument("-a", required=True, help='Путь до txt')
    args = parser.parse_args()
    print(f"[LOG] Получен аргумент -a: {args.a}")
    count_sum(args.a)
    print("[LOG] Скрипт завершен")