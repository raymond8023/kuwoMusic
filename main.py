# -- coding: utf-8 --**

import argparse
import os
import time

from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
import requests
import eyed3


def getAlbumInfo(driver, url):
    driver.get(url)
    album = driver.find_element(By.XPATH,'/html/body/div/div/div/div[2]/div/div[1]/div[2]/div[1]/p[1]')
    singer = driver.find_element(By.XPATH,'/html/body/div/div/div/div[2]/div/div[1]/div[2]/div[1]/p[2]/span')
    songs = driver.find_elements(By.XPATH,'//*[@class="name"]')
    songList = []
    for song in songs:
        songList.append(song.text)
    return album.text,singer.text,songList

def getMusic(album,singer,song,index,keywords):
    search_url = 'http://www.kuwo.cn/api/www/search/searchMusicBykeyWord?'
    search_data = {
        'key': keywords,
        'pn': '1',
        'rn': '512',
        'httpsStatus': '1',
        'reqId': '858597c1-b18e-11ec-83e4-9d53d2ff08ff'
    }
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept - encoding': 'gzip, deflate',
        'accept - language': 'zh - CN, zh;q = 0.9',
        'cache - control': 'no - cache',
        'Connection': 'keep-alive',
        'csrf': 'HH3GHIQ0RYM',
        'Referer': 'http://www.kuwo.cn/search/list?key=%E5%91%A8%E6%9D%B0%E4%BC%A6',
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/99.0.4844.51 Safari/537.36',
        'Cookie': '_ga=GA1.2.218753071.1648798611; _gid=GA1.2.144187149.1648798611; _gat=1; '
                  'Hm_lvt_cdb524f42f0ce19b169a8071123a4797=1648798611; '
                  'Hm_lpvt_cdb524f42f0ce19b169a8071123a4797=1648798611; kw_token=HH3GHIQ0RYM'
    }
    for j in range(10):
        print(f"{index+1} {song} 第{j+1}次尝试...")
        try:
            response = requests.get(search_url, params=search_data, headers=headers, timeout=20).json()
            resList = response['data']['list']
            for i in range(len(resList)):
                if resList[i]['album']==album and resList[i]['artist']==singer and resList[i]['name']==song:
                    songUrl = f"http://www.kuwo.cn/api/v1/www/music/playUrl?mid={resList[i]['rid']}&type=convert_url3&httpsStatus=1&reqId={response['reqId']}"
                    responseSong = requests.get(songUrl).json()
                    musicUrl = responseSong['data'].get('url')
                    return musicUrl
            for i in range(len(resList)):
                if singer in resList[i]['artist'] and resList[i]['name']==song:
                    songUrl = f"http://www.kuwo.cn/api/v1/www/music/playUrl?mid={resList[i]['rid']}&type=convert_url3&httpsStatus=1&reqId={response['reqId']}"
                    responseSong = requests.get(songUrl).json()
                    musicUrl = responseSong['data'].get('url')
                    return musicUrl
            print("没能找到这首歌曲："+song)
        except Exception as e:
            print(e)

def downloadMusic(musicUrl,index,album,singer,song):
    directory = "./" + singer + "-" + album + "/"
    if '?' in directory:
        directory = directory.replace('?','？')
    if not os.path.exists(directory):
        os.mkdir(directory)
    fileName = directory + str(index+1) + ". " + song + " - " + singer + ".mp3"
    try:
        responseMusic = requests.get(musicUrl)
        # print("requests over")
        with open(fileName, 'wb') as file:
            file.write(responseMusic.content)
            # file.close()
        print("下载成功:",index+1,song)
        # print("write over")
        fixFileInfo(fileName,album,singer,song,index+1)
    except Exception as e:
        print(e)

def fixFileInfo(fileName,album,singer,song,index):
    audiofile = eyed3.load(fileName)
    audiofile.tag.artist = singer
    audiofile.tag.album = album
    audiofile.tag.title = song
    audiofile.tag.track_num = index
    audiofile.tag.save(version=eyed3.id3.ID3_DEFAULT_VERSION, encoding='utf-8')
    # print("fix over")


if __name__ == '__main__':
    # 初始化chrome
    option = ChromeOptions()
    option.add_argument('-mute-audio')
    option.add_argument('--headless')
    option.service = Service('D:\Software\Code\python\chromedriver.exe')
    driver = webdriver.Chrome(options=option)
    # 需要提供专辑页面的网址
    parser = argparse.ArgumentParser(description='KuwoMusic')
    parser.add_argument('--url', type=str, help='url')
    args = parser.parse_args()
    url = args.url
    # url = 'http://www.kuwo.cn/album_detail/10157'
    if url==None:
        url=input("请粘贴酷我（kuwo.cn）网站中的专辑页面（形如：http://www.kuwo.cn/album_detail/xxxxxx）:")
    # 获取专辑名、歌手名、歌曲名单
    album,singer,songList=getAlbumInfo(driver,url)
    # album,singer,songList='周杰伦的床边故事','周杰伦',['不该 (with aMEI)']
    for i in range(len(songList)):
        keywords = singer + " " + songList[i]
        musicUrl = getMusic(album,singer,songList[i],i,keywords)
        # if musicUrl ==None:
        #     musicUrl = getMusic(album, singer, songList[i], i, songList[i])
        if musicUrl != None:
            downloadMusic(musicUrl,i,album,singer,songList[i])
    print("爬取完成，按任意键关闭窗口。")
    os.system("pause")
    os.system("exit")
