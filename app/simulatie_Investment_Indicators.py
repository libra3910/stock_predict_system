import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('whitegrid')
plt.rcParams['font.family'] = 'Yu Mincho'

# 翌日収益率、翌日超過収益率の追加
def add_nextday_return(data_for_analysis_loaded):

    independent_variables_names = [
    'market_beta', '企業規模', '簿価時価比率', '財務レバレッジ',
    '赤字ダミー', '25日移動平均乖離率', 'PER'
    ]
    columns_to_use = [
        '業種', '翌日収益率', '翌日超過収益率', '収益率', '市場収益率'
    ] + independent_variables_names

    data_for_analysis=data_for_analysis_loaded.assign(
        # 超過収益率を1日分ずらして、翌日超過収益率を作成
        翌日超過収益率=lambda x: x['超過収益率'].groupby(level=0).shift(-1),
        # 後のシミュレーションで利用するので一緒に作成しておく
        翌日収益率=lambda x: x['収益率'].groupby(level=0).shift(-1)  
    )[columns_to_use]

    return data_for_analysis

# 終値の追加
def add_today_endprice(stockprice):

    independent_variables_names = [
    'SC', '日時', '前日終値', '始値', '高値', '安値'
    ]
    columns_to_use = ['終値'] + independent_variables_names

    data_for_stockprice=stockprice.assign(
        # 前日終値を1日分ずらして、終値を作成
        終値=lambda x: x['前日終値'].groupby(level=0).shift(-1),
    )[columns_to_use]

    return data_for_stockprice

# 選択した指標を5段階にランキングする。
def create_portfolio_by_one_variable(
    data,
    sort_by,
    q,
    labels=None,
    group_name=None
):
    group_by_date = data.groupby('日時')
    
    if isinstance(q, int) and labels is None:
        labels = range(q)

    values = []
    for date, value in group_by_date:
        if value[sort_by].isnull().all(): # 空のDataFrameは無視する
            continue
            
        value = value.assign(
            quantile=lambda x: pd.qcut(
                x[sort_by], q, labels=labels
            )
        )
        
        if group_name is not None:
            value.rename(columns={'quantile':group_name}, inplace=True)
            
        values.append(value)
    
    return pd.concat(values)



