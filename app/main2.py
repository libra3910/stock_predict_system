import create_features

group_by_date = create_features.read_db_data()

print("DBデータ読込完了")

data_for_analysis = create_features.create_features_from_data(group_by_date)

print("特徴量作成完了")

create_features.deta_db_insert(data_for_analysis)

print("DB登録完了")

print(data_for_analysis)

