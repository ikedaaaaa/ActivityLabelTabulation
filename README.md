# ActivityLabelTabulation
活性度のラベルを集計するプログラム

## 1. コンテナを作成する．
``` bash
# ymlやdockerfileを編集し，buildしないとダメな場合
docker compose -f compose.yml up --build -d

# buildをしなくてもいい場合
docker compose -f compose.yml up  -d
```

## 2. コンテナ内に入る．
``` bash
docker exec -it ActivityLabelTabulation bash   
```

## 3. コンテナ内でpythonファイルを実行する
``` bash
# python main.py {集計するディレクトリ}
例：python main.py 実験後データ
```

## 4. コンテナを壊す
``` bash
docker compose -f compose.yml down  
```


# プログラムの仕様
## ディレクトリ構造
実験後データ-
          
