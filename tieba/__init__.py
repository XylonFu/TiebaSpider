import warnings

from scrapy.exceptions import ScrapyDeprecationWarning

warnings.filterwarnings("ignore", category=ScrapyDeprecationWarning)
