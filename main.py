#!usr/bin/env python
# -*- cording: utf-8 -*-

import sys
import os
import glob
import pandas as pd
from collections import Counter


def load_activity_data(base_directory):
    """
    指定したディレクトリ内の全ての first_data, second_data を読み込む
    """
    personal_activity_label_list = []

    # 各実験フォルダを検索(実験_活性度調査_* にマッチするフォルダをすべて取得)
    experiment_dirs = sorted(glob.glob(os.path.join(base_directory, "実験_活性度調査_*")))

    # print(experiment_dirs)

    # 各フォルダを順に処理
    for experiment_dir in experiment_dirs:
        # print(experiment_dir)
        sub_dirs = sorted(glob.glob(os.path.join(experiment_dir, "*")))  # 00, 01, ..., 014 のフォルダを取得
        personal_list = []
        for sub_dir in sub_dirs:
            first_data_path = os.path.join(sub_dir, f"{os.path.basename(sub_dir)}_first_data.csv")
            second_data_path = os.path.join(sub_dir, f"{os.path.basename(sub_dir)}_second_data.csv")

            if os.path.exists(first_data_path):
                df_first = pd.read_csv(first_data_path, usecols=["cid", "class"])
                # df_first.columns = ["", ""]  # 列名を空にする
                personal_list.append(df_first) #ファーストデータを追加する


            if os.path.exists(second_data_path):
                df_second = pd.read_csv(second_data_path, usecols=["cid", "class"])
                # df_second.columns = ["", ""]  # 列名を空にする
                personal_list.append(df_second) #セカンドデータを追加する

        result_df = pd.concat(personal_list,ignore_index=True)
        personal_activity_label_list.append(result_df)
    # [print(personal_activity_label) for personal_activity_label in personal_activity_label_list]
    # print(personal_activity_label_list)
    return personal_activity_label_list

def is_consecutive(keys):
    # keysが連番になっているかを確認
    return all(keys[i] + 1 == keys[i + 1] for i in range(len(keys) - 1))

def determine_activity_level(personal_activity_label_list):
    """
    多数決で活性度を決定し、決まらないものを保留リストに格納
    """
    class_counts = {}
    # cidごとにclassの出現回数をカウント
    for df in personal_activity_label_list:
        for _, row in df.iterrows():
            cid, cls = row['cid'], row['class']
            if cid not in class_counts:
                class_counts[cid] = Counter()
            class_counts[cid][cls] += 1
    
    #決まった活性度を入れるリスト
    correct_activity_label_data = []
    #保留リスト
    undecided_activity_label_list = []

    # 最頻値が一つかどうかを判定
    for cid, counter in class_counts.items():
        most_common = counter.most_common()
        max_count = most_common[0][1]
        top_classes = [cls for cls, count in most_common if count == max_count]
        if len(top_classes) == 1:
            # if len(most_common)==3:
                # sorted_data = sorted(most_common, key=lambda x: x[0])
                # # タプルの2番目の要素（key）を抽出
                # keys = [x[0] for x in sorted_data]

                # 連番かどうかを判定
                # if is_consecutive(keys):
                #     print(cid, sorted_data,"top",top_classes[0])
                # else:
                #     print(cid, sorted_data,"top",top_classes[0],"連番ではありません")
                # # print(sorted_data)
            correct_activity_label_data.append({'cid': cid, 'class': top_classes[0]})
        else:
            #保留の時のデータを確認する用
            # print(cid,most_common)


            undecided_activity_label_list.append(cid)
    # データフレームに変換
    correct_activity_label_df = pd.DataFrame(correct_activity_label_data)
    
    
    return correct_activity_label_df, undecided_activity_label_list

def calculate_reliability(personal_activity_label_list, correct_activity_label_df):
    """
    活性度採用率の一番高い人を返す
    """
    reliability_scores = []

    for idx, df in enumerate(personal_activity_label_list):
        merged = df.merge(correct_activity_label_df, on="cid", suffixes=("_eval", "_correct"))
        correct_matches = (merged["class_eval"] == merged["class_correct"]).sum()
        reliability_scores.append((idx, correct_matches / len(merged)))

    # print(reliability_scores)
    # 一番信頼性の高い評価者を返す
    best_reviewer_idx = max(reliability_scores, key=lambda x: x[1])[0]
    return best_reviewer_idx

def resolve_undecided_labels(undecided_activity_label_list, personal_activity_label_list, best_reviewer_idx, correct_activity_label_df):
    """ 保留された `cid` に対して、一番信頼性の高い評価者のデータを採用する """
    best_reviewer_df = personal_activity_label_list[best_reviewer_idx]

    for cid in undecided_activity_label_list:
        selected_class = best_reviewer_df[best_reviewer_df["cid"] == cid]["class"].values[0]
        correct_activity_label_df = pd.concat([correct_activity_label_df, pd.DataFrame({"cid": [cid], "class": [selected_class]})])

    return correct_activity_label_df

def main():
    """
    メイン
    """
    # print("directory name:",args[0])
    # print("Current working directory:", os.getcwd())
    # print("Contents of the base directory:", os.listdir("./実験_活性度調査/03実験後データ"))

    #ファイルのパス
    base_directory = "./実験_活性度調査/03実験後データ" #コードからの相対パス

    #ファイルパスの確認
    # print(base_directory)

    #ファイルからデータを読み込む
    personal_activity_label_list = load_activity_data(base_directory)

    #データの確認
    # print(personal_activity_label_list[0])
    # print(personal_activity_label_list[1])
    # print(personal_activity_label_list[2])
    # print(personal_activity_label_list[3])
    # print(personal_activity_label_list[0][0])

    #多数決で活性度を決定、決まらないものを保留リストに入れる
    correct_activity_label_df, undecided_activity_label_list = determine_activity_level(personal_activity_label_list)

    # pd.set_option('display.max_rows', None)  # すべての行を表示
    # pd.set_option('display.max_columns', None)  # すべての列を表示
    # pd.set_option('display.width', None)  # 自動で適切な横幅に調整
    
    #決定リストと保留リストの確認
    # print(correct_activity_label_df)
    # print(undecided_activity_label_list)

    #活性度採用率が一番高い人を選ぶ
    best_reviewer_idx = calculate_reliability(personal_activity_label_list,correct_activity_label_df)
    #誰の活性度が採用されるか確認
    # print(best_reviewer_idx)

    #保留リストのcidを活性度採用率が一番高い人のclassして決定リストと合成する
    correct_activity_label_df = resolve_undecided_labels(undecided_activity_label_list, personal_activity_label_list, best_reviewer_idx, correct_activity_label_df)
    # print(correct_activity_label_df)
    
    #出力
    correct_activity_label_df.to_csv("data/correct_activity_label.csv", index=False)
    print("✅ 出力完了: data/correct_activity_label.csv")
    
    

#実行
if __name__ == '__main__':
    sys.exit(main())