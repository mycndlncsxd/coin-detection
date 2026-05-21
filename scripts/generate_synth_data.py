"""
Генератор синтетических данных с монетами
Папки:
    backgrounds/ - фоновые изображения (любые форматы)
    coins/ - изображения монет на прозрачном фоне (PNG)
        rub_1/ - папка с монетами 1 рубль (класс 0)
        rub_2/ - папка с монетами 2 рубля (класс 1)
        rub_5/ - папка с монетами 5 рублей (класс 2)
        rub_10/ - папка с монетами 10 рублей (класс 3)
Результат:
    output/
        images/ - сгенерированные изображения
        labels/ - YOLO аннотации
"""

import os
import random
import numpy as np
from pathlib import Path
from PIL import Image, ImageEnhance, ImageDraw, ImageOps

# ========== НАСТРОЙКИ ==========
BACKGROUNDS_DIR = "/home/matan/Desktop/STUDYING/COURSE_Classwork/data/dataset_v8_synth/bg"
COINS_DIR = "/home/matan/Desktop/STUDYING/COURSE_Classwork/data/dataset_v8_synth/coins"
OUTPUT_DIR = "/home/matan/Desktop/STUDYING/COURSE_Classwork/data/dataset_v8_synth/result"
NUM_IMAGES = 100
MIN_COINS = 2
MAX_COINS = 10
OUTPUT_SIZE = (640, 640)

# Настройки аугментации
BRIGHTNESS_RANGE = (0.8, 1.2)
CONTRAST_RANGE = (0.8, 1.2)
BRIGHTNESS_PROB = 0.6
CONTRAST_PROB = 0.6

# Настройки монет
MIN_COIN_SIZE_PERCENT = 12  # минимальный размер монеты в процентах от фона
MAX_COIN_SIZE_PERCENT = 17  # максимальный размер монеты в процентах от фона
MIN_DISTANCE = 20  # минимальное расстояние между монетами в пикселях
# ================================

# Маппинг классов (папка -> class_id)
CLASS_MAPPING = {
    "rub_10": 0,
    "rub_5": 1,
    "rub_2": 2,
    "rub_1": 3,
}

def load_backgrounds(bg_dir):
    """Загружает все фоновые изображения"""
    bg_dir = Path(bg_dir)
    backgrounds = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
        backgrounds.extend(bg_dir.glob(ext))
    print(f"📁 Загружено фонов: {len(backgrounds)}")
    return backgrounds

def load_coins(coins_dir):
    """Загружает монеты из папок (папка = класс)"""
    coins_dir = Path(coins_dir)
    coins = {}
    
    for class_name, class_id in CLASS_MAPPING.items():
        class_dir = coins_dir / class_name
        if class_dir.exists():
            coins[class_id] = list(class_dir.glob("*.png"))
            print(f"   Класс {class_id} ({class_name}): {len(coins[class_id])} монет")
        else:
            print(f"   ⚠️ Папка не найдена: {class_dir}")
    
    return coins

def get_non_transparent_bbox(image):
    """
    Возвращает bounding box непрозрачной области изображения
    Возвращает (x_min, y_min, x_max, y_max)
    """
    # Конвертируем в numpy array
    if image.mode == 'RGBA':
        alpha = np.array(image.split()[-1])
        # Находим где альфа-канал > 0 (непрозрачные пиксели)
        non_transparent = np.where(alpha > 0)
        if len(non_transparent[0]) > 0:
            y_min = np.min(non_transparent[0])
            y_max = np.max(non_transparent[0])
            x_min = np.min(non_transparent[1])
            x_max = np.max(non_transparent[1])
            return x_min, y_min, x_max, y_max
    return 0, 0, image.width, image.height

def random_resize_rotate(coin, bg_width, bg_height):
    """
    Случайный размер и поворот
    Возвращает трансформированную монету и её реальный bounding box
    """
    # Определяем целевой размер (по непрозрачной области)
    orig_bbox = get_non_transparent_bbox(coin)
    orig_width = orig_bbox[2] - orig_bbox[0]
    orig_height = orig_bbox[3] - orig_bbox[1]
    
    # Размер монеты в процентах от фона
    max_size = min(bg_width, bg_height)
    target_size_percent = random.randint(MIN_COIN_SIZE_PERCENT, MAX_COIN_SIZE_PERCENT)
    target_size = int(max_size * target_size_percent / 100)
    
    # Масштабируем по максимальной стороне
    scale = target_size / max(orig_width, orig_height)
    new_w = int(coin.width * scale)
    new_h = int(coin.height * scale)
    
    # Изменяем размер
    coin_resized = coin.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Поворачиваем
    angle = random.randint(0, 360)
    coin_rotated = coin_resized.rotate(angle, expand=True, 
                                        resample=Image.Resampling.BICUBIC)
    
    # Получаем bounding box непрозрачной области после поворота
    final_bbox = get_non_transparent_bbox(coin_rotated)
    
    return coin_rotated, final_bbox

def random_position(coin_bbox, bg_width, bg_height, existing_boxes, min_distance=MIN_DISTANCE):
    """
    Случайная позиция без сильного перекрытия с другими монетами
    coin_bbox: (x_min, y_min, x_max, y_max) относительные координаты внутри монеты
    """
    max_attempts = 50
    # Размер bounding box'а монеты
    coin_w = coin_bbox[2] - coin_bbox[0]
    coin_h = coin_bbox[3] - coin_bbox[1]
    
    for attempt in range(max_attempts):
        x = random.randint(0, max(0, bg_width - coin_w))
        y = random.randint(0, max(0, bg_height - coin_h))
        
        # Проверяем перекрытие с существующими монетами
        overlap = False
        for (ex, ey, ew, eh) in existing_boxes:
            if (x < ex + ew + min_distance and 
                x + coin_w + min_distance > ex and
                y < ey + eh + min_distance and 
                y + coin_h + min_distance > ey):
                overlap = True
                break
        
        if not overlap:
            return x, y
    
    return 0, 0

def apply_random_brightness(image, prob=BRIGHTNESS_PROB, brightness_range=BRIGHTNESS_RANGE):
    """Случайное изменение яркости"""
    if random.random() < prob:
        factor = random.uniform(brightness_range[0], brightness_range[1])
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(factor)
    return image

def apply_random_contrast(image, prob=CONTRAST_PROB, contrast_range=CONTRAST_RANGE):
    """Случайное изменение контраста"""
    if random.random() < prob:
        factor = random.uniform(contrast_range[0], contrast_range[1])
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(factor)
    return image

def apply_augmentations(image):
    """Применяет все аугментации"""
    image = apply_random_brightness(image)
    image = apply_random_contrast(image)
    return image

def generate_synthetic_dataset(backgrounds, coins, output_dir, num_images):
    """Генерирует синтетический датасет"""
    
    output_images = output_dir / "images"
    output_labels = output_dir / "labels"
    output_images.mkdir(parents=True, exist_ok=True)
    output_labels.mkdir(parents=True, exist_ok=True)
    
    for img_idx in range(num_images):
        # 1. Загружаем случайный фон
        bg_path = random.choice(backgrounds)
        bg = Image.open(bg_path).convert("RGB")
        
        # 2. Изменяем размер фона до OUTPUT_SIZE
        bg.thumbnail(OUTPUT_SIZE, Image.Resampling.LANCZOS)
        bg_width, bg_height = bg.size
        
        # 3. Решаем сколько монет будет
        num_coins = random.randint(MIN_COINS, MAX_COINS)
        annotations = []
        boxes = []  # хранит (x, y, width, height) в пикселях для bounding box'ов
        
        for coin_num in range(num_coins):
            # 4. Выбираем случайный класс и монету
            class_id = random.choice(list(coins.keys()))
            coin_path = random.choice(coins[class_id])
            coin_orig = Image.open(coin_path).convert("RGBA")
            
            # 5. Изменяем размер и поворачиваем монету, получаем bounding box
            coin_transformed, coin_bbox = random_resize_rotate(coin_orig, bg_width, bg_height)
            
            # Размер bounding box'а монеты
            coin_w = coin_bbox[2] - coin_bbox[0]
            coin_h = coin_bbox[3] - coin_bbox[1]
            
            # 6. Ищем позицию для монеты на фоне
            x, y = random_position(coin_bbox, bg_width, bg_height, boxes)
            
            # Сохраняем bounding box для проверки перекрытий
            boxes.append((x, y, coin_w, coin_h))
            
            # 7. Вырезаем bounding box из монеты и накладываем
            # Обрезаем монету по bounding box'у
            coin_cropped = coin_transformed.crop((coin_bbox[0], coin_bbox[1], 
                                                   coin_bbox[2], coin_bbox[3]))
            
            # Накладываем только непрозрачную часть
            bg.paste(coin_cropped, (x, y), coin_cropped)
            
            # 8. Создаем YOLO аннотацию (нормализованные координаты)
            x_center = (x + coin_w / 2) / bg_width
            y_center = (y + coin_h / 2) / bg_height
            width_norm = coin_w / bg_width
            height_norm = coin_h / bg_height
            
            # Проверяем, что координаты в пределах [0,1]
            x_center = max(0.0, min(1.0, x_center))
            y_center = max(0.0, min(1.0, y_center))
            width_norm = max(0.0, min(1.0, width_norm))
            height_norm = max(0.0, min(1.0, height_norm))
            
            annotations.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width_norm:.6f} {height_norm:.6f}")
        
        # 9. Аугментация итогового изображения
        bg = apply_augmentations(bg)
        
        # 10. Сохраняем изображение и аннотации
        img_name = f"synth_{img_idx:06d}.jpg"
        txt_name = img_name.replace(".jpg", ".txt")
        
        bg.save(output_images / img_name, quality=95)
        
        with open(output_labels / txt_name, "w") as f:
            f.write("\n".join(annotations))
        
        # Прогресс
        if (img_idx + 1) % 10 == 0:
            print(f"   Сгенерировано {img_idx + 1}/{num_images}")
    
    print(f"\n✅ Готово! Сохранено в {output_dir}")
    print(f"   Изображения: {output_images}")
    print(f"   Аннотации:   {output_labels}")

def verify_random_image(output_dir, num_verifications=5):
    """
    Визуальная проверка совпадения аннотаций с монетами
    Создает изображения с рамками для проверки
    """
    output_dir = Path(output_dir)
    images_dir = output_dir / "images"
    labels_dir = output_dir / "labels"
    verify_dir = output_dir / "verification"
    verify_dir.mkdir(exist_ok=True)
    
    # Получаем список всех изображений
    images = list(images_dir.glob("*.jpg"))
    if not images:
        print("❌ Нет изображений для проверки")
        return
    
    # Выбираем случайные изображения для проверки
    to_verify = random.sample(images, min(num_verifications, len(images)))
    
    print(f"\n🔍 Верификация {len(to_verify)} случайных изображений...")
    
    for img_path in to_verify:
        label_path = labels_dir / img_path.name.replace(".jpg", ".txt")
        
        if not label_path.exists():
            print(f"   ⚠️ Нет аннотации для {img_path.name}")
            continue
        
        # Открываем изображение
        img = Image.open(img_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # Читаем аннотации
        with open(label_path, 'r') as f:
            lines = f.readlines()
        
        colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange']
        
        for i, line in enumerate(lines):
            parts = line.strip().split()
            if len(parts) == 5:
                class_id, x_center, y_center, w_norm, h_norm = parts
                
                # Конвертируем обратно в пиксели
                x_center_px = float(x_center) * width
                y_center_px = float(y_center) * height
                w_px = float(w_norm) * width
                h_px = float(h_norm) * height
                
                # Вычисляем координаты прямоугольника
                x1 = int(x_center_px - w_px / 2)
                y1 = int(y_center_px - h_px / 2)
                x2 = int(x_center_px + w_px / 2)
                y2 = int(y_center_px + h_px / 2)
                
                # Рисуем рамку
                color = colors[int(class_id) % len(colors)]
                draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
                draw.text((x1, y1-15), f"Class {class_id}", fill=color)
        
        # Сохраняем верифицированное изображение
        verify_path = verify_dir / img_path.name
        img.save(verify_path)
        print(f"   ✅ Сохранено: {verify_path}")
    
    print(f"\n📁 Проверочные изображения сохранены в {verify_dir}")

def main():
    print("=" * 50)
    print("ГЕНЕРАТОР СИНТЕТИЧЕСКИХ МОНЕТ")
    print("=" * 50)
    
    # Проверка папок
    if not Path(BACKGROUNDS_DIR).exists():
        print(f"❌ Папка {BACKGROUNDS_DIR} не найдена!")
        return
    
    if not Path(COINS_DIR).exists():
        print(f"❌ Папка {COINS_DIR} не найдена!")
        return
    
    # Загрузка данных
    backgrounds = load_backgrounds(BACKGROUNDS_DIR)
    if not backgrounds:
        print(f"❌ Нет фонов в папке {BACKGROUNDS_DIR}!")
        return
    
    coins = load_coins(COINS_DIR)
    total_coins = sum(len(v) for v in coins.values())
    if total_coins == 0:
        print(f"❌ Нет монет в папке {COINS_DIR}!")
        return
    
    # Вывод настроек
    print(f"\n📊 Параметры:")
    print(f"   Изображений: {NUM_IMAGES}")
    print(f"   Монет на изображение: {MIN_COINS}-{MAX_COINS}")
    print(f"   Размер монет: {MIN_COIN_SIZE_PERCENT}-{MAX_COIN_SIZE_PERCENT}% от фона")
    print(f"   Размер выходных изображений: {OUTPUT_SIZE[0]}x{OUTPUT_SIZE[1]}")
    print(f"   Яркость: {BRIGHTNESS_RANGE[0]}..{BRIGHTNESS_RANGE[1]} (вероятность {BRIGHTNESS_PROB*100:.0f}%)")
    print(f"   Контраст: {CONTRAST_RANGE[0]}..{CONTRAST_RANGE[1]} (вероятность {CONTRAST_PROB*100:.0f}%)")
    print(f"   Мин. расстояние между монетами: {MIN_DISTANCE}px")
    
    # Генерация
    print(f"\n🔨 Генерация...")
    generate_synthetic_dataset(backgrounds, coins, Path(OUTPUT_DIR), NUM_IMAGES)
    
    # Верификация (проверка корректности аннотаций)
    print(f"\n🔍 Проверка корректности аннотаций...")
    verify_random_image(Path(OUTPUT_DIR), num_verifications=5)
    
    print("\n✨ Скрипт успешно завершен!")

if __name__ == "__main__":
    main()