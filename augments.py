import pyarrow.parquet as pq
import pandas as pd
import io
import numpy as np
from PIL import Image
import albumentations as A
from nlpaug.augmenter.word import SynonymAug
import pyarrow as pa
import os
import random

# Конфигурация
INPUT_PARQUET = './Datasets/dataset1.parquet'
OUTPUT_PARQUET = 'augmented_data.parquet'
NUM_AUGMENTATIONS = 3  # Количество аугментированных вариантов для каждого оригинала
IMAGE_SIZE = (224, 224)  # Размер для ресайза изображений

# Определим аугментации для изображений
image_augmenter = A.Compose([
    A.HorizontalFlip(p=0.5),
    A.Rotate(limit=30, p=0.5),
    A.RandomBrightnessContrast(p=0.3),
    A.GaussianBlur(blur_limit=(3, 7), p=0.2),
    A.Resize(*IMAGE_SIZE)
])

# Определим аугментации для текста
text_augmenter = SynonymAug(aug_src='wordnet')


def process_dataset():
    # Чтение исходных данных
    df = pq.read_table(INPUT_PARQUET).to_pandas()

    augmented_data = []

    for idx, row in df.iterrows():
        # Обработка изображений
        img_data = row['image']
        original_bytes = img_data['bytes']

        try:
            image = Image.open(io.BytesIO(original_bytes)).convert('RGB')
            np_image = np.array(image)
        except Exception as e:
            print(f"Error loading image {idx}: {str(e)}")
            continue

        # Обработка текста
        original_text = row['text']

        # Генерируем аугментированные варианты
        for aug_idx in range(NUM_AUGMENTATIONS):
            try:
                # Аугментация изображения
                augmented_image = image_augmenter(image=np_image)['image']
                pil_image = Image.fromarray(augmented_image)

                # Сохраняем изображение в bytes
                img_byte_arr = io.BytesIO()
                pil_image.save(img_byte_arr, format='JPEG')
                img_bytes = img_byte_arr.getvalue()

                # Аугментация текста
                augmented_text = text_augmenter.augment(original_text)

                # Сохраняем метаданные
                augmented_data.append({
                    'original_id': idx,
                    'augmentation_id': aug_idx,
                    'image': {
                        'bytes': img_bytes,
                        'Color': img_data.get('Color'),
                        'Department': img_data.get('Department')
                    },
                    'text': augmented_text,
                    'image_size': f"{IMAGE_SIZE[0]}x{IMAGE_SIZE[1]}"
                })

            except Exception as e:
                print(f"Error in augmentation {aug_idx} for sample {idx}: {str(e)}")

        # Сохраняем оригинал с пометкой
        augmented_data.append({
            'original_id': idx,
            'augmentation_id': -1,  # -1 означает оригинал
            'image': img_data,
            'text': original_text,
            'image_size': 'original'
        })

    # Создаем DataFrame и сохраняем в Parquet
    augmented_df = pd.DataFrame(augmented_data)

    # Определяем схему для PyArrow
    schema = pa.schema([
        ('original_id', pa.int32()),
        ('augmentation_id', pa.int8()),
        ('image', pa.struct([
            ('bytes', pa.binary()),
            ('Color', pa.string()),
            ('Department', pa.string())
        ])),
        ('text', pa.string()),
        ('image_size', pa.string())
    ])

    table = pa.Table.from_pandas(augmented_df, schema=schema)
    pq.write_table(table, OUTPUT_PARQUET, compression='SNAPPY')

    print(f"Аугментация завершена. Сохранено {len(augmented_df)} записей в {OUTPUT_PARQUET}")


if __name__ == "__main__":
    process_dataset()