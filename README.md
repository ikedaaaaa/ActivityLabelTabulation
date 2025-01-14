# ActivityLabelTabulation
活性度のラベルを集計するプログラム

## 1. コンテナを作成する．
``` bash
# yml,dockerfile,requirements.txtを編集した場合はbuildをする必要がある
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

# 開発中の注意点
## 新しいパッケージを入れたい場合
```bash
# コンテナ内で実行
pip install {package}

# 次にコンテナを立てるときにそのパッケージを入れることができるために実行
pip freeze > requirements.txt
```

# プログラムの仕様
## ディレクトリ構造
```
02実験後データ/
    ┝ 実験_活性度調査_01_{名前}/
    │    └ 00/
    │    │     └ 00_conv_file/
    │    │     │   └ 00_00.wav
    │    │     │   └ 00_01.wav
    │    │     │   ...
    │    │     └ 00_first_data.csv
    │    │     └ 00_second_data.csv
    │    │     └ assertive_point_00_first_data.csv
    │    │     └ assertive_point_00_second_data.csv
    │    └ 01/
    │    ...
    │    └ 014/
    │    └ 会話活性度の定義.pdf
    │    ...
    ┝ 実験_活性度調査_03_{名前}/
    ┝ 実験_活性度調査_07_{名前}/
    ┝ 実験_活性度調査_09_{名前}/
```
## したいこと
全ての区間の活性度を決定したい．

4人（今後増える可能性も見越す）の多数決で活性度を決定する．

ex)「cid」が「00_00」のものを，4人がどう答えているか．(5.0,5.0,3.0,5.0なら5.0を採用)

多数決で決定できる場合は，それがそのまま活性度となる．

多数決で決められない場合は，4人の中で，一番他の評価者と同じ評価を行うことが多かった人が選んだ活性度を採用する．（それぞれの活性度採用確率を調べ，一番高い人）

なお，[1.0,2.0,3.0,4.0,5.0] = [LL,LM,MM,MH,HH]

## プログラムの簡単な手順
### 1.データを読み込む
評価者それぞれの活性度データを読み込む(評価者それぞれの{数字}_first_data.csv,{数字}_second_data.csv)．

評価者のリスト(personal_activity_label_list)．その中身は[column=cid,class]のデータフレーム

```
ex)
personal_activity_label_list[0]
cid,class
00_00,5.0
00_01,3.0
...
14_59,5.0


personal_activity_label_list[1]
cid,class
00_00,3.0
00_01,1.0
...
14_59,3.0
```

### 2.集計する
cidごとでclassの数を数えて，最多が一つかどうかを判定する

最多が一つだった場合は，新しいデータフレーム(correct_activity_label_df(column=cid,class))に新しい行（cidと決定したclass）を追加する．

最多が複数あった場合は，一旦保留（保留リストを作ってもいい？undecided_activity_label_list）

```
ex)
correct_activity_label_df
cid,class
00_00,3.0
00_03,1.0
...
14_59,3.0

undecided_activity_label_list
[00_01,00_02,10_11,12_15,05_33]
```

### 3.活性度採用率が一番高い人を選ぶ
評価者全員の，最多が一つしかない全ての区間の採用率を調べる（各評価者のclassと決定したclassの一致率を調べるといい）

=>personal_activity_label_listそれぞれとcorrect_activity_label_dfの一致率

一番採用率が高い人を選ぶ

### 4.残りの活性度を選ぶ
一旦保留にした区間を，一番採用率が高い人が選んだ活性度にする．

そのデータをcorrect_activity_label_dfに追加する

```
ex)
correct_activity_label_df
cid,class
00_00,3.0
00_01,1.0
00_02,3.0
00_03,1.0
...
14_59,3.0
```

### 5.出力する
correct_activity_label_dfをcsvに出力する（correct_activity_label.csv）
