# -*- coding: utf-8 -*-
# Author: adm1nSQL

import aiohttp
import asyncio
from bs4 import BeautifulSoup
import os

proxies = 'http://127.0.0.1:7890'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (HTML, like Gecko) '
                         'Chrome/108.0.0.0 Safari/537.36'}
list_urls = []
down_urls = []


async def fetch(session, url):
    try:
        async with session.get(url, proxy=proxies, headers=headers, timeout=10) as response:
            return await response.text()
    except Exception as e:
        print(f"发生异常: {e}")
        return None


async def get_page(s_page, e_page):
    tasks = []
    for i in range(s_page, e_page):
        url = 'https://mm.tvv.tw/category/xinggan/' + str(i)
        tasks.append(get_img_list(url))
    await asyncio.gather(*tasks)


async def get_img_list(url):
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            features_divs = soup.find_all('div', class_='col-md-3 col-sm-6 col-xs-6 blog-listing')

            for div in features_divs:
                img_list = div.find_all('div', class_='blog-image')
                for img in img_list:
                    a_tags = img.find_all('a')
                    for a in a_tags:
                        href = a.get('href')
                        list_urls.append(href)


async def get_img_url(session, url):
    async with session.get(url, proxy=proxies, headers=headers, timeout=10) as response:
        if response.status == 200:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            img_div = soup.find('div', class_='blog-details-text')
            img_tags = img_div.find_all('img')
            img_urls = [img.get('src') for img in img_tags]
            down_urls.extend(img_urls)


async def download_img(session, url):
    img_name = url.split('/')[-1]
    path = os.path.join('./性感美女/', str(url.split('/')[-2]))
    os.makedirs(path, exist_ok=True)
    try:
        async with session.get(url, proxy=proxies, headers=headers, timeout=10) as response:
            if response.status == 200:
                img_data = await response.read()
                with open(os.path.join(path, img_name), 'wb') as f:
                    f.write(img_data)
                    print("已保存图片:", path + '/' + img_name)
    except:
        await download_img(session, url)


async def main():
    s_page = input("请输入起始页，回车则代表从第1页开始爬取:")
    if not s_page or s_page.isspace():
        s_page = 1
    else:
        try:
            s_page = int(s_page)
        except ValueError:
            s_page = int(input("无效的输入，请输入数字作为起始页，回车则代表从第1页开始爬取:"))
    e_page = input("请输入结束页:")
    try:
        e_page = int(e_page)
    except ValueError:
        e_page = int(input("无效的输入，请输入数字作为结束页:"))
    print(f"==========起始页为{s_page}，结束页为{e_page}>>>>>>>>>>\n==========开始爬取图片列表>>>>>>>>>>")
    await get_page(s_page, e_page)
    print("*" * 33)
    print("==========开始获取下载地址>>>>>>>>>>")
    async with aiohttp.ClientSession() as session:
        tasks = [get_img_url(session, url) for url in list_urls]
        await asyncio.gather(*tasks)
    print("*" * 33)
    print("==========开始下载图片>>>>>>>>>>")
    async with aiohttp.ClientSession() as session:
        tasks = [download_img(session, url) for url in down_urls]
        await asyncio.gather(*tasks)
    print("✅爬取任务执行完毕！")


if __name__ == '__main__':
    asyncio.run(main())
