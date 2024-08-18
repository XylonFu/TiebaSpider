from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from tieba.spiders.spider import BaiduTiebaSpider


def get_last_pn_from_file(file_path, default_pn=0, increment=50):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            if lines:
                last_line = lines[-1].strip()
                last_pn = int(last_line.split("pn=")[-1])
                return last_pn + increment
    except Exception as e:
        print(f"Error reading file: {e}")
    return default_pn


if __name__ == "__main__":
    pn = get_last_pn_from_file('links.txt', 0, 50)

    process = CrawlerProcess(get_project_settings())
    process.crawl(BaiduTiebaSpider, pn=str(pn))
    process.start()
