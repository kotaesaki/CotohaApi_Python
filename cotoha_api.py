# -*- coding:utf-8 -*-

import os
import urllib.request
import json
import configparser
import codecs


# COTOHA API操作用クラス
class CotohaApi:
    # 初期化
    def __init__(self, client_id, client_secret, developer_api_base_url, access_token_publish_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.developer_api_base_url = developer_api_base_url
        self.access_token_publish_url = access_token_publish_url
        self.getAccessToken()

    # アクセストークン取得
    def getAccessToken(self):
        # アクセストークン取得URL指定
        url = self.access_token_publish_url

        # ヘッダ指定
        headers={
            "Content-Type": "application/json;charset=UTF-8"
        }

        # リクエストボディ指定
        data = {
            "grantType": "client_credentials",
            "clientId": self.client_id,
            "clientSecret": self.client_secret
        }
        # リクエストボディ指定をJSONにエンコード
        data = json.dumps(data).encode()

        # リクエスト生成
        req = urllib.request.Request(url, data, headers)

        # リクエストを送信し、レスポンスを受信
        res = urllib.request.urlopen(req)

        # レスポンスボディ取得
        res_body = res.read()

        # レスポンスボディをJSONからデコード
        res_body = json.loads(res_body)

        # レスポンスボディからアクセストークンを取得
        self.access_token = res_body["access_token"]


    # 感情分析API
    def sentiment(self, sentence):
        # 感情分析API URL指定
        url = "https://api.ce-cotoha.com/api/dev/nlp/v1/sentiment"
        # ヘッダ指定
        headers={
            "Authorization": "Bearer " + self.access_token,
            "Content-Type": "application/json;charset=UTF-8",
        }
        # リクエストボディ指定
        data = {
            "sentence": sentence
        }
        # リクエストボディ指定をJSONにエンコード
        data = json.dumps(data).encode()
        # リクエスト生成
        req = urllib.request.Request(url, data, headers)
        # リクエストを送信し、レスポンスを受信
        try:
            res = urllib.request.urlopen(req)
        # リクエストでエラーが発生した場合の処理
        except urllib.request.HTTPError as e:
            # ステータスコードが401 Unauthorizedならアクセストークンを取得し直して再リクエスト
            if e.code == 401:
                print ("get access token")
                self.access_token = getAccessToken(self.client_id, self.client_secret)
                headers["Authorization"] = "Bearer " + self.access_token
                req = urllib.request.Request(url, data, headers)
                res = urllib.request.urlopen(req)
            # 401以外のエラーなら原因を表示
            else:
                print ("<Error> " + e.reason)

        # レスポンスボディ取得
        res_body = res.read()
        # レスポンスボディをJSONからデコード
        res_body = json.loads(res_body)
        # レスポンスボディから解析結果を取得
        return res_body



if __name__ == '__main__':
    # ソースファイルの場所取得
    APP_ROOT = os.path.dirname(os.path.abspath( __file__)) + "/"

    # 設定値取得
    config = configparser.ConfigParser()
    config.read(APP_ROOT + "config.ini")
    CLIENT_ID = config.get("COTOHA API", "Developer Client id")
    CLIENT_SECRET = config.get("COTOHA API", "Developer Client secret")
    DEVELOPER_API_BASE_URL = config.get("COTOHA API", "Developer API Base URL")
    ACCESS_TOKEN_PUBLISH_URL = config.get("COTOHA API", "Access Token Publish URL")

    # COTOHA APIインスタンス生成
    cotoha_api = CotohaApi(CLIENT_ID, CLIENT_SECRET, DEVELOPER_API_BASE_URL, ACCESS_TOKEN_PUBLISH_URL)

    # 解析対象文
    sentence = "好き好き好き好き好きなんです。すっキー好き好き好きなんです。"

    # 構文解析API実行
    result = cotoha_api.sentiment(sentence)

    # 出力結果を見やすく整形
    result_formated = json.dumps(result, indent=4, separators=(',', ': '))
    print (codecs.decode(result_formated, 'unicode-escape'))