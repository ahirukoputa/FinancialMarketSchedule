#フォームサイズ
form_width = 1200
form_height = 500

#総合データの基準
treeview_columns = ("weekday", "year", "month", "day", "n225","usdjpy", "dji", "ixic", "sp500", "event")
treeview_columns_text = ("W","Y","M","D","N225","USDJPY","DJI","IXIC","SP500","EVENTS")

#個別データ用
init_data_columns = ("weekday", "year", "month", "day", "event")

#ファイナスデータ用
finance_data_columns = ("weekday", "year", "month", "day", "n225","usdjpy", "dji", "ixic", "sp500")
#
finance_columns = ("n225","usdjpy", "dji", "ixic", "sp500")

#tk.NO=False tk.YES=True
column_configs = {
    'weekday':{'width': 40,'anchor': 'w','stretch': False},
    'year':{'width': 45,'anchor': 'center','stretch': False},
    'month':{'width': 25,'anchor': 'e','stretch': False},
    'day':{'width': 30,'anchor': 'e','stretch': False},
    'n225':{'width': 65,'anchor': 'e','stretch': False},
    'usdjpy':{'width': 65,'anchor': 'e','stretch': False},
    'dji':{'width': 65,'anchor': 'e','stretch': False},
    'ixic':{'width': 65,'anchor': 'e','stretch': False},
    'sp500':{'width': 65,'anchor': 'e','stretch': False},
    'event':{'width': 300,'anchor': 'w','stretch': True}
} 
tag_configs = {
    'saturday': {'foreground': 'blue', 'background': ''},
    'sunday': {'foreground': 'red', 'background': ''},
    'evenrow': {'foreground': '', 'background': 'white'},
    'oddrow': {'foreground': '', 'background': '#eeeeee'}    
}

finance_url_Data = (
    "https://finance.yahoo.co.jp/quote/998407.O/news",
    "https://finance.yahoo.co.jp/quote/USDJPY=FX",
    "https://finance.yahoo.co.jp/quote/%5EDJI/news",
    "https://finance.yahoo.co.jp/quote/%5EIXIC/news",
    "https://finance.yahoo.co.jp/quote/%5EGSPC/news"
)
finance_zone = ("jp","jp","us","us","us")

current_year = 2025
event_filenames = (f'boj-{current_year}.csv',
                   f'fomc-{current_year}.csv',
                   f'cpe-{current_year}.csv',
                   f'cpi-{current_year}.csv',
                   f'ppi-{current_year}.csv',
                   f'seu-{current_year}.csv',
                   'japan_sq_events.csv',
                   'us_sq_events.csv',
                   'us_employment_events.csv',
                   'us_ism_manufacturing_events.csv',
                   'us_ism_nonmanufacturing_events.csv'
                   )

