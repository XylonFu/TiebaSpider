# TiebaSpider

## Project Overview

TiebaSpider is a general-purpose crawler developed using the Scrapy framework, specifically designed to scrape detailed content from all posts on Baidu Tieba. This project offers the following features:

- **Comprehensive Scraping**: Not only can it scrape all posts from a specified Tieba, but it can also retrieve all floor-level replies (i.e., comments within comments) within each post.
- **Optimized Proxy Mechanism**: Reduces the frequency of proxy switching, effectively lowering data collection costs. Scraping an entire Tieba costs only a few RMB for IP proxy fees.
- **Resume Capability**: Implements process monitoring to ensure the crawler can resume from where it left off after an interruption.
- **Distributed Crawling**: By modifying the settings in `tieba/settings.py`, the crawler can be distributed across multiple servers.

## Directory Structure

```plaintext
TiebaSpider
│
├── tieba
│   ├── spiders
│   │   ├── __init__.py
│   │   └── spider.py
│   ├── __init__.py
│   ├── items.py
│   ├── middlewares.py
│   ├── pipelines.py
│   ├── proxies.py
│   └── settings.py
├── monitor_spider.py
├── run_spider.py
└── scrapy.cfg
```

## Installation and Usage

### 1. Clone the Repository

```bash
git clone https://github.com/XylonFu/TiebaSpider.git
cd TiebaSpider
```

### 2. Install Dependencies

Ensure that Python 3.11+ and pip are installed, then run the following command to install the required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Configure MySQL Database

In `tieba/settings.py`, configure the MySQL database settings:

```python
MYSQL_DB_NAME = 'tieba'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '123456'
MYSQL_HOST = 'localhost'
```

### 4. Configure Proxy

Set up the proxy API credentials in `tieba/settings.py`:

```python
PROXY_API_SECRET = 'your_api_secret'
PROXY_API_SIGN = 'your_api_sign'
PROXY_API_KEY = 'your_api_key'
```

### 5. Configure the Crawler

In the `tieba/spiders/spider.py` file, configure the Tieba name you want to scrape (i.e., the `kw` parameter):

```python
def start_requests(self):
    base_url = 'https://tieba.baidu.com/f?kw=YourTiebaName&ie=utf-8&pn={}'
    yield scrapy.Request(url=base_url.format(self.pn), callback=self.parse)
```

Replace `YourTiebaName` with the name of the Tieba you want to scrape.

### 6. Configure the Number of Pages to Scrape

In `run_spider.py`, you can set the number of pages to scrape by modifying the `pn` value:

```python
pn = get_last_pn_from_file('links.txt', 0, 50)
```

The `pn` parameter indicates the starting page, with each increment of 50 representing a jump to the next page.

### 7. Run the Crawler

Run the following command to start the crawler:

```bash
python run_spider.py
```

### 8. Monitor the Crawler

Use `monitor_spider.py` to monitor the crawler's operation and automatically restart it if it stops unexpectedly:

```bash
python monitor_spider.py
```

## Features

### 1. Scrape Posts and Floor-Level Replies

The `spider.py` file defines the crawler logic. It will scrape all posts in the specified Tieba, page by page, and retrieve detailed content from each post, including all comments and floor-level replies.

### 2. Proxy Management

The `middlewares.py` and `proxies.py` files implement automatic proxy acquisition and switching, ensuring that the crawler can avoid being blocked by Baidu's anti-crawling mechanisms.

### 3. Data Storage

The `pipelines.py` file handles storing the scraped data into a MySQL database, including information on posts, comments, and replies.

### 4. Resume Capability

The `get_last_pn_from_file` function in `run_spider.py` reads from the `links.txt` file to determine the last scraped position and resumes scraping from that point.

### 5. Distributed Crawling

If you need to run the crawler on multiple servers, you can uncomment the Scrapy-Redis settings in `tieba/settings.py` to enable distributed crawling.

## Notes

- **Proxy Configuration**: The project currently uses Tianqi HTTP proxy service. Developers can change the proxy service provider as needed and modify the interfaces in `proxies.py` accordingly.
- **Database Configuration**: Ensure that the MySQL database is properly configured and running; otherwise, the crawler will not be able to store data.
- **Logging**: `monitor_spider.py` logs each time the crawler is restarted, helping you monitor the crawler's stability.

## License

This project is open-sourced under the MIT License. For more details, please refer to the [LICENSE](LICENSE) file.

## Contributing

Contributions are welcome! If you have any suggestions or find any issues, please submit an Issue or Pull Request.

---

If you have any questions or need help, please contact the developer: [XylonFu@outlook.com](mailto:XylonFu@outlook.com).