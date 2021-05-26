import PySimpleGUI as sg
import numpy as np
import openpyxl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
sns.set_style('whitegrid')
plt.rcParams['font.family'] = 'Yu Mincho'
import get_stockinfo
import read_database
import simulatie_Investment_Indicators

# グラフの描画
def draw_plot_L1(target_indicate, to_plot):
    fig, ax = plt.subplots(figsize=(12, 5))

    ax.set_xlabel('日時')  # x軸ラベル
    ax.set_ylabel('累積リターン')  # y軸ラベル
    title = target_indicate + "の高低と超過収益率"
    ax.set_title(title) # グラフタイトル

    ax.grid()            # 罫線
    #ax.set_xlim([-10, 10]) # x方向の描画範囲を指定
    #ax.set_ylim([0, 1])    # y方向の描画範囲を指定

    c1,c2,c3,c4 = "blue","green","red","black"      # 各プロットの色
    l1,l2,l3,l4 = "乖離率 低","乖離率 高","単純平均リターン","翌日収益率"   # 各ラベル

    y1 = to_plot['乖離率 低']
    y2 = to_plot['乖離率 高']
    y3 = to_plot['単純平均リターン']
    y4 = to_plot['翌日収益率']

    ax.plot(y1, color=c1, label=l1)
    ax.plot(y2, color=c2, label=l2)
    ax.plot(y3, color=c3, label=l3)
    ax.plot(y4, color=c4, label=l4)

    ax.legend(loc=0)    # 凡例
    fig.tight_layout()  # レイアウトの設定
    
    fig.show()

LABEL_1 = '１．株価・投資指標・財務データ取込    '
LABEL_2 = '２．株価・投資指標・財務データ読込    '
LABEL_3 = '　　日付：FROM～TO '
LABEL_5 = '３．銘柄情報表示　銘柄コード          '
LABEL_6 = '４．投資指標シミュレーション          '
LABEL_7 = '５．　株価　シミュレーション          '

LABEL_INPUT = 'データ取込'
LABEL_READ = 'データ取得'
LABEL_SC = '銘柄コード'
LABEL_DSP1 = '表示'
LABEL_DSP2 = '表示'
LABEL_DSP3 = '表示'
LABEL_EXL1 = 'EXCEL'
LABEL_EXL2 = 'EXCEL'
LABEL_STUDY = '学習'
LABEL_EXIT = '終了'

# PyS impleGUIのCanvasオブジェクト

itm = ['収益率','超過収益率','企業規模','簿価時価比率','財務レバレッジ','株価収益率','25日移動平均乖離率','マーケットベータ']

layout = [
    [sg.Text(LABEL_1, size=(35,1)),
                      sg.Button(LABEL_INPUT, key='bti')],
    [sg.Text(LABEL_2, size=(35,1))],
    [sg.Text(LABEL_3, size=(35,1)),
                      sg.InputText(key='FROMYYMMDD', size=(8,1), enable_events=False),
                      sg.Text('～'),
                      sg.InputText(key='TOYYMMDD', size=(8,1), enable_events=False),
                      sg.Button(LABEL_READ, key='btr')],
    [sg.Text(LABEL_5, size=(35,1)),
                      sg.InputText(key='SC', size=(4,1), enable_events=False),
                      sg.Button(LABEL_DSP1, key='btd1')],
    [sg.Text(LABEL_6, size=(35,1)),
                      sg.Listbox(itm, size=(18,3), key='-LIST-'),
                      sg.Button(LABEL_DSP2, key='btd2'),
                      sg.Button(LABEL_EXL1, key='bte1')],
    [sg.Text(LABEL_7, size=(35,1)),
                      #sg.Button(LABEL_STUDY),
                      sg.Button(LABEL_DSP3, key='btd3'),
                      sg.Button(LABEL_EXL2, key='bte2')],
    [sg.Button(LABEL_EXIT, key='btext')],
    [sg.Text(size=(70,1), text_color='#ff0000', border_width=1, key='TA1')],
    [sg.Text(size=(35,1), text_color='#ffff00', border_width=1, key='DS0')],
    [sg.Text(size=(35,1), text_color='#ffff00', border_width=1, key='DS1'),sg.Text(size=(35,1), text_color='#ffff00', border_width=1, key='DSB')],
    [sg.Text(size=(35,1), text_color='#ffff00', border_width=1, key='DS2'),sg.Text(size=(35,1), text_color='#ffff00', border_width=1, key='DS8')],
    [sg.Text(size=(35,1), text_color='#ffff00', border_width=1, key='DS3'),sg.Text(size=(35,1), text_color='#ffff00', border_width=1, key='DS9')],
    [sg.Text(size=(35,1), text_color='#ffff00', border_width=1, key='DS4'),sg.Text(size=(35,1), text_color='#ffff00', border_width=1, key='DS10')],
    [sg.Text(size=(35,1), text_color='#ffff00', border_width=1, key='DS5'),sg.Text(size=(35,1), text_color='#ffff00', border_width=1, key='DS11')],
    [sg.Text(size=(35,1), text_color='#ffff00', border_width=1, key='DS6'),sg.Text(size=(35,1), text_color='#ffff00', border_width=1, key='DS12')],
    [sg.Text(size=(35,1), text_color='#ffff00', border_width=1, key='DS7'),sg.Text(size=(35,1), text_color='#ffff00', border_width=1, key='DS13')]
]

window = sg.Window('株価予測システム', layout)
#outputCombo = window['OUTPUT']

while True:
    event, values = window.read() #イベントの読み取り
    
    if event == 'btext':
        break
        

    if event == 'bti':
        s1 = sg.PopupYesNo('取込を実行してよろしいですか？',title='確認します',
            text_color='#ff0',background_color='#777',button_color=('#f00','#ccc'))
        if s1 == 'Yes': 
            txtdat = 'aaa'
            window['TA1']. Update( txtdat )
            

    if event == 'btr':
        s2 = sg.PopupYesNo('読込を実行してよろしいですか？',title='確認します',
            text_color='#ff0',background_color='#777',button_color=('#f00','#ccc'))
        if s2 == 'Yes': 
            # 日付の取得
            fromdate = values['FROMYYMMDD']
            fromdate = fromdate[0:4]+'-'+fromdate[4:6]+'-'+fromdate[6:8]+' 00:00:00'
            todate = values['TOYYMMDD']
            todate = todate[0:4]+'-'+todate[4:6]+'-'+todate[6:8]+' 00:00:00'
            txtdat = "FROMDATE=" + str(fromdate) + " TODATE=" + str(todate)
            # FROM～TOの日付を表示
            window['TA1']. Update( txtdat )
            # データベース読込 -- analyzer --
            data_for_analysis_loaded = read_database.read_db_data_analyzer(fromdate, todate)
            data_for_analysis = simulatie_Investment_Indicators.add_nextday_return(data_for_analysis_loaded)
            txtdat = "株価・投資指標・財務データを読み込みました。"
            window['TA1']. Update( txtdat )
            # データベース読込 -- stockprice --
            #stockprice = read_database.read_db_data_stockprice(fromdate, todate)
            #data_for_stockprice = simulatie_Investment_Indicators.add_today_endprice(stockprice)
            #txtdat = "株価(前日終値、始値、安値、高値)データを読み込みました。"
            #window['TA1']. Update( txtdat )

    if event == 'btd1':
        s3 = sg.PopupYesNo('銘柄表示を実行してよろしいですか？',title='確認します',
            text_color='#ff0',background_color='#777',button_color=('#f00','#ccc'))
        if s3 == 'Yes':
            #
            txtds0 = '銘柄情報'
            window['DS0']. Update( txtds0 )
            #
            name = get_stockinfo.get_company_name(values['SC'])
            txtds1 = '銘柄名：' + name
            window['DS1']. Update( txtds1 )
            #
            name = get_stockinfo.get_market_name(values['SC'])
            txtdsb = 'マーケット：' + name
            window['DSB']. Update( txtdsb )
            #
            oprice, high,low,yearHigh,yearLow,volume,minUnit,avgTrade,mcap,per,pbr,yeld = get_stockinfo.get_stock_info(values['SC'])
            #
            name = oprice
            txtds2 = '始値：' + name
            window['DS2']. Update( txtds2 )
            #
            name = high
            txtds3 = '高値：' + name
            window['DS3']. Update( txtds3 )
            #
            name = low
            txtds4 = '安値：' + name
            window['DS4']. Update( txtds4 )
            #
            name = yearHigh
            txtds5 = '年高：' + name
            window['DS5']. Update( txtds5 )
            #
            name = yearLow
            txtds6 = '年安：' + name
            window['DS6']. Update( txtds6 )
            #
            name = volume
            txtds7 = '出来高：' + name
            window['DS7']. Update( txtds7 )
            #
            name = minUnit
            txtds8 = '単元株数：' + name
            window['DS8']. Update( txtds8 )
            #
            name = avgTrade
            txtds9 = '平均売買：' + name
            window['DS9']. Update( txtds9 )
            #
            name = mcap
            txtds10 = '時価総額：' + name
            window['DS10']. Update( txtds10 )
            #
            name = per
            txtds11 = 'PER：' + name
            window['DS11']. Update( txtds11 )
            #
            name = pbr
            txtds12 = 'PBR：' + name
            window['DS12']. Update( txtds12 )
            #
            name = yeld
            txtds13 = '配当利回：' + name
            window['DS13']. Update( txtds13 )
    
    if event == 'btd2':
        s4 = sg.PopupYesNo('指標グラフ表示を実行してよろしいですか？',title='確認します',
            text_color='#ff0',background_color='#777',button_color=('#f00','#ccc'))
        if s4 == 'Yes':
            if values['-LIST-']:
                # リストボックスから選択した指標名を取得
                target_indicate = values['-LIST-'][0]
                window['TA1']. Update( target_indicate )

                # 翌日収益率、翌日超過収益率の追加
                data_for_analysis = simulatie_Investment_Indicators.add_nextday_return(data_for_analysis_loaded)
                
                # リストボックスから選択した指標に基づくランキング（5段階）を行う。
                portfolio_sort_by = simulatie_Investment_Indicators.create_portfolio_by_one_variable(
                    data=data_for_analysis,
                    sort_by=target_indicate,
                    q=5,
                    labels=[1,2,3,4,5],
                    group_name='ランク'
                )
                
                # ランクごとの翌日収益率の日時平均（全SC）を算出する。グラフは最上位（1）と最下位(5)をプロット。
                portfolio_returns = portfolio_sort_by.groupby(
                    ['ランク', '日時']
                )['翌日収益率'].mean()
                
                # 翌日収益率の日時平均（全SC）を算出する。
                market_return = data_for_analysis.groupby(
                    '日時'
                )['翌日収益率'].mean().rename('単純平均リターン')
                
                # 対象SCの翌日収益率
                sc = int(values['SC'])
                target_returns = data_for_analysis.loc[(sc),'翌日収益率']
                
                # plotするデータの作成
                to_plot=portfolio_returns.unstack().T.filter(
                    items=[1, 5]
                ).rename(
                    columns={1:'乖離率 低', 5:'乖離率 高'}
                ).join(
                    market_return
                ).dropna(
                    how='all'
                ).join(
                    target_returns
                ).apply(
                    lambda column: np.log((column + 1).cumprod())
                )
                to_plot.columns.rename('ポートフォリオ', inplace=True)
                to_plot.to_excel('C:/Users/es/Documents/Python Scripts/6.GraduateMission/1.product/5.kadai_source/test/to_plot_graph.xlsx')
                
                # グラフの描画
                draw_plot_L1(target_indicate, to_plot)

window.close()
