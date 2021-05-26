import create_data

daily_data = create_data.price_and_stock_merge()

print("株価一覧表と投資指標データのマージ完了")

temporary_data_excess_returns = create_data.daily_data_and_free_rate_merge(daily_data)

print("日次データと国際金融情報のマージ完了")

excess_returns_with_financial_data = create_data.daily_data_and_financial_data_merge(temporary_data_excess_returns)

print("日次データと財務データのマージ完了")

create_data.deta_db_insert(excess_returns_with_financial_data)

print("DB登録完了")

print(excess_returns_with_financial_data.columns)
