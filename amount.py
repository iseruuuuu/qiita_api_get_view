import time
from datetime import datetime
import requests
import json
from tabulate import tabulate
from tqdm import tqdm
import argparse
from dateutil import parser as dt_parser

# メンバー全員の投稿アカウント毎の個人トークンの定義
tokens = {
    "iseki": "",
}

# HTTPS のパラメータ情報
params = {
    "page": "1",
    "per_page": "100",
}

# アカウント毎に投稿した記事のListを取得
def GetPostList():
    current_year = datetime.now().year
    last_year = current_year - 1

    current_year_count = 0
    last_year_count = 0
    cnt = 0

    # 投稿アカウントでの取得
    for key, token in tokens.items():
        # HTTPS のヘッダー情報 with 個人トークン
        print("\n ■---■---■ 投稿者：{}".format(key))
        headers = {
            "Authorization": "Bearer " + token
        }

        # 個人トークンを利用してのその個人の投稿記事情報の取得
        res1 = requests.get('https://qiita.com/api/v2/authenticated_user/items', params=params, headers=headers)
        jsonlist = json.loads(res1.text)

        # 投稿記事毎View数の取得
        post_count, this_year, last_year = GetView(jsonlist, headers, current_year, last_year)
        cnt += post_count
        current_year_count += this_year
        last_year_count += last_year

    return cnt, current_year_count, last_year_count

# 投稿した記事のView数の取得
def GetView(jsonlist, headers, current_year, last_year):
    item_key = ['User', 'url', 'page_views_count', 'likes_count', 'created_at', 'updated_at', 'Title']
    item_value = []
    current_year_posts = 0
    last_year_posts = 0

    # 投稿記事毎の情報の取得
    # プログレスバーで進捗状況を表示
    for item in tqdm(jsonlist):
        # その記事情報の取得
        res2 = requests.get('https://qiita.com/api/v2/items/' + item['id'], headers=headers)
        rec = json.loads(res2.text)

        # アカウント名、記事URL、View数、いいね数、作成日、更新日、記事タイトル 情報の取得
        created_at = dt_parser.isoparse(rec['created_at'])
        if created_at.year == current_year:
            current_year_posts += 1
        elif created_at.year == last_year:
            last_year_posts += 1

        item_value.append([rec['user']['id'], rec['url'], rec['page_views_count'], rec['likes_count'], rec['created_at'], rec['updated_at'], rec['title']])

    # json形式への変換
    rows = [dict(zip(item_key, item)) for item in item_value]

    # 取得情報の表示
    print(tabulate(rows, headers='keys'))
    print("\n   ---> 投稿数：{}\n".format(len(rows)))

    return len(rows), current_year_posts, last_year_posts

if __name__ == '__main__':    
    parser = argparse.ArgumentParser(description='Qiitaの投稿記事に対するView数を取得する')
    args = parser.parse_args()

    start = time.time()
    cnt, current_year_count, last_year_count = GetPostList()
    generate_time = time.time() - start

    print("")
    print("　Qiita Post 総数 : " + str(cnt))
    print("  今年の投稿数 : " + str(current_year_count))
    print("  昨年の投稿数 : " + str(last_year_count))
    print("  取得時間:{0}".format(generate_time) + " [sec] \n")
