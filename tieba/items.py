import scrapy


class PostItem(scrapy.Item):
    post_id = scrapy.Field()
    title = scrapy.Field()


class CommentItem(scrapy.Item):
    comment_id = scrapy.Field()
    post_id = scrapy.Field()
    user = scrapy.Field()
    user_nickname = scrapy.Field()
    user_id = scrapy.Field()
    portrait = scrapy.Field()
    level_name = scrapy.Field()
    cur_score = scrapy.Field()
    floor = scrapy.Field()
    publish_time = scrapy.Field()
    content = scrapy.Field()
    is_anonym = scrapy.Field()
    post_type = scrapy.Field()
    comment_num = scrapy.Field()
    is_fold = scrapy.Field()
    post_index = scrapy.Field()
    ip_address = scrapy.Field()
    is_like = scrapy.Field()


class ReplyItem(scrapy.Item):
    reply_id = scrapy.Field()
    comment_id = scrapy.Field()
    post_id = scrapy.Field()
    user = scrapy.Field()
    content = scrapy.Field()
    publish_time = scrapy.Field()
    replied_user_name = scrapy.Field()
