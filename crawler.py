import os
import textract
import pandas as pd
from zipfile import ZipFile
from rarfile import RarFile
from py7zr import SevenZipFile

from generator import gen_files


def extract_text(file_path):
    try:
        return textract.process(file_path).decode("utf-8")
    except:
        return ""

def process_archive(archive_path, extract_dir="temp"):
    # Распаковка ZIP/RAR/7Z и обработка вложенных файлов
    ...

def crawl(root_dir, output_csv="output.csv"):
    data = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith((".zip", ".rar", ".7z")):
                process_archive(file_path)
            else:
                content = extract_text(file_path)
                data.append({
                    "file_path": file_path,
                    "content": content
                })
    pd.DataFrame(data).to_csv(output_csv, index=False)

if __name__ == "__main__":
    gen_files()
    #crawl("storage")