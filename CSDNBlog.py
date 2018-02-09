# -*- coding: utf-8 -*-
import os
import re
import sys
import json
import requests
import datetime
from tomd import Tomd
from bs4 import BeautifulSoup

class CSDNBlog:

    def __init__(self,uid):
        self.uid = uid

    # 生成目录
    def generateTOC(self,fileName): 
        with open(fileName,'wt',encoding='utf-8') as f:
            itemTpl = '* {0} - [{1}]({2})\n'
            for item in self.getPosts():
                f.write(itemTpl.format(
                    datetime.datetime.strftime(item['date'],'%Y-%m-%d'),
                    item['title'],
                    'http://blog.csdn.net/{0}'.format(item['link'])
                ))

    # 导出Markdown文件
    def generateMarkdown(self):
        basePath = sys.path[0]
        if(os.path.isfile(basePath)):
            basePath = os.ptah.dirname(basePath)
        basePath = basePath + '\\blogs\\'
        if(os.path.exists(basePath) == False):
            os.makedirs(basePath)
        for item in self.getPosts():
            fileName = u'{0}\\{1}.md'.format(basePath,item['title'])
            print('Generate file:{0}'.format(fileName))
            with open(fileName,'wt',encoding='utf-8') as f:
                f.write('title: {0}\n'.format(item['title']))
                f.write('date: {0}\n'.format(
                    datetime.datetime.strftime(item['date'],'%Y-%m-%d %H:%M:%S')
                ))
                f.write('categories: {0}\n'.format(
                   '[' + ','.join(item['categories']) + ']'
                ))
                f.write('tags: {0}\n'.format(
                   '[' + ','.join(item['tags']) + ']'
                ))
                f.write('\n---')
                f.write(item['content'])

    # 返回文章信息
    def getPost(self,soup):
        post = {}

        #title/link of post
        span_title = soup.find_all('span',class_='link_title')[0]
        post['title'] = span_title.a.text.strip()
        post['link'] = span_title.a['href']

        #date of post
        span_date = soup.find_all('span',class_='link_postdate')[0]
        post['date'] = datetime.datetime.strptime(span_date.text,'%Y-%m-%d %H:%M')

        #view of post
        span_view = soup.find_all('span',class_='link_view')[0]
        pattern = re.compile('(\d+)')
        post['view'] = pattern.search(span_view.text).groups()[0]

        #comments of post
        span_comments = soup.find_all('span',class_='link_comments')[0]
        post['comments'] = pattern.search(span_comments.text).groups()[0]
        
        return post
    
    # 返回全部文章信息
    def getPosts(self):
        posts = []
        headers = {
            'Host': 'blog.csdn.net',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'
        }
        
        page = 1
        pages = page + 1
        while(page<pages):
            reqURL = 'http://blog.csdn.net/{0}/article/list/{1}'.format(self.uid,page)
            resp = requests.get(reqURL,headers=headers)
            soup = BeautifulSoup(resp.text,'html.parser')
            pages = self.getPages(soup)
            items = soup.find_all('div',class_='list_item article_item')
            for item in items:
                post = self.getPost(item)
                details = self.getPostDetails('http://blog.csdn.net/{0}'.format(post['link']))
                post['tags'] = details['tags']
                post['categories'] = details['categories']
                post['content'] = details['content']
                posts.append(post)
            page = page + 1
        return posts
    
    # 返回分页总页数
    def getPages(self,soup):
        pageList = soup.find_all('div',class_='pagelist')[0]
        span = pageList.span.text
        pattern = re.compile('共(\d+)页')
        pages = pattern.search(span).groups()[0]
        return int(pages)

    # 返回文章正文内容
    def getPostDetails(self,URL):
        details = {}
        headers = {
            'Host': 'blog.csdn.net',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'
        }
        
        resp = requests.get(URL,headers=headers)
        soup = BeautifulSoup(resp.text,'html.parser')
        
        # tags of post
        tags = []
        span_tags = soup.find_all('span',class_='link_categories')
        if(len(span_tags)>0):
            for tag in span_tags[0].find_all('a'):
                tags.append(tag.text)
        
        # categories of post
        categories = []
        div_labels = soup.find_all('div',class_='category_r')
        if(len(div_labels)>0):
            dev_labels =div_labels[0].find_all('label')
        pattern = re.compile('(.*)\s+\d+')
        for label in div_labels:
            categories.append(label.span.contents[0].string.replace('[','').replace(']',''))
        
        # contents of post
        html_content = soup.find_all(id = 'article_content')[0].prettify()
        
        details['tags'] = tags
        details['categories'] = categories
        details['content'] = html_content

        return details

blog = CSDNBlog('qinyuanpei')
#blog.generateTOC('CSDNTOC.md')
blog.generateMarkdown()

