# ライブラリimport
import re
import pandas as pd
from tqdm import tqdm_notebook as tqdm
from os import path
from pathlib import Path
import numpy as np
from tqdm import tqdm_notebook as tqdm
import sqlite3

# 作業ディレクトリの設定
    
DATA_DIR = 'X:/kabu.plus/csv/'  # データをダウンロードしたフォルダ
PRICE_DIR = path.join(DATA_DIR, 'japan-all-stock-prices/daily/')  # 株価一覧表
STOCK_DATA_DIR = path.join(DATA_DIR, 'japan-all-stock-data/daily/')  # 投資指標データ
FIN_RESULTS_DIR = path.join(DATA_DIR, 'japan-all-stock-financial-results/monthly/')  # 決算・財務・業績データ
OUT_DIR = 'C:/Users/es/Documents/Python Scripts/6.GraduateMission/1.product/0.data/'  # 結合したデータを保存するフォルダ
DB_DIR = 'C:/Users/es/Documents/Python Scripts/6.GraduateMission/3.sqlite3/'
    

def wareki2datetime(wareki: str, separator:str = '.'): # 和暦を西暦に変換する。
    year, month, day = wareki.split('.')
    if year.startswith('S'):
        year = 1925 + int(year[1:])
    elif year.startswith('H'):
        year = 1988 + int(year[1:])
    elif year.startswith('R'):
        year = 2018 + int(year[1:])
    else:
        NotImplementedError('S, H, R以外には使えません。')
    return pd.datetime(year, int(month), int(day))

def price_and_stock_merge():
    
    # 株価一覧表と投資指標データの結合
    
    # 株価一覧表
    
    price_data = []
    file_list = list(Path(PRICE_DIR).glob('japan-all-stock-prices_*.csv'))  # PRICE_DIR以下にあるcsvファイルのパスをすべて取得する

    for file in tqdm(file_list):
        data_ = pd.read_csv(f'file:{file}', encoding='sjis', na_values='-')
        data_.columns = [column.strip() for column in data_.columns]  # カラム名にスペースが混じることがあるので削除
        timestamp = pd.Timestamp(re.findall(r'\d{8}', file.stem)[0])  # 日時はファイル名から取得
        price_data.append(data_.assign(日時=timestamp))

    price_data = pd.concat(price_data).assign(
        日時=lambda x: x['日時'].map(
            lambda elm: pd.Timestamp(pd.to_datetime(elm).date())  # 時刻をすべて00:00:00に合わせる
        )
    )
    
    # 投資指標データ
    
    stock_data = []
    file_list = list(Path(STOCK_DATA_DIR).glob('japan-all-stock-data_*.csv'))  # STOCK_DATA_DIR以下にあるcsvファイルのパスをすべて取得する

    for file in tqdm(file_list):
        data_ = pd.read_csv(f'file:{file}', encoding='sjis', na_values='-')
        data_.columns = [column.strip() for column in data_.columns]  # カラム名にスペースが混じることがあるので削除
        timestamp = pd.Timestamp(re.findall(r'\d{8}', file.stem)[0])  # 日時はファイル名から取得
        stock_data.append(data_.assign(日時=timestamp))
        
    stock_data = pd.concat(stock_data).assign(
        日時=lambda x: x['日時'].map(
            lambda elm: pd.Timestamp(pd.to_datetime(elm).date())  # 時刻をすべて00:00:00に合わせる
        ),
        安値日付=lambda x: x['安値日付'].map(
            lambda elm: pd.Timestamp(pd.to_datetime(str(elm)[0:8]).date())  # 時刻をすべて00:00:00に合わせる
        ),
        高値日付=lambda x: x['高値日付'].map(
            lambda elm: pd.Timestamp(pd.to_datetime(str(elm)[0:8]).date())  # 時刻をすべて00:00:00に合わせる
        )
    )
    
    # 株価データ、投資指標データのマージ
    
    daily_data = pd.merge(price_data, stock_data, on=['SC', '時価総額（百万円）', '名称', '市場', '業種', '日時'], how='left')
    
    return daily_data
    

def daily_data_and_free_rate_merge(daily_data):
    
    # daily_dataと国債金利情報を結合する。
    
    
    # daily_data 銘柄ごとに計算するため、証券コード(SC)で集計する

    groups= daily_data.groupby('SC')

    data_set =[]
    for security, values in tqdm(groups):
    
        # 全体の10%以上の取引日で取引のない銘柄は無視する
        if values['株価'].isnull().sum() > values.shape[0]*0.1:  
            continue
    
        # 一時的にmarket_value列を作って計算する
        #  証券コード(SC)1、2は株価指数を表しているので、単純に指数値を入れる。
        if security in {1, 2}: 
            values = values.assign(market_value=lambda x: x['株価'])
        else:
            values = values.assign(market_value=lambda x: x['時価総額（百万円）'])
    
        # calculate return
        values = values.sort_values('日時')  # 時系列順でソート
        values['収益率'] = values['market_value'].pct_change()  # 変化率の計算
        values.drop(columns=['market_value'])  # 一時的な列を削除
        data_set.append(values)

    daily_data_adj = pd.concat(data_set)  # 銘柄ごとに計算したものを結合

    #  極端な値を外れ値として削除。ここでは上下0.1%を外れ値とする。
    threshold = .001

    lower = daily_data_adj['収益率'].quantile(threshold)
    upper = daily_data_adj['収益率'].quantile(1-threshold)

    daily_data_adj = daily_data_adj[(lower < daily_data_adj['収益率']) & (daily_data_adj['収益率'] < upper)].copy()
    
    # 国際金利情報の計算
    
    jgb_path = f'{OUT_DIR}risk_free_rate/jgbcm_all.csv'
    risk_free_rate = pd.read_csv(
        jgb_path,
        skiprows=1,
        usecols=['基準日', '10年'],
        parse_dates=['基準日'],
        date_parser=wareki2datetime,
        encoding='sjis',
        index_col=['基準日'],
        na_values='-'
    )

    risk_free_rate = risk_free_rate['10年'].apply(
    # 半年複利(%表記)を日次対数収益率に変換
        lambda x: np.log(1 + .01 * .5 * x) / 125 
    ).apply(
        # 単利へ変換
            lambda x: np.exp(x) -1 
    )
    risk_free_rate.rename('安全資産利子率', inplace=True)
    risk_free_rate.index.rename('日時', inplace=True)

    risk_free_rate = pd.DataFrame(risk_free_rate)
    
    stock_return_and_risk_free_return = pd.merge(
        daily_data_adj[daily_data_adj['SC']>2],  # 指数を除く
        risk_free_rate, on='日時'
    )  

    # SCと日時をindexにする
    stock_return_and_risk_free_return.set_index(
        ['SC', '日時'],
        verify_integrity=True, 
        inplace=True
    )
    
    # 日時で集計
    group_by_date = stock_return_and_risk_free_return.groupby('日時')  

    data_with_market_returns = []
    for date, values in tqdm(group_by_date):
        sum_of_market_capital = values['時価総額（百万円）'].sum()
        values = values.assign(
            # returnが全てnullならnullにする
            市場収益率=lambda x: (
                x['収益率'] * (x['時価総額（百万円）'] / sum_of_market_capital)
            ).sum(
                min_count=1
            )
        )
        data_with_market_returns.append(values)

    data_with_market_returns = pd.concat(data_with_market_returns)
    
    data_with_excess_returns = data_with_market_returns.assign(
        超過収益率=lambda x: x['収益率'] - x['安全資産利子率'],
        市場超過収益率=lambda x: x['市場収益率'] - x['安全資産利子率']
    )
    
    # 扱いやすくするためにindexを通常の列に戻す
    temporary_data_excess_returns = data_with_excess_returns.reset_index()  
    
    return temporary_data_excess_returns

def daily_data_and_financial_data_merge(temporary_data_excess_returns):
    
    # 財務データ
    
    financial_data = []
    file_list = list(Path(FIN_RESULTS_DIR).glob('japan-all-stock-financial-results_*.csv'))
    for file in tqdm(file_list):
        data_ = pd.read_csv(f'file:{file}', encoding='sjis', na_values='-')
        data_.columns = [column.strip() for column in data_.columns]
        timestamp = pd.Timestamp(re.findall(r'\d{8}', file.stem)[0])
        financial_data.append(data_.assign(日時=timestamp))

    financial_data = pd.concat(financial_data)
    financial_data = financial_data.assign(
        日時=lambda x: x['日時'].map(
            lambda elm: pd.Timestamp(pd.to_datetime(elm).date())
        ),
        kessan_tmp=lambda x: x['決算発表日（本決算）'].map(
            lambda elm: pd.Timestamp(pd.to_datetime(str(elm)[0:8]).date())  # 全角()が扱えないので一時カラムで対処
        )
    ).drop(columns='決算発表日（本決算）').rename(columns={'kessan_tmp': '決算発表日（本決算）'})[financial_data.columns]  # 列の順番を元に戻す

    # read financial data
    # financial_data = pd.read_pickle(f'{DATA_CHAPTER1}financial_data_all.pickle')

    # 利用しない列を削除
    financial_data.drop(
        columns=['発行済株式数', '日時'],
        inplace=True
    )  

    # 決算発表当日の株価データとマージできるように、株価データに決算発表日を張る
    group_by_security = temporary_data_excess_returns.groupby('SC')

    temporary_list = []
    for security, values in tqdm(group_by_security):
        # 財務データから決算発表日を取得 
        # 例: array(
        #         ['2016-05-11T00:00:00.000000000',
        #          '2017-05-11T00:00:00.000000000'],
        #         dtype='datetime64[ns]'
        #     )
        announcement_dates = financial_data[
            '決算発表日（本決算）'
        ][
            financial_data.SC == security
        ].dropna().unique() 
        # 古い順にソートしてnp.arrayに戻す
        announcement_dates = pd.Series(announcement_dates).sort_values().values
    
        # 収益率データの「日時」が含まれる決算期を意味するカテゴリカル変数を作る。
        # 例: 「日時」が2016-05-11より前 → 欠損値、 
        #     「日時」が2016-05-11～2017-05-10 → 2016-05-11、など
        aligned = values.assign(
            announcement_date=lambda x: pd.cut(
                x['日時'],
                (
                    list(announcement_dates)
                ) + [np.datetime64(values['日時'].max() + pd.offsets.Day())],
                labels=announcement_dates,
                right=False
            ).astype(
                np.datetime64
            )
        )
        temporary_list.append(aligned)

    temporary_data_excess_returns = pd.concat(temporary_list)
    temporary_data_excess_returns.rename(
        columns={'announcement_date':'決算発表日（日時）'},
        inplace=True
    )
    del temporary_list

    # 財務データを決算発表日について一意にする
    financial_data = financial_data.groupby(
        ['SC', '決算発表日（本決算）']
    ).first().reset_index()

    excess_returns_with_financial_data = pd.merge(
        temporary_data_excess_returns,
        financial_data,
        left_on=['SC','名称', '決算発表日（日時）'],
        right_on=['SC','名称', '決算発表日（本決算）'],
        how='left'
    )
    #excess_returns_with_financial_data.set_index(
    #    ['SC', '日時'],
    #    inplace=True,
    #    verify_integrity=True
    #)

    del temporary_data_excess_returns
    
    return excess_returns_with_financial_data
    
def deta_db_insert(excess_returns_with_financial_data):

    dbname = f'{DB_DIR}kabu_inv_fin.db'
    
    conn = sqlite3.connect(dbname)
    
    excess_returns_with_financial_data.to_sql('fundamental', conn, if_exists='replace')
    
    conn.close()

