import datetime
import json
import re

import scrapy

from tieba.items import PostItem, CommentItem, ReplyItem


class BaiduTiebaSpider(scrapy.Spider):
    name = 'baidu_tieba'
    allowed_domains = ['tieba.baidu.com']

    def __init__(self, pn=0, *args, **kwargs):
        super(BaiduTiebaSpider, self).__init__(*args, **kwargs)
        self.pn = int(pn)

    def start_requests(self):
        base_url = 'https://tieba.baidu.com/f?kw=弱智&ie=utf-8&pn={}'
        yield scrapy.Request(url=base_url.format(self.pn), callback=self.parse)

    def parse(self, response, **kwargs):
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('links.txt', 'a') as file:
            file.write(current_time + ' ' + response.url + '\n')

        for post in response.css('li.j_thread_list .threadlist_lz a.j_th_tit '):
            href = post.css('::attr(href)').get()
            title = post.css('::text').get()
            full_url = response.urljoin(href)
            post_id = href.split('/')[-1]

            yield scrapy.Request(full_url, self.parse_post, priority=1, meta={'post_id': post_id, 'title': title})

        self.pn += 50
        next_page_url = f'https://tieba.baidu.com/f?kw=弱智&ie=utf-8&pn={self.pn}'
        yield scrapy.Request(url=next_page_url, callback=self.parse, priority=0)

    def parse_post(self, response):
        post_id = response.meta['post_id']
        title = response.meta['title']

        post_item = PostItem(
            post_id=post_id,
            title=title,
        )
        yield post_item

        for comment in response.css('div.l_post.j_l_post.l_post_bright'):
            data_field = comment.css('::attr(data-field)').get()
            data = json.loads(data_field)

            comment_item = CommentItem(
                comment_id=data['content']['post_id'],
                post_id=response.meta['post_id'],
                user=data['author'].get('user_name', '匿名用户'),
                user_nickname=data['author'].get('user_nickname', data['author']['user_name'] if data['author'][
                    'user_name'] else '匿名用户'),
                user_id=data['author'].get('user_id', '未知'),
                portrait=f"https://tieba.baidu.com/home/main?id={data['author'].get('portrait', '')}&fr=pb&ie=utf-8",
                level_name=comment.css('.user_badge::attr(title)').get().split('，')[0] if comment.css(
                    '.user_badge::attr(title)').get() else '未知',
                cur_score=data['author'].get('cur_score', 0),
                floor=str(data['content'].get('post_no', '未知')),
                publish_time=comment.css('.post-tail-wrap .tail-info::text').re_first(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}'),
                content=comment.css('div.d_post_content.j_d_post_content::text').get(
                    default='内容被折叠或删除').strip(),
                is_anonym=data['content'].get('is_anonym', False),
                post_type=data['content'].get('type', '未知'),
                comment_num=data['content'].get('comment_num', 0),
                is_fold=data['content'].get('is_fold', False),
                post_index=data['content'].get('post_index', '未知'),
                ip_address=comment.css('.post-tail-wrap span::text').re_first(r'IP属地:(\S+)') or '未知',
                is_like=data['author'].get('is_like', False),
            )
            yield comment_item

            comment_id = data['content']['post_id']
            lzl_container_style = comment.css('.j_lzl_container.core_reply_wrapper::attr(style)').get('')
            min_height_match = re.search(r'min-height:(\d+)px', lzl_container_style)
            if min_height_match:
                min_height = int(min_height_match.group(1))
                if min_height <= 50:
                    self.logger.debug(f'Skipping lzl processing for comment_id={comment_id} due to min-height <= 50px')
                    continue

            lzl_url = f"https://tieba.baidu.com/p/comment?tid={post_id}&pid={comment_id}&pn=1"
            yield scrapy.Request(lzl_url, callback=self.parse_comment, priority=3,
                                 meta={'post_id': post_id, 'comment_id': comment_id})

        next_page_link = response.xpath('//a[contains(text(),"下一页")]/@href').get()
        if next_page_link:
            next_page_url = response.urljoin(next_page_link)
            yield scrapy.Request(next_page_url, self.parse_post, priority=2, meta={'post_id': post_id, 'title': title})
        else:
            self.logger.debug(f"到达最后一页: {post_id}")

    def parse_comment(self, response):
        post_id = response.meta['post_id']
        comment_id = response.meta['comment_id']

        for reply in response.css('li.lzl_single_post.j_lzl_s_p'):
            data_field = reply.css('::attr(data-field)').get()
            data = json.loads(data_field)

            content_full = reply.css('span.lzl_content_main').xpath('string(.)').get().strip()
            replied_user = reply.css('span.lzl_content_main a.at::text').get()

            if replied_user:
                content = content_full.replace(f"回复 {replied_user} :", "").strip()
            else:
                content = content_full

            reply_item = ReplyItem(
                reply_id=data['spid'],
                comment_id=comment_id,
                post_id=post_id,
                user=data.get('user_name', '匿名用户'),
                content=content,
                publish_time=reply.css('span.lzl_time::text').get(),
                replied_user_name=replied_user.strip() if replied_user else None
            )

            yield reply_item

        next_page_number = response.xpath('//a[contains(text(),"下一页")]/@href').re_first(r'#(\d+)')
        if next_page_number:
            next_page_url = f"https://tieba.baidu.com/p/comment?tid={post_id}&pid={comment_id}&pn={next_page_number}"
            yield scrapy.Request(next_page_url, callback=self.parse_comment, priority=4,
                                 meta={'post_id': post_id, 'comment_id': comment_id})
        else:
            self.logger.debug(f"到达最后一页: {post_id}, {comment_id}")
