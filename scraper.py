import requests
from bs4 import BeautifulSoup
import csv
import os
import re

# スクレイピングクラス
class Scraper:
    def __init__(self):
        self.name = 'scraper'

    def fetch_data(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return self.get_html(response.text)
        except requests.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
            return None

    def get_html(self, data):
        return BeautifulSoup(data, 'lxml')

    def get_tables(self, html):
        return html.find_all("table")
    
    def save_to_csv(self, filename, lines): 
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile: 
            for line in lines:
                csvfile.write(line + '\n')  # 行を書き込み

class JPX_Data:
    def __init__(self):
        self.base_url = "https://www.jpx.co.jp/"
        self.scr = Scraper()
        self.display_data()

    def display_data(self):
        print(self.scr.fetch_data(self.base_url))
    

# BOJ日銀用クラス    
class BoJ_Data:
    def __init__(self):
        self.base_url = "https://www.boj.or.jp/"
        self.boj = Scraper()

    def schedule(self, url, year):
        html = self.boj.fetch_data(url)
        if html is None:
            return []
        tables = self.boj.get_tables(html)
        scdl = self.table_data(year, tables)
        return self.make_csv_data(scdl)
    
    def table_data(self, year, tables):
        data = []
        headers = []
        for table in tables:
            caption = table.find("caption")
            spld = "表　" + str(year) + "年"
            if caption and spld in caption.text:
                # ヘッダーの最初の行を取得
                header_rows = table.find("thead").find_all("tr")
                for header_row in header_rows:
                    header = [th.text.strip().replace('\n', ' ') for th in header_row.find_all("th")]
                    # フィルタリング：'各資料の公表日' を除外
                    header = [h for h in header if h != '各資料の公表日']
                    headers.extend(header)

                # データを抽出
                rows = table.find("tbody").find_all("tr")
                for row in rows:
                    cells = [cell.text.strip() for cell in row.find_all("td")]
                    data.append(cells)
 
        # ヘッダーの順番を入れ替える 
        if '総裁定例記者会見' in headers:
            headers.append(headers.pop(headers.index('総裁定例記者会見')))
            
        return headers, data

    def convert_date(self, date_str, base_month=None):
        days_mapping = {"月": "mon", "火": "tue", "水": "wed", "木": "thu", "金": "fri", "土": "sat", "日": "sun"}
        # フルパターン（例：1月23日（木））
        full_pattern = r"(\d+)月\s?(\d+)日（(\w)）"
        match = re.match(full_pattern, date_str)
        if match:
            month = match.group(1)
            day = match.group(2)
            day_of_week = match.group(3)
            day_of_week_eng = days_mapping.get(day_of_week)
            line = day_of_week_eng + "," + month + "," + day
            return line
        # 短縮パターン（例：24日（金））
        short_pattern = r"(\d+)日（(\w)）"
        match = re.match(short_pattern, date_str)
        if match:
            day = match.group(1)
            day_of_week = match.group(2)
            day_of_week_eng = days_mapping.get(day_of_week)
            line = day_of_week_eng + "," + (base_month if base_month else "") + "," + day
            return line
        return date_str

    def make_csv_data(self, data):
        lines = []
        num = len(data[0])
        base_month = None
        print(data[0])
        for row in data[1]:
            line = ''
            for n in range(num):
                if '・' in row[n]:
                    sub_row = row[n].split('・')
                    base_month = re.match(r"(\d+)月", sub_row[0]).group(1) if re.match(r"(\d+)月", sub_row[0]) else base_month
                    for sr in sub_row:
                        line = self.convert_date(sr, base_month) + ',' + data[0][n]
                        lines.append(line)
                        print(line)
                elif '-' in row[n]:
                    pass
                elif '未定' in row[n]:
                    pass
                else:
                    base_month = re.match(r"(\d+)月", row[n]).group(1) if re.match(r"(\d+)月", row[n]) else base_month
                    line = self.convert_date(row[n], base_month) + ',' + data[0][n]
                    lines.append(line)
                    print(line)
        print(lines)
        return lines

#bls = BLS_Data()
#Schedule = bls.schedule(bls.base_url,2025)

#boj = BoJ_Data()
jpx = JPX_Data()

#schedule = boj.schedule("https://www.boj.or.jp/mopo/mpmsche_minu/index.htm", 2025)
#filename = "boj-2025.csv"
#boj.boj.save_to_csv(filename, schedule)

#print(f"データが {filename} に保存されました。")
