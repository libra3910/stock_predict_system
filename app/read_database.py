import pandas as pd
import sqlite3

# 作業ディレクトリの設定
DB_DIR = 'C:/Users/es/Documents/Python Scripts/6.GraduateMission/3.sqlite3/'

# データベースから読込む
def read_db_data_analyzer(fromdate, todate):

    dbname = f'{DB_DIR}kabu_inv_fin.db'
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    
    date = (fromdate, todate)

    data = []
    for row in cur.execute('SELECT * FROM analyze where 日時 between  ? and ?', date):
        data.append(row)

    data = pd.DataFrame(data, columns=[
                    'SC','日時','超過収益率','市場超過収益率','収益率','市場収益率','alpha','market_beta',
                    '企業規模','簿価時価比率','財務レバレッジ','E(+)/P','赤字ダミー','25日移動平均乖離率','業種','PER']
                   )

    data.set_index(
        ['SC', '日時'],
        inplace=True,
        verify_integrity=True
    )

    cur.close()
    conn.close()
    
    return data
    
def read_db_data_stockprice(fromdate, todate):

    dbname = f'{DB_DIR}kabu_inv_fin.db'
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    
    date = (fromdate, todate)

    data = []
    for row in cur.execute('SELECT SC, 日時, 前日終値, 始値, 高値, 安値 FROM stockprice where 日時 between  ? and ?', date):
        data.append(row)

    print(len(data))
    data_frame = pd.DataFrame(data, columns=['SC', '日時', '前日終値', '始値', '高値', '安値'])
    

    data_frame.set_index(
        ['SC', '日時'],
        inplace=True,
        verify_integrity=True
    )

    cur.close()
    conn.close()
    
    return data_frame
