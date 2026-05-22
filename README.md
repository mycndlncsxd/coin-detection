## Проект курсовой работы: распознавание монет (1, 2, 5, 10 рублей) на фотографиях и автоматический подсчёт суммы.
# Структура репозитория:
```
├── scripts/                   # все скрипты проекта
│   ├── count_sum.py           # подсчёт суммы по аннотациям
│   ├── generate_synth_data.py # генератор синтетических данных
│   ├── heic_to_jpg.py         # конвертер HEIC → JPG
│   ├── rename_files_from_n.py # переименование файлов
│   ├── show_boxes_txt.py      # визуализация YOLO аннотаций
│   └── via6.html              # VGG Image Annotator (разметка)
├── weights/                   # веса обученной модели
│   └── yolo26s_640_weak_aug_fix/
│       └── best.pt
├── .gitignore                 # исключённые из Git файлы
├── README.md                  # этот файл
├── yamls/		               # .yaml файлы с директориями и параметрами 
│   ├── train.yaml	           # параметры обучения
│   └── coins.yaml	           # директории и классы
└── runs/		               # тестирование модели
    └── yolo26s_640_weak_aug_fix
        └── conf_0.15	       # confidence = 0.15 для наглядности
```
# Установка:
## Клонировать репозиторий
```
git clone https://github.com/mycndlncsxd/coin-detection.git
cd coin-detection
```
## Создать виртуальное окружение
```
python -m venv venv
source venv/bin/activate  # только для Linux/Mac
```
## Установить зависимости
```
pip install ultralytics pillow opencv-python imutils imagesize progressbar2
```
# Скрипты:
1) Генерация синтетических данных с монетами на случайных фонах. Настройки находятся внутри скрипта.

2) Подсчёт суммы сканирует YOLO аннотации и считает общую сумму.

3) Визуализация аннотаций рисует bounding boxes на изображениях.

4) Конвертация HEIC → JPG

5) Переименование файлов с определенного номера (для порядка в датасете)

6) via6.html представляет собой проработанный инструмент для разметки данных

# Обучение модели
Модель обучена на архитектуре YOLOv26s с параметрами:
```
data: /mnt/data/projects/coins_counter/dataset_all_v2/coins.yaml
epochs: 100
batch: 6
imgsz: 640
save: True
device: 0
exist_ok: True
workers: 8
patience: 100
project: coins_counter
name: yolo26s_2026-05-21_640_weak_aug_fix
optimizer: auto
save: True
save_period: 5
hsv_h: 0.005    # очень слабое изменение цвета (±0.5%)
hsv_s: 0.2      # слабое изменение насыщенности
hsv_v: 0.2      # слабое изменение яркости
degrees: 180 
translate: 0.05 # сдвиг на 5%
scale: 0.2      # масштаб 0.8x до 1.2x
shear: 0.0
perspective: 0.0
flipud: 0.0
fliplr: 0.0
mosaic: 0.0
mixup: 0.0
copy_paste: 0.0
```
# Визуализация
В папке plots представлены графики, демонстрирующие различные метрики

# Примеры работы модели
Находятся в папке runs
