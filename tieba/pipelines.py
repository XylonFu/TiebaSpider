import pymysql
from scrapy.exceptions import DropItem
from scrapy.utils import spider

from tieba.items import PostItem, CommentItem, ReplyItem


class TiebaPipeline:
    def __init__(self, db_name, user, password, host):
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            db_name=crawler.settings.get('MYSQL_DB_NAME'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            host=crawler.settings.get('MYSQL_HOST')
        )

    def open_spider(self, spider):
        self.conn = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            db=self.db_name,
            charset='utf8mb4',
            autocommit=True
        )
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                post_id VARCHAR(255) PRIMARY KEY,
                title TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                comment_id VARCHAR(255) PRIMARY KEY,
                post_id VARCHAR(255),
                user VARCHAR(255),
                user_nickname VARCHAR(255),
                user_id VARCHAR(255),
                portrait TEXT,
                level_name VARCHAR(255),
                cur_score INT,
                floor VARCHAR(255),
                publish_time VARCHAR(255),
                content TEXT,
                is_anonym BOOLEAN,
                post_type VARCHAR(255),
                comment_num INT,
                is_fold BOOLEAN,
                post_index INT,
                ip_address VARCHAR(255),
                is_like BOOLEAN,
                FOREIGN KEY (post_id) REFERENCES posts(post_id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS replies (
                reply_id VARCHAR(255) PRIMARY KEY,
                comment_id VARCHAR(255),
                post_id VARCHAR(255),
                user VARCHAR(255),
                content TEXT,
                publish_time VARCHAR(255),
                replied_user_name VARCHAR(255),
                FOREIGN KEY (comment_id) REFERENCES comments(comment_id),
                FOREIGN KEY (post_id) REFERENCES posts(post_id)
            )
        """)

    def process_item(self, item, spider):
        if isinstance(item, PostItem):
            self.insert_post(item)
        elif isinstance(item, CommentItem):
            self.insert_comment(item)
        elif isinstance(item, ReplyItem):
            self.insert_reply(item)
        else:
            raise DropItem(f"Missing type in item: {item}")
        return item

    def insert_post(self, item):
        try:
            self.cursor.execute(
                "INSERT INTO posts (post_id, title) VALUES (%s, %s) ON DUPLICATE KEY UPDATE title=%s",
                (item['post_id'], item['title'], item['title'])
            )
        except pymysql.IntegrityError as e:
            spider.logger.debug(f"MySQL error: {e}")

    def insert_comment(self, item):
        try:
            self.cursor.execute("""
                INSERT INTO comments (comment_id, post_id, user, user_nickname, user_id, portrait, level_name, cur_score, floor, publish_time, content, is_anonym, post_type, comment_num, is_fold, post_index, ip_address, is_like) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (item['comment_id'],
                  item['post_id'], item['user'], item['user_nickname'], item['user_id'], item['portrait'],
                  item['level_name'], item['cur_score'], item['floor'], item['publish_time'],
                  item['content'], item['is_anonym'], item['post_type'], item['comment_num'],
                  item['is_fold'], item['post_index'], item['ip_address'], item['is_like']
                  ))
        except pymysql.IntegrityError as e:
            spider.logger.debug(f"MySQL error: {e}")

    def insert_reply(self, item):
        try:
            self.cursor.execute("""
                INSERT INTO replies (reply_id, comment_id, post_id, user, content, publish_time, replied_user_name) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                item['reply_id'], item['comment_id'], item['post_id'], item['user'],
                item['content'], item['publish_time'], item['replied_user_name']
            ))
        except pymysql.IntegrityError as e:
            spider.logger.debug(f"MySQL error: {e}")

    def close_spider(self, spider):
        self.conn.close()
