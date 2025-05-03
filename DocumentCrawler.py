import textract
import logging
from tempfile import mkdtemp
import os
from zipfile import ZipFile
from rarfile import RarFile
from py7zr import SevenZipFile
import shutil
import csv

SUPPORTED_EXTENSIONS = {
    '.doc', '.docx', '.xls', '.xlsx', '.pdf',
    '.zip', '.rar', '.7z'
}

class DocumentCrawler:
    def __init__(self):
        self.processed_files = 0
        self.failed_files = 0

    def extract_text(self, file_path: str) -> str:
        # Извлечение текста из файла
        try:
            return textract.process(file_path).decode('utf-8', errors='replace')
        except Exception as e:
            logging.error(f"Ошибка чтения {file_path}: {str(e)}")
            return ""

    def process_archive(self, archive_path: str) -> list:
        # Обработка архивов с извлечением вложенных файлов
        results = []
        temp_dir = mkdtemp()

        try:
            # Распаковка архивов
            if archive_path.lower().endswith('.zip'):
                with ZipFile(archive_path) as z:
                    z.extractall(temp_dir)
            elif archive_path.lower().endswith('.rar'):
                with RarFile(archive_path) as r:
                    r.extractall(temp_dir)
            elif archive_path.lower().endswith('.7z'):
                with SevenZipFile(archive_path) as z:
                    z.extractall(temp_dir)

            # Обработка распакованных файлов
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    if self.is_supported_file(full_path):
                        results.extend(self.process_file(full_path))

        except Exception as e:
            logging.error(f"Ошибка обработки архива {archive_path}: {str(e)}")
        finally:
            shutil.rmtree(temp_dir)

        return results

    def is_supported_file(self, file_path: str) -> bool:
        # Проверка поддержки формата файла
        ext = os.path.splitext(file_path)[1].lower()
        return ext in SUPPORTED_EXTENSIONS

    def process_file(self, file_path: str) -> list:
        # Обработка одного файла
        result = []
        try:
            if file_path.lower().endswith(('.zip', '.rar', '.7z')):
                result = self.process_archive(file_path)
            else:
                content = self.extract_text(file_path)
                result.append({
                    'path': file_path,
                    'filename': os.path.basename(file_path),
                    'filetype': os.path.splitext(file_path)[1][1:].upper(),
                    'content': content[:5000] + '...' if len(content) > 5000 else content
                })
                self.processed_files += 1
        except Exception as e:
            self.failed_files += 1
            logging.error(f"Ошибка обработки {file_path}: {str(e)}")

        return result

    def crawl(self, root_dir: str, output_file: str) -> None:
        # Основная функция сканирования
        results = []

        logging.info(f"Начало сканирования директории: {root_dir}")

        for root, _, files in os.walk(root_dir):
            for file in files:
                full_path = os.path.join(root, file)
                if self.is_supported_file(full_path):
                    results.extend(self.process_file(full_path))

        # Сохранение результатов в CSV
        if results:
            keys = results[0].keys()
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(results)

        logging.info(
            f"Сканирование завершено. Успешно: {self.processed_files}, "
            f"Ошибок: {self.failed_files}, Результаты сохранены в: {output_file}"
        )