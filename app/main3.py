import create_stockprice

stock_data = create_stockprice.read_db_data()

print("DBデータ読込完了")

create_stockprice.deta_db_insert(stock_data)

print("DB登録完了")

print(stock_data)

