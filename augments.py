# import pandas as pd
# import io
# import numpy as np
# from PIL import Image
# import albumentations as A
# from tqdm import tqdm
#
# df = pd.read_parquet('datasets/dataset1.parquet')
# print("Original DataFrame shape:", df.shape)
#
# albumentations_transform = A.Compose([
#     A.RandomScale(scale_limit=0.1, p=0.3),
#     A.Rotate(limit=(-15, 15)),
#     A.HorizontalFlip(p=0.5),
#     A.VerticalFlip(p=0.1),
#     A.GridDistortion(distort_limit=0.05, p=0.1),
#     A.PadIfNeeded(min_height=256, min_width=256, p=1.0),
#     ], bbox_params=A.BboxParams(format='pascal_voc', min_area=1024, min_visibility=0.1) if 'bbox' in df.columns else None)
#
#
# def augment_and_convert(image_data):
#     img_bytes = image_data['bytes'] if isinstance(image_data, dict) else image_data
#
#     img = Image.open(io.BytesIO(img_bytes))
#     img_np = np.array(img)
#
#     if len(img_np.shape) == 2:
#         img_np = np.expand_dims(img_np, axis=-1)
#
#     try:
#         if 'bbox' in image_data:
#             augmented = albumentations_transform(
#                 image=img_np,
#                 bboxes=[image_data['bbox']],
#                 class_labels=['dress'] if 'class' not in image_data else [image_data['class']]
#             )
#             augmented_img_np = augmented['image']
#             augmented_bbox = augmented['bboxes'][0] if augmented['bboxes'] else image_data['bbox']
#         else:
#             augmented = albumentations_transform(image=img_np)
#             augmented_img_np = augmented['image']
#     except Exception as e:
#         print(f"Error augmenting image: {e}")
#         augmented_img_np = img_np
#
#     augmented_img = Image.fromarray(augmented_img_np)
#     img_byte_arr = io.BytesIO()
#     augmented_img.save(img_byte_arr, format='PNG')
#
#     if isinstance(image_data, dict):
#         result = {
#             'bytes': img_byte_arr.getvalue(),
#             **{k: v for k, v in image_data.items() if k != 'bytes'}
#         }
#         if 'bbox' in image_data:
#             result['bbox'] = augmented_bbox
#         return result
#     else:
#         return img_byte_arr.getvalue()
#
#
# augmented_data = []
# for idx, row in tqdm(df.iterrows(), total=len(df)):
#     try:
#         augmented_row = row.copy()
#         augmented_row['image'] = augment_and_convert(row['image'])
#         augmented_data.append(augmented_row)
#     except Exception as e:
#         print(f"Error processing row {idx}: {e}")
#         augmented_data.append(row)
#
# augmented_df = pd.DataFrame(augmented_data)
#
# augmented_df.to_parquet('datasets/dataset1_augmented_safe.parquet', index=False)
# print("Augmented DataFrame saved to datasets/dataset1_augmented_safe.parquet")
# print("New DataFrame shape:", augmented_df.shape)


import pandas as pd
import io
import numpy as np
from PIL import Image
import albumentations as A
from tqdm import tqdm

df = pd.read_parquet('datasets/dataset1.parquet')
print("Original DataFrame shape:", df.shape)


albumentations_transform1 = A.Compose([
    A.RandomScale(scale_limit=(0.2, 0.6), p=0.3),
    A.HorizontalFlip(p=0.5),
], bbox_params=A.BboxParams(format='pascal_voc', min_area=1024, min_visibility=0.1) if 'bbox' in df.columns else None)

albumentations_transform2 = A.Compose([
    A.RandomScale(scale_limit=(0.2, 0.6), p=0.3),
    A.Rotate(limit=(5, 15)),
    A.GridDistortion(distort_limit=0.05, p=0.1),
    A.PadIfNeeded(min_height=256, min_width=256, p=1.0),
], bbox_params=A.BboxParams(format='pascal_voc', min_area=1024, min_visibility=0.1) if 'bbox' in df.columns else None)


def augment_and_convert(image_data, transform):
    img_bytes = image_data['bytes'] if isinstance(image_data, dict) else image_data

    img = Image.open(io.BytesIO(img_bytes))
    img_np = np.array(img)

    if len(img_np.shape) == 2:
        img_np = np.expand_dims(img_np, axis=-1)

    try:
        if 'bbox' in image_data:
            augmented = transform(
                image=img_np,
                bboxes=[image_data['bbox']],
                class_labels=['dress'] if 'class' not in image_data else [image_data['class']]
            )
            augmented_img_np = augmented['image']
            augmented_bbox = augmented['bboxes'][0] if augmented['bboxes'] else image_data['bbox']
        else:
            augmented = transform(image=img_np)
            augmented_img_np = augmented['image']
    except Exception as e:
        print(f"Error augmenting image: {e}")
        augmented_img_np = img_np

    augmented_img = Image.fromarray(augmented_img_np)
    img_byte_arr = io.BytesIO()
    augmented_img.save(img_byte_arr, format='PNG')

    if isinstance(image_data, dict):
        result = {
            'bytes': img_byte_arr.getvalue(),
            **{k: v for k, v in image_data.items() if k != 'bytes'}
        }
        if 'bbox' in image_data:
            result['bbox'] = augmented_bbox
        return result
    else:
        return img_byte_arr.getvalue()


augmented_data1 = []
for idx, row in tqdm(df.iterrows(), total=len(df), desc="First augmentation"):
    try:
        augmented_row = row.copy()
        augmented_row['image'] = augment_and_convert(row['image'], albumentations_transform1)
        augmented_data1.append(augmented_row)
    except Exception as e:
        print(f"Error processing row {idx}: {e}")
        augmented_data1.append(row)

augmented_data2 = []
for idx, row in tqdm(df.iterrows(), total=len(df), desc="Perspective augmentation"):
    try:
        augmented_row = row.copy()
        augmented_row['image'] = augment_and_convert(row['image'], albumentations_transform2)
        augmented_data2.append(augmented_row)
    except Exception as e:
        print(f"Error processing row {idx}: {e}")
        augmented_data2.append(row)

final_augmented_data = augmented_data1 + augmented_data2
augmented_df = pd.DataFrame(final_augmented_data)

augmented_df.to_parquet('datasets/dataset1_augmented_perspective.parquet', index=False)
print("\nAugmented DataFrame saved to datasets/dataset1_augmented_perspective.parquet")
print("Original DataFrame shape:", df.shape)
print("New DataFrame shape:", augmented_df.shape)