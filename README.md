# C94-python-youtubeAPI
コミックマーケット94で「職場でNavelチョコ食べたい」にて頒布した「声に寄り添う技術の作法」に収録されている「PythonでYoutubeDataAPI使ってみた」用に作成したコードです。

YouTube Data API v3 (https://developers.google.com/youtube/v3/) を使用し、指定された再生リスト内の動画の再生回数と再生時間の一覧を作成します。

# 導入方法
## Python Version
依存先のパッケージ (https://github.com/google/google-api-python-client) に準じます。
>2018/8/18時点  
Python 2.7, 3.4, 3.5, and 3.6 are fully supported and tested. This library may work on later versions of 3, but we do not currently run tests against those versions.

## 依存パッケージのインストール
```
$ pip install --upgrade google-api-python-client
$ pip install --upgrade oauth2client
```

## YoutubeDataAPIを使用することのできるキーの設定
1.  https://cloud.google.com/console にアクセスしYouTube Data API v3用のAPIキーを作成してください。詳しくは以下のページの「作業を始める前に」を参考にしてください。
 https://developers.google.com/youtube/v3/getting-started

 2. getPlayListData.pyの15行目の`{DEVELOPER_KEY}`を作成したAPIキーで置き換えてください。  
 例：APIキーがexample_keyだった場合
 ```python
 DEVELOPER_KEY = "example_key"
 ```

# 使用方法
 getPlayListData.pyを実行してください。  
 デフォルトでは「はんなりバリカタ！」の再生リスト情報を取得し、結果を
  result.csv として出力します。  
 任意の再生リストを指定したい場合、`--id`オプションに再生リストのIDを指定して実行するか、getPlayListData.pyの144行目のdefaultのIDを書き換えてから実行してください。  
 再生リストIDは再生ページのURLから取得できます。listパラメータの部分です。  
 例：「【VRアイドル】えのぐチャンネル」内の「生放送」再生リスト
   (https://www.youtube.com/watch?v=iOilJtjKK0w&list=PLVgMytg4cke2P_XCjvw6Y_Z3KMq5ukzvT) 

 ```
 python getPlayListData.py --id PLVgMytg4cke2P_XCjvw6Y_Z3KMq5ukzvT
 ```


