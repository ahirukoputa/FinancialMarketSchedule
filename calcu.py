import calendar 
import datetime 
import jpholiday 
import holidays 
import os

class CountryEvents:
    def __init__(self, year):
        self.year = year
        self.data = self.initialize_dates()

    def initialize_dates(self):
        data = []
        for month in range(1, 13):
            month_days = calendar.monthrange(self.year, month)[1]
            for day in range(1, month_days + 1):
                date = datetime.datetime(self.year, month, day)
                weekday = date.strftime("%a").lower()
                data.append([weekday, self.year, month, day, ''])
        return data

    def add_holidays(self):
        pass

    def load_external_events(self, event_name):
        filename = f'{event_name}-{self.year}.csv'
        if os.path.exists(filename):
            with open(filename, encoding='utf-8') as f:
                data = f.readlines()
                self.set_event_data(data)

    def set_event_data(self, datas):
        for bd in datas:
            d = bd.split(',')
            for row in self.data:
                if int(d[1]) == int(row[2]) and int(d[2]) == int(row[3]):
                    row[4] += d[3].strip() 

    def adjust_date_if_holiday(self, date):
        pass

    def calculate_first_business_day(self, month):
        first_day = datetime.datetime(self.year, month, 1)
        if first_day.weekday() == 5:  # 土曜日
            first_day += datetime.timedelta(days=2)
        elif first_day.weekday() == 6:  # 日曜日
            first_day += datetime.timedelta(days=1)
        return self.adjust_date_if_holiday(first_day)

    def calculate_nth_business_day(self, month, nth_business_day):
        first_business_day = self.calculate_first_business_day(month)
        business_day = first_business_day
        business_days_count = 1
        while business_days_count < nth_business_day:
            business_day += datetime.timedelta(days=1)
            if business_day.weekday() < 5 and not self.is_holiday(business_day):  # 平日で祝日でない場合
                business_days_count += 1
        return business_day

    def is_holiday(self, date):
        return False

    def add_event_on_nth_business_day(self, event_name, nth_business_day):
        for month in range(1, 13):
            business_day = self.calculate_nth_business_day(month, nth_business_day)
            for row in self.data:
                if row[1] == business_day.year and row[2] == business_day.month and row[3] == business_day.day:
                    row[4] += f"{event_name}　"

class JapanEvents(CountryEvents):
    def __init__(self, year):
        super().__init__(year)
        self.add_holidays()

    def add_holidays(self):
        for row in self.data:
            date = datetime.datetime(row[1], row[2], row[3])
            if jpholiday.is_holiday(date):
                holiday_name = jpholiday.is_holiday_name(date)
                row[4] += f"祝日: {holiday_name}　" 

    def adjust_date_if_holiday(self, date):
        while jpholiday.is_holiday(date) or date.weekday() >= 5:
            date += datetime.timedelta(days=1)
        return date

    def is_holiday(self, date):
        return jpholiday.is_holiday(date)

class USEvents(CountryEvents):
    def __init__(self, year):
        super().__init__(year)
        self.us_holidays = holidays.UnitedStates(years=year)
        self.add_holidays()

    def add_holidays(self):
        for row in self.data:
            date = datetime.datetime(row[1], row[2], row[3])
            if date in self.us_holidays:
                holiday_name = self.us_holidays.get(date)
                row[4] += f"米国祝日: {holiday_name}　"

    def adjust_date_if_holiday(self, date):
        while date in self.us_holidays or date.weekday() >= 5:
            date += datetime.timedelta(days=1)
        return date

    def is_holiday(self, date):
        return date in self.us_holidays

class DataEvents:
    def __init__(self):
        self.japan_events = None
        self.us_events = None
        self.data = []

    def load_events(self, year):
        #ここでデータを初期化
        self.data = []
        self.japan_events = JapanEvents(year)
        self.us_events = USEvents(year)
        self.add_specific_events()
        self.import_specific_events()
        self.merge_data()
        return self.data

    def import_specific_events(self):
        self.japan_events.load_external_events('boj')
        self.us_events.load_external_events('fomc')
        self.us_events.load_external_events('ppi')
        self.us_events.load_external_events('cpi')
        self.us_events.load_external_events('cpe')

    def add_specific_events(self):
        self.japan_events.add_event_on_nth_business_day("日本SQ　", 2)
        self.us_events.add_event_on_nth_business_day("米SQ　", 3)
        self.us_events.add_event_on_nth_business_day("米国雇用統計　", 1)
        self.us_events.add_event_on_nth_business_day("ISM製造業景況感指数　", 1)
        self.us_events.add_event_on_nth_business_day("ISM非製造業景況感指数　", 3)

    def merge_data(self):
        for i in range(len(self.japan_events.data)):
            self.data.append([
                self.japan_events.data[i][0],  # Weekday
                self.japan_events.data[i][1],  # Year
                self.japan_events.data[i][2],  # Month
                self.japan_events.data[i][3],  # Day
                self.japan_events.data[i][4] + self.us_events.data[i][4]  # Events
            ])

    def display_data(self):
        for d in self.data:
            print(d)

    def get_today_year(self):
        today = datetime.date.today()
        return today.year
    
    def get_data(self):
        return self.data

# インスタンス作成とメソッドの呼び出し
#data_events = DataEvents()
#data_events.load_events(2025)
#print(len(data_events.get_data()))


