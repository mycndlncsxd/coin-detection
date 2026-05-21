import os
import json
import pandas as pd
from PIL import Image, ImageDraw

CSV_PATH = "/Users/plnmsv/Desktop/work/Нарушена_целостность_искусственной_дорожной_неровности_FP.csv"
IMAGES_DIR = "/Users/plnmsv/Desktop/work/test/FP"
OUTPUT_DIR = "/Users/plnmsv/Desktop/work/test/bbox"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def normalize_image_name(filename: str) -> str:
    """
    Преобразует имя файла:
    1_7f06ac39-0aea-4cc9-915b-107a46fc31e5.jpg
    -> 7f06ac39-0aea-4cc9-915b-107a46fc31e5
    """
    name = os.path.splitext(filename)[0]
    return name.split("_", 1)[-1]


# строим мапу: uuid -> реальное имя файла
image_map = {}
for img_name in os.listdir(IMAGES_DIR):
    normalized = normalize_image_name(img_name)
    image_map[normalized] = img_name


# читаем CSV (новая структура)
df = pd.read_csv(CSV_PATH, header=None)
df.columns = ["path", "class", "json_data", "label"]

for _, row in df.iterrows():
    csv_image_name = row["path"].split("/")[-1]

    if csv_image_name not in image_map:
        # print(f"[WARN] Фото не найдено: {csv_image_name}")
        continue

    image_filename = image_map[csv_image_name]
    image_path = os.path.join(IMAGES_DIR, image_filename)

    with Image.open(image_path) as img:
        draw = ImageDraw.Draw(img)

        data = json.loads(row["json_data"])
        bboxes = data.get("bBoxes", [])

        for box in bboxes:
            x0, y0 = box["x0"], box["y0"]
            x1, y1 = box["x1"], box["y1"]

            # рисуем бокс
            draw.rectangle([x0, y0, x1, y1], outline="red", width=3)

        # сохраняем результат
        out_path = os.path.join(OUTPUT_DIR, image_filename)
        img.save(out_path)

print("Отрисовка боксов завершена")
