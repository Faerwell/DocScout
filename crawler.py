import logging
import argparse

from DocumentCrawler import DocumentCrawler
from generator import gen_files

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)




if __name__ == "__main__":
    # Генерация файлов и архива
    gen_files()

    parser = argparse.ArgumentParser(
        description='Crawler для сканирования документов и архивов'
    )
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Путь к сканируемой директории'
    )
    parser.add_argument(
        '-o', '--output',
        default='output.csv',
        help='Путь к выходному CSV-файлу'
    )

    args = parser.parse_args()
    crawler = DocumentCrawler()
    crawler.crawl(args.input, args.output)


