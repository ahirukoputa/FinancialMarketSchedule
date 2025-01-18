import requests
from bs4 import BeautifulSoup
import csv
import calendar
import datetime
import pandas as pd
import os
import config #初期設定

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
    
    def get_span(self, html):
        return html.find_all("span")
    
    def save_to_csv(self, filename, data): 
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile: 
            writer = csv.writer(csvfile)
            writer.writerow(config.finance_data_columns)
            writer.writerows(data)  # 全行を書き込み

    def load_from_csv(self, filename):
        if os.path.exists(filename):
            try:
                return pd.read_csv(filename)
            except pd.errors.EmptyDataError:
                print(f"{filename} is empty. Returning an empty DataFrame.")
                return pd.DataFrame(columns=config.finance_data_columns)
        else:
            return pd.DataFrame(columns=config.finance_data_columns)

class FinanceData:
    def __init__(self):
        self.urls = config.finance_url_Data
        self.zone = config.finance_zone
        self.scr = Scraper()
        self.data_filename = f"finance-{config.current_year}.csv"
        
        # ファイルあるかどうかを確認して読み込みまたは保存
        if os.path.exists(self.data_filename):
            self.data = self.scr.load_from_csv(self.data_filename)
            print(f"Data loaded from {self.data_filename}")
        else:
            self.data = self.initialize_dates()
            self.save_initialize_data()
            print(f"Data saved to {self.data_filename}")

    def initialize_dates(self):
        data = []
        for month in range(1, 13):
            month_days = calendar.monthrange(config.current_year, month)[1]
            for day in range(1, month_days + 1):
                date = datetime.datetime(config.current_year, month, day)
                weekday = date.strftime("%a").lower()
                data.append([weekday, config.current_year, month, day, 0, 0, 0, 0, 0])
        return pd.DataFrame(data, columns=config.finance_data_columns)

    def get_data(self):
        nums = ['0', '0', '0', '0', '0']
        for i, url in enumerate(self.urls):
            soup = self.scr.fetch_data(url)
            if soup:
                data = soup.find('span', class_="_StyledNumber__value_x0ii7_10") or soup.find('span', class_="number__3wVT") or soup.find('span', class_="_FxRateItem__number_1ye8x_48")
                if data:
                    nums[i] = data.get_text().replace(',', '')
                else:
                    print("Data span not found")
            else:
                print("Failed to fetch data from:", url)
        return nums
    
    def test_scraper(self,url):
        soup = self.scr.fetch_data(url)
        if soup:
            print(soup)
            

    def get_now(self):
        dt_now = datetime.datetime.now()
        return [dt_now.year, dt_now.month, dt_now.day, dt_now.hour, dt_now.minute]

    def get_yesterday(self): 
        dt_now = datetime.datetime.now() 
        dt_yesterday = dt_now - datetime.timedelta(days=1) 
        return [dt_yesterday.year, dt_yesterday.month, dt_yesterday.day]

    def prepare_data_for_save(self):
        dt_now = self.get_now()
        dt_yesterday = self.get_yesterday()
        current_data = self.get_data()
        test_datas = []
        print(current_data)
        # dt_now and dt_yesterday のデータを self.data に追加 
        for i, cd in enumerate(current_data): 
            test_data = ['','','','',''] 
            if self.zone[i] == "jp": 
                test_data = [dt_now[0], dt_now[1], dt_now[2], cd] 
            elif self.zone[i] == 'us': 
                test_data = [dt_yesterday[0], dt_yesterday[1], dt_yesterday[2], cd] 
            test_datas.append(test_data) 

        # test_datas を self.data に更新 
        for i, test_data in enumerate(test_datas): 
            for index, row in self.data.iterrows():
                if row['year'] == test_data[0] and row['month'] == test_data[1] and row['day'] == test_data[2]:
                    self.data.at[index, self.data.columns[4 + i]] = test_data[3]
                    break
                
        self.scr.save_to_csv(self.data_filename, self.data.values)

    def save_initialize_data(self):
        self.scr.save_to_csv(self.data_filename, self.data.values)

if __name__ == "__main__":
    # インスタンスを作成する
    fd = FinanceData()
    print(fd.get_now())
    fd.prepare_data_for_save()
    print(fd.data)
    
    #url = 'https://www.bls.gov/news.release/cpi.toc.htm' 
    #headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3' }

    #try:
    #    response = requests.get(url, headers=headers)
    #    response.raise_for_status()  # ステータスコードが200以外の場合に例外を発生
    #    soup = BeautifulSoup(response.text, 'lxml')
    #    time.sleep(2)  # リクエスト間隔を2秒に設定
        # ここにスクレイピング処理を続ける
    #except requests.RequestException as e:
    #    print(f"Error fetching data from {url}: {e}")
    
    #fd = FinanceData()
    #fd.get_now()
    #fd.test_scraper('https://www.bls.gov/')