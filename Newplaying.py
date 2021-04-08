import os
import ast
import json
import tweepy
from datetime import datetime
from unicodedata import east_asian_width
from matplotlib import pyplot as plt
from dotenv import load_dotenv
from PIL import Image

load_dotenv(".env")

consumer_key= os.environ.get("consumer_key")
consumer_secret=os.environ.get("consumer_secret")
access_token=os.environ.get("access_token")
access_token_secret=os.environ.get("access_token_secret")


dt = datetime.now()
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

Artist_file = "C:/Users/hayaa/iCloudDrive/iCloud~is~workflow~my~workflows/artist.txt"
title_file = "C:/Users/hayaa/iCloudDrive/iCloud~is~workflow~my~workflows/title.txt"
pic_file = "C:/Users/hayaa/iCloudDrive/iCloud~is~workflow~my~workflows/jacket.png"
db_file = "C:/Users/hayaa/Documents/A_Python/Auto_Nowplaying/archive.json"
graph_file = "graph.png"
music_db = dict()

tweet = f"#僕の聴いてる音楽\n\n{dt.month}/{dt.day}\n"

def make_image(pic_file):   #画像を持ってくる
    img = Image.open(pic_file)
    img_resize_lanczos = img.resize((img.width//2, img.height//2), Image.LANCZOS)
    img_resize_lanczos.save('C:/Users/hayaa/iCloudDrive/iCloud~is~workflow~my~workflows/jacket_resize.png')
    pic_file_resize = 'C:/Users/hayaa/iCloudDrive/iCloud~is~workflow~my~workflows/jacket_resize.png'
    return pic_file_resize

def Artist_read(Artist_file):   #アーティストのリスト
    with open(Artist_file,"r",encoding="utf-8") as f:
        Artist_list = f.read()
        Artist_list = Artist_list.split("|")

        for n,i in enumerate(Artist_list):
            if len(i) > 15:
                Artist_list[n] = i[:13] + "..."
    return Artist_list

def title_read(title_file):     #タイトルのリスト
    with open(title_file,"r",encoding="utf-8") as f:
        title_list = f.read()
        title_list = title_list.split("|")
    return title_list

def counter(tweet):     #文字のカウンター
    tweet_list = list(tweet)
    text_counter = 0
    for n in tweet_list:
        j = east_asian_width(n)
        if 'F' == j:
            text_counter += 2
        elif 'H' == j:
            text_counter += 1
        elif 'W' == j:
            text_counter += 2
        elif 'Na' == j:
            text_counter += 1
        elif 'A' == j:
            text_counter += 2
        else:
            text_counter += 1
    return text_counter

def make_tweet(Artist_list,title_list):    #ツイート文の作成
    global tweet
    for Artist,title in zip(Artist_list,title_list):
        text_counter = counter(tweet)
        if text_counter < 220:
            tweet += f"{title}/{Artist}\n"
        else:
            break

def make_graph(music_db):
    x = []
    y = []
    for i in music_db:
        x.append(i)
        y.append(music_db[i])
    plt.bar(x,y)
    plt.xticks(rotation=270)
    plt.savefig(graph_file)

def do_tweet(file,tweet):   #実際にツイートする
    try:
        api.update_with_media(filename = file, status = tweet)
    except:
        api.update_status(status = "自動ツイートが文字数制限でできなかったので\nほのけのTwitterを見ててください\nhttps://twitter.com/_kuroki_honoka?s=20")
    
def add_db(Artist_list,music_db):   #dbに追加する(ここはjson)
    for n in range(len(Artist_list)):
        if not n in music_db:
            music_db[n] = 1
        else:
            music_db[n] += 1

def open_db():  #jsonからdictにする
    with open(db_file,encoding="utf-8") as f:
        music_db = json.load(f)
    return music_db

def write_db(music_db):     #書き込む
    with open(db_file,"w",encoding="utf-8") as f:
        if dt.day != 1:
            music_json = json.dumps(music_db,ensure_ascii=False,indent=4)
            f.write(music_json)
        else:
            f.write("{}")

def count_music(music_db):    #何回聴いたか数える
    count = sum(music_db.values())
    return count

def tweet_first(music_db):    #月初めのツイート
    if dt.day == 1:
        text = f"#僕の聴いた音楽\n\n{dt.month - 1}月聞いたアーティスト\n\n"
        
        for i in music_db:
            text_counter = counter(text)
            if text_counter < 200:
                text += f"{i}/{music_db[i]}回\n"
            else:
                break
            count = count_music(music_db)
        text += f"\nその他{count}曲聞きました"
        make_graph(music_db)
        api.update_with_media(filename = graph_file, status = text)


def main():
    global tweet
    pic_file_resize =  make_image(pic_file) #画像サイズ変更
    Artist_list = Artist_read(Artist_file) #アーティストのリスト作成
    title_list = title_read(title_file) #タイトルのリスト作成
    make_tweet(Artist_list,title_list) #ツイート文作成
    do_tweet(pic_file_resize,tweet)
    music_db = open_db() #データベース開くよ
    tweet_first(music_db) #月初めのツイート
    add_db(Artist_list,music_db) #データベースに追加するよ
    write_db(music_db) #データベースに書き込むよ
    

if __name__ == "__main__":
    main()