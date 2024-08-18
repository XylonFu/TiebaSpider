# TiebaSpider

## 项目简介

TiebaSpider 是一个基于 Scrapy 框架开发的通用爬虫，专门用于爬取百度贴吧的所有帖子详细内容。此项目具备以下特点：

- **全面爬取**：不仅可以爬取指定贴吧的所有帖子内容，还能获取每个帖子中的全部楼中楼信息（即回复）。
- **优化代理机制**：降低了请求切换代理的频率，有效减少了数据采集成本。爬取一个完整的贴吧仅需几块钱人民币的 IP 代理费用。
- **断点续爬**：实现了进程监控机制，保证爬虫中断后可以重新续爬。
- **分布式爬虫**：通过修改 `tieba/settings.py` 中的设置，可实现多台服务器上的分布式爬虫。

## 目录结构

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

## 安装与使用

### 1. 克隆项目

```bash
git clone https://github.com/XylonFu/TiebaSpider.git
cd TiebaSpider
```

### 2. 安装依赖

确保已安装 Python 3.11+ 和 pip，然后执行以下命令安装所需的 Python 包：

```bash
pip install -r requirements.txt
```

### 3. 配置 MySQL 数据库

在 `tieba/settings.py` 中配置 MySQL 数据库的相关设置：

```python
MYSQL_DB_NAME = 'tieba'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '123456'
MYSQL_HOST = 'localhost'
```

### 4. 配置代理

在 `tieba/settings.py` 中设置代理 API 的认证信息：

```python
PROXY_API_SECRET = 'your_api_secret'
PROXY_API_SIGN = 'your_api_sign'
PROXY_API_KEY = 'your_api_key'
```

### 5. 配置爬虫

在 `tieba/spiders/spider.py` 文件中配置需要爬取的贴吧名称（即 `kw` 参数）：

```python
def start_requests(self):
    base_url = 'https://tieba.baidu.com/f?kw=你的贴吧名称&ie=utf-8&pn={}'
    yield scrapy.Request(url=base_url.format(self.pn), callback=self.parse)
```

将 `你的贴吧名称` 替换为你想要爬取的贴吧名称。

### 6. 配置爬取页数

在 `run_spider.py` 中，可以通过修改 `pn` 的值来设置爬取的页数：

```python
pn = get_last_pn_from_file('links.txt', 0, 50)
```

`pn` 参数表示从第几页开始爬取，每次增加 50 表示跳转到下一页。

### 7. 运行爬虫

执行以下命令启动爬虫：

```bash
python run_spider.py
```

### 8. 监控爬虫

使用 `monitor_spider.py` 可以监控爬虫的运行状态，并在爬虫意外停止时自动重启：

```bash
python monitor_spider.py
```

## 功能说明

### 1. 爬取帖子及楼中楼信息

`spider.py` 文件定义了爬虫的逻辑。它会根据指定的贴吧关键词，逐页爬取该贴吧中的所有帖子，并获取每个帖子的详细内容，包括所有评论和楼中楼的回复信息。

### 2. 代理管理

`middlewares.py` 和 `proxies.py` 实现了代理的自动获取和切换，确保在访问过程中尽量避免被百度反爬虫机制拦截。

### 3. 数据存储

`pipelines.py` 负责将爬取到的数据存储到 MySQL 数据库中。包括帖子、评论和回复的信息。

### 4. 断点续爬

`run_spider.py` 中的 `get_last_pn_from_file` 函数会读取 `links.txt` 文件，获取上次爬取的位置，并从该位置继续爬取。

### 5. 分布式爬虫

如果需要在多台服务器上运行爬虫，可以取消 `tieba/settings.py` 中 Scrapy-Redis 相关设置的注释，从而实现分布式爬虫。

## 注意事项

- **代理配置**：目前使用的是天启HTTP代理服务，开发者可以根据需要自行更换代理服务提供商并修改 `proxies.py` 中的接口。
- **数据库配置**：确保 MySQL 数据库已正确配置并运行，否则爬虫将无法存储数据。
- **日志记录**：`monitor_spider.py` 会记录每次爬虫重启的时间，便于监控爬虫的稳定性。

## 许可证

该项目基于 MIT 许可证开源，详细信息请查看 [LICENSE](LICENSE) 文件。

## 贡献

欢迎贡献代码！如果您有任何建议或发现了任何问题，请提交 Issue 或 Pull Request。

---

如果有任何疑问或需要帮助，请联系开发者：[XylonFu@outlook.com](mailto:XylonFu@outlook.com)。