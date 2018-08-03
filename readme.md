## 2018年 人工知能 レポート課題

* collect_script
	* スクレイピング用スクリプト (main.py)
	    * Webページからテキスト抽出
	    * テキストのファイル出力


```
$ python main.py -h
usage: main.py [-h] [--proxy_host PROXY_HOST] [--proxy_port PROXY_PORT]
               [--filepath FILEPATH]

optional arguments:
  -h, --help            show this help message and exit
  --proxy_host PROXY_HOST
                        set Tor proxy host
  --proxy_port PROXY_PORT
                        set Tor proxy port
  --filepath FILEPATH   set output filepath

$ python main.py --proxy_host localhost --proxy_port 9050 --filepath ../resource/result
```

* analysis_script
	* 分析用スクリプト (main.py)
		* ファイルからSQLiteデータベースへの格納処理
		* 形態素解析
		* tf-idfによるベクトルの計算
		* k-meansによるクラスタリング
		* cosine similarityによる類似度計算

```
$ mkdir test

$ mkdir pickle

$ sqlite3 ./test/test.db
sqlite> create table link(id integer primary key,link text,body text);
sqlite> create table noun(id integer primary key,link text,body text);
sqlite> .exit

$ python main.py -h
usage: main.py [-h] [--filepath FILEPATH] [--dbpath DBPATH]
               [--picklepath PICKLEPATH]

optional arguments:
  -h, --help            show this help message and exit
  --filepath FILEPATH   set input file path
  --dbpath DBPATH       set input db path
  --picklepath PICKLEPATH
                        set output/input pickle path

$ python main.py --filepath ../resource/result --dbpath ./test/test.db --picklepath ./pickle
```



### 依存ライブラリなど

```
$ sudo apt-get install sqlite3
$ sudo apt-get install tor
$ /etc/init.d/tor start
$ sudo pip install bs4
$ sudo pip install nltk
$ sudo pip install scikit-learn
```