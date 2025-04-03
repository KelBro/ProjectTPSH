import os
from PIL import Image

def delete_small_images(directory, min_size=32):
    """
    Удаляет изображения размером меньше min_size x min_size пикселей
    
    :param directory: Папка с изображениями
    :param min_size: Минимальный размер (ширина и высота) в пикселях
    """
    deleted_count = 0
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        
        try:
            # Явно закрываем файл после открытия
            img = Image.open(filepath)
            width, height = img.size
            img.close()  # Важно: закрываем файл
            
            if width < min_size or height < min_size:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                    print(f"Удалено: {filename} ({width}x{height})")
                except PermissionError:
                    print(f"Не удалось удалить {filename}: файл занят другим процессом")
                    
        except (IOError, OSError) as e:
            print(f"Ошибка при обработке {filename}: {str(e)}")
        except Exception as e:
            print(f"Неизвестная ошибка с {filename}: {str(e)}")
    
    print(f"\nГотово! Удалено изображений: {deleted_count}")

# Пример использования
if __name__ == "__main__":
    folder_path = '.\FitLPh'
    delete_small_images(folder_path)