import cv2
import numpy as np
import os
from pathlib import Path

def draw_yolo_boxes(image_path, txt_path, class_names=None, colors=None, output_path=None):
    """
    Рисует bounding boxes на изображении из YOLO формата аннотаций
    
    Args:
        image_path: путь к изображению
        txt_path: путь к txt файлу с аннотациями
        class_names: список названий классов (опционально)
        colors: словарь цветов для классов (опционально)
        output_path: путь для сохранения результата (опционально)
    """
    # Загрузка изображения
    img = cv2.imread(image_path)
    if img is None:
        print(f"Ошибка: не удалось загрузить изображение {image_path}")
        return
    
    img_height, img_width = img.shape[:2]
    
    # Чтение аннотаций
    if not os.path.exists(txt_path):
        print(f"Ошибка: файл аннотаций {txt_path} не найден")
        return
    
    with open(txt_path, 'r') as f:
        lines = f.readlines()
    
    if not lines:
        print("Аннотации не найдены")
        return
    
    # Генерация случайных цветов если не указаны
    if colors is None:
        colors = {}
    
    # Отрисовка каждого бокса
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        parts = line.split()
        if len(parts) != 5:
            print(f"Неверный формат строки: {line}")
            continue
            
        class_id = int(parts[0])
        x_center = float(parts[1])
        y_center = float(parts[2])
        width = float(parts[3])
        height = float(parts[4])
        
        # Конвертация нормализованных координат в пиксельные
        x1 = int((x_center - width / 2) * img_width)
        y1 = int((y_center - height / 2) * img_height)
        x2 = int((x_center + width / 2) * img_width)
        y2 = int((y_center + height / 2) * img_height)
        
        # Получение цвета для класса
        if class_id in colors:
            color = colors[class_id]
        else:
            # Генерация случайного цвета
            color = tuple(np.random.randint(0, 255, 3).tolist())
            colors[class_id] = color
            
        # Отрисовка прямоугольника
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        
        # Добавление метки класса
        label = class_names[class_id] if class_names and class_id < len(class_names) else f"Class {class_id}"
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
        
        # Фон для текста
        cv2.rectangle(img, (x1, y1 - label_size[1] - 5), (x1 + label_size[0], y1), color, -1)
        # Текст
        cv2.putText(img, label, (x1, y1 - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Сохранение или отображение результата
    if output_path:
        cv2.imwrite(output_path, img)
        print(f"Результат сохранен в {output_path}")
    else:
        # Отображение изображения
        cv2.imshow('Bounding Boxes', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def process_directory(image_dir, txt_dir, class_names=None, output_dir=None):
    """
    Обрабатывает все изображения в директории с соответствующими txt файлами
    
    Args:
        image_dir: директория с изображениями
        txt_dir: директория с txt аннотациями
        class_names: список названий классов
        output_dir: директория для сохранения результатов (опционально)
    """
    # Создание директории для результатов если нужно
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Поиск всех изображений
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    images = []
    
    for ext in image_extensions:
        images.extend(Path(image_dir).glob(f'*{ext}'))
        images.extend(Path(image_dir).glob(f'*{ext.upper()}'))
    
    if not images:
        print(f"Изображения не найдены в {image_dir}")
        return
    
    print(f"Найдено {len(images)} изображений")
    
    # Случайные цвета для разных классов
    colors = {}
    
    # Обработка каждого изображения
    for img_path in images:
        txt_path = Path(txt_dir) / f"{img_path.stem}.txt"
        
        if not txt_path.exists():
            print(f"Предупреждение: аннотация не найдена для {img_path.name}")
            continue
            
        print(f"Обработка {img_path.name}...")
        
        output_path = None
        if output_dir:
            output_path = Path(output_dir) / img_path.name
            
        draw_yolo_boxes(str(img_path), str(txt_path), class_names, colors, output_path)

# Пример использования
if __name__ == "__main__":
    # Пример названий классов (замените на свои)
    class_names = [
        "rub_10", "rub_5", "rub_2", "rub_1"
    ]
    
    # Вариант 1: Отображение одного изображения
    # draw_yolo_boxes("image.jpg", "image.txt", class_names)
    
    # Вариант 2: Пакетная обработка директории
    process_directory(
        image_dir="/home/matan/Desktop/STUDYING/COURSE_Classwork/data/dataset_all_v2/dataset_v1_fixed/merged",      # Директория с изображениями
        txt_dir="/home/matan/Desktop/STUDYING/COURSE_Classwork/data/dataset_all_v2/dataset_v1_fixed/merged",         # Директория с txt файлами
        class_names=class_names,   # Названия классов (опционально)
        output_dir="/home/matan/Desktop/STUDYING/COURSE_Classwork/data/dataset_all_v2/dataset_v1_fixed/images_with_boxes"       # Директория для сохранения (опционально)
    )