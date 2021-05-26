# ライブラリimport

import pandas as pd
import numpy as np
from scipy import stats
from tqdm import tqdm_notebook as tqdm

from sklearn import linear_model, preprocessing
import statsmodels.api as sm

import matplotlib.pyplot as plt
import seaborn as sns
plt.rcParams['font.family'] = 'Yu Mincho'
import sqlite3

# 作業ディレクトリの設定
DB_DIR = 'C:/Users/es/Documents/Python Scripts/6.GraduateMission/3.sqlite3/'

ROLLING_WINDOW = 125  # window幅125日でrolling regressionする

# データベースから読込む
def read_db_data():

    dbname = f'{DB_DIR}kabu_inv_fin.db'
    conn = sqlite3.connect(dbname)

    df=pd.read_sql_query('SELECT * FROM fundamental', conn)

    conn.close()
    
    return df

#  対数変換で正規分布に近づける
def correct_skewness(series):
    if series.min() <= 0:
        series += series.min() + 1
    
    corrected = np.log(series)
    
    return corrected


#  標準化して変数のスケールを合わせる
def standardize_characteristics(series):
    series = series.dropna()
    standardized = stats.zscore(series)
    
    return pd.Series(standardized, index=series.index)


#  winsorizeによる外れ値の処理
def trim_outliers(series, limits=.01):
    series = series.dropna()
    trimmed = stats.mstats.winsorize(series, limits=limits)
    
    return pd.Series(trimmed, index=series.index)

# market_beta作成のため線形回帰により切片を算出する
def calculate_beta_for_one_security_and_period(
    data: pd.DataFrame,
    endog_name,
    exog_names, model
):
    data = data.reset_index()
    security_code = data['SC'].unique()[0]
    end_date = data['日時'].max()
    
    endog = data[endog_name].values
    exog = data[exog_names].values

    model.fit(X=exog, y=endog)  # 線形回帰を行う
    
    # 回帰係数を保存。coef_にベータが入っている。
    betas = np.append(model.intercept_, model.coef_)  
    
    # 求めたベータをDataFrameとして保存
    index = pd.MultiIndex.from_tuples(
        [(security_code, end_date)], names=['SC', '日時']
    )
    
    result = pd.DataFrame([betas],
                          columns=['alpha'] + list(exog_names),
                          index=index, dtype='float32')
    
    return result

# market_bet算出のためのループ処理
def run_time_series_regression_on_one_security(
    data_one_security_time_series: pd.DataFrame,
    endog_name,
    exog_names, model
):
    # endog_name + exog_namesカラムがnanであるものを削除
    data_for_estimation = data_one_security_time_series.dropna(
        subset=endog_name + exog_names
    )  
    length_data = data_for_estimation.shape[0]
    
    results = []
    # length_data < ROLLING_WINDOWならスキップされる
    for i in range(length_data - ROLLING_WINDOW):  
        data = data_for_estimation.iloc[i:ROLLING_WINDOW+i]
        results.append(
            calculate_beta_for_one_security_and_period(
                data,
                endog_name,
                exog_names,
                model
            )
        )

    # サンプルサイズがwindow幅より少ないときはNoneを返す
    if not results:  
        return None
        
    results = pd.concat(results)
    
    return results

# market_beta算出のため、特徴量をループ処理に引き渡す
def run_rolling_regression_over_all_securities(
    data_with_excess_returns,
    endog_name,
    exog_names=None
):
    # endog_name以外のカラムを抽出
    exog_names = exog_names or data_with_excess_returns.columns[
        ~data_with_excess_returns.columns.isin(endog_name)
    ] 
    
    # これをmodelとして使用する
    model = linear_model.LinearRegression() 
    
    group_by_security = data_with_excess_returns.groupby('SC')
    
    results = []
    for security, values in tqdm(group_by_security):

        result = run_time_series_regression_on_one_security(
            values,
            endog_name,
            exog_names,
            model
        )
        if result is None: 
            continue
        results.append(result)
    
    results = pd.concat(results)
    return results
    
    market_betas = run_rolling_regression_over_all_securities(
    data,
    endog_name=['超過収益率'],
    exog_names=['市場超過収益率']
    )

# DBから読込んだデータから特徴量を作成する。
def create_features_from_data(data):

    data.set_index(
        ['SC', '日時'],
        inplace=True,
        verify_integrity=True
    )

    # --- 企業規模 ---
    
    group_by_date = data.groupby('日時')

    dataset_of_firm_size = []
    for date, value in group_by_date:
        market_value_of_equity = value['時価総額（百万円）']
        market_value_of_equity = correct_skewness(
            market_value_of_equity
        )
        market_value_of_equity = standardize_characteristics(
            market_value_of_equity
        )
        market_value_of_equity = trim_outliers(
            market_value_of_equity
        )
    
        market_value_of_equity.name = '企業規模'
    
        dataset_of_firm_size.append(market_value_of_equity)

    dataset_of_firm_size = pd.concat(dataset_of_firm_size)

    # --- 時価簿価比率 ---
    
    group_by_date = data.groupby('日時')

    dataset_of_bm = []
    for date, value in group_by_date:
        book_to_market = value['自己資本（百万円）'] / value['時価総額（百万円）']
    
        # 自己資本がマイナスである銘柄を除去
        book_to_market = book_to_market[book_to_market >0]   
    
        book_to_market = correct_skewness(book_to_market)
        book_to_market = standardize_characteristics(book_to_market)
        book_to_market = trim_outliers(book_to_market)
    
        book_to_market.name = '簿価時価比率'
    
        dataset_of_bm.append(book_to_market)

    dataset_of_bm = pd.concat(dataset_of_bm)
    
    # --- 財務レバレッジ ---
    
    group_by_date = data.groupby('日時')

    dataset_of_leverage = []
    for date, value in group_by_date:
        financial_leverage = value['総資産（百万円）'] / value['時価総額（百万円）']
        financial_leverage = correct_skewness(financial_leverage)
        financial_leverage = standardize_characteristics(financial_leverage)
        financial_leverage = trim_outliers(financial_leverage)
    
        financial_leverage.name = '財務レバレッジ'
    
        dataset_of_leverage.append(financial_leverage)

    dataset_of_leverage = pd.concat(dataset_of_leverage)
    
    # --- E(+)/P ----
    
    group_by_date = data.groupby('日時')

    dataset_of_price_to_earnings = []
    for date, value in group_by_date:
        earnings_over_market_equity = value[
            '当期利益（百万円）'
        ] / value['時価総額（百万円）']
    
        # 自己資本がマイナスである銘柄を除去
        earnings_over_market_equity = earnings_over_market_equity[
            earnings_over_market_equity > 0
        ]  
    
        earnings_over_market_equity = correct_skewness(
            earnings_over_market_equity
        )
        earnings_over_market_equity = standardize_characteristics(
            earnings_over_market_equity
        )
        earnings_over_market_equity = trim_outliers(
            earnings_over_market_equity
        )
    
        earnings_over_market_equity.name = 'E(+)/P'
    
        dataset_of_price_to_earnings.append(earnings_over_market_equity)

    dataset_of_price_to_earnings = pd.concat(dataset_of_price_to_earnings)
    
    # --- 赤字ダミー ---

    deficit_dummy = data['当期利益（百万円）'].apply(
        lambda x: np.nan if np.isnan(x) else 1 if x <= 0 else 0
    )
    deficit_dummy = deficit_dummy.rename('赤字ダミー')

    # --- 日移動平均乖離率 ---

    period = 25  # 移動平均の期間を25日にする

    group_by_security = data.groupby('SC')  # 銘柄ごとに計算

    dataset_mv_returns = []
    for security, value in group_by_security:
        equity_price = value['時価総額（百万円）']
        moving_average = equity_price.rolling(period).mean()
        moving_average = np.log(equity_price) - np.log(moving_average)
        moving_average.name = f'{period}日移動平均乖離率'
        dataset_mv_returns.append(moving_average)

    dataset_mv_returns = pd.concat(dataset_mv_returns)

    del period

    #  25日移動平均乖離率の対数変換、標準化、外れ値
    group_by_date = dataset_mv_returns.groupby('日時')

    dataset_mv_returns = []
    for date, value in group_by_date:
        if value.isnull().all():
            continue
        processed_mv = standardize_characteristics(value)
        processed_mv = trim_outliers(processed_mv)
        processed_mv.name = value.name
        dataset_mv_returns.append(processed_mv)

    dataset_mv_returns = pd.concat(dataset_mv_returns)

    # --- market_beta ----
    
    market_betas = run_rolling_regression_over_all_securities(
        data,
        endog_name=['超過収益率'],
        exog_names=['市場超過収益率']
    )

    # 「市場超過収益率」に対する回帰係数 -> マーケット・ベータなので名前を変更
    market_betas.rename(
        columns={'市場超過収益率':'market_beta'},
        inplace=True
    )

    # 全特徴量をDBに登録
    industry = data['業種']

    data_for_analysis = pd.concat([
        data[['超過収益率', '市場超過収益率', '収益率', '市場収益率']],
        market_betas,
        dataset_of_firm_size,
        dataset_of_bm,
        dataset_of_leverage,
        dataset_of_price_to_earnings,
        deficit_dummy,
        dataset_mv_returns,
        industry
     ], axis=1)

    data_for_analysis = data_for_analysis.assign(
        PER=lambda x: np.where(
            data_for_analysis['赤字ダミー'] == 1,
            0,
            data_for_analysis['E(+)/P']
        )
    )

    return data_for_analysis

def deta_db_insert(data_for_analysis):

    dbname = f'{DB_DIR}kabu_inv_fin.db'
    
    conn = sqlite3.connect(dbname)
    
    data_for_analysis.to_sql('analyze', conn, if_exists='replace')
    
    conn.close()



