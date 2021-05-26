# ライブラリimport

import pandas as pd
import sqlite3

# 作業ディレクトリの設定
DB_DIR = 'C:/Users/es/Documents/Python Scripts/6.GraduateMission/3.sqlite3/'

# データベースから読込む
def read_db_data():

    dbname = f'{DB_DIR}kabu_inv_fin.db'
    conn = sqlite3.connect(dbname)

    df=pd.read_sql_query('select SC, 日時, 前日終値, 始値, 高値, 安値 from fundamental', conn)

    conn.close()
    
    return df
    
def deta_db_insert(df):

    dbname = f'{DB_DIR}kabu_inv_fin.db'
    
    conn = sqlite3.connect(dbname)
    
    df.to_sql('stockprice', conn, if_exists='replace')
    
    conn.close()
