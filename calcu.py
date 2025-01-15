import calendar 
import datetime 
import jpholiday 
import holidays 
import os
import pandas as pd
import config

class CountryEvents:
    def __init__(self, year):
        print("countryevents")
        self.year = year

    def initialize_dates(self):
        print("countryevents_initialize_dates")
        data = []
        for month in range(1, 13):
            month_days = calendar.monthrange(self.year, month)[1]
            for day in range(1, month_days + 1):
                date = datetime.datetime(self.year, month, day)
                weekday = date.strftime("%a").lower()
                row = [weekday, self.year, month, day]
                for _ in range(len(config.treeview_columns) - len(row)):
                    row.append('')
                data.append(row)
        return pd.DataFrame(data, columns=config.treeview_columns)

    def save_schedule_to_csv(self, data, filename):
        print("countryevents_save_schedule_to_csv")
        data.sort_values(by=['year', 'month', 'day'], inplace=True)
        data.to_csv(filename, index=False, encoding='utf-8')

    def save_individual_events_to_csv(self, data, event_name, filename):
        print("countryevents_save_individual_events_to_csv")
        event_data = data[data['event'].str.contains(event_name, na=False)]
        
        # カラム名の存在確認
        missing_columns = [col for col in config.init_data_columns if col not in event_data.columns]
        if missing_columns:
            raise KeyError(f"Missing columns: {missing_columns}")

        event_data = event_data.loc[:, [col for col in config.init_data_columns if col in event_data.columns]].drop_duplicates()
        event_data.sort_values(by=['year', 'month', 'day'], inplace=True)
        event_data.to_csv(filename, index=False, encoding='utf-8')

    def add_event_on_nth_business_day(self, data, event_name, nth_business_day):
        print("countryevents_add_event_on_nth_business_day")
        for month in range(1, 13):
            business_day = self.calculate_nth_business_day(data, month, nth_business_day)
            if business_day is not None:
                data.loc[
                    (data['year'] == business_day.year) &
                    (data['month'] == business_day.month) &
                    (data['day'] == business_day.day),
                    'event'
                ] += f"【{event_name}】"

    def calculate_nth_business_day(self, data, month, nth_business_day):
        print("countryevents_calculate_nth_business_day")
        first_business_day = self.calculate_first_business_day(data, month)
        if first_business_day is None:
            return None

        business_day = first_business_day
        business_days_count = 1
        while business_days_count < nth_business_day:
            business_day += datetime.timedelta(days=1)
            if business_day.weekday() < 5 and not self.is_holiday(business_day):
                business_days_count += 1
        return business_day

    def calculate_first_business_day(self, data, month):
        print("countryevents_calculate_first_business_day")
        first_day = datetime.datetime(self.year, month, 1)
        if first_day.weekday() == 5:  # 土曜日
            first_day += datetime.timedelta(days=2)
        elif first_day.weekday() == 6:  # 日曜日
            first_day += datetime.timedelta(days=1)
        return self.adjust_date_if_holiday(first_day)

    def is_holiday(self, date):
        # 日本の祝日を考慮
        return jpholiday.is_holiday(date)

    def adjust_date_if_holiday(self, date):
        print("countryevents_adjust_date_if_holiday")
        while self.is_holiday(date) or date.weekday() >= 5:
            date += datetime.timedelta(days=1)
        return date


class JapanEvents(CountryEvents):
    def __init__(self, year):
        print("japanevents")
        super().__init__(year)

    def add_holidays(self, data):
        print("japanevents_add_holidays")
        for index, row in data.iterrows():
            date = datetime.datetime(row['year'], row['month'], row['day'])
            if jpholiday.is_holiday(date):
                holiday_name = jpholiday.is_holiday_name(date)
                data.at[index, 'event'] += f"【日本祝日: {holiday_name}】"

    def is_holiday(self, date):
        return jpholiday.is_holiday(date)

class USEvents(CountryEvents):
    def __init__(self, year):
        print("usevents")
        super().__init__(year)
        self.us_holidays = holidays.UnitedStates(years=year)

    def add_holidays(self, data):
        print("usevents_add_holidays")
        for index, row in data.iterrows():
            date = datetime.datetime(row['year'], row['month'], row['day'])
            if date in self.us_holidays:
                holiday_name = self.us_holidays.get(date)
                data.at[index, 'event'] += f"【米国祝日: {holiday_name}】"

    def is_holiday(self, date):
        return date in self.us_holidays

class ScheduleSaver:
    def __init__(self):
        print("schedulesaver")
        self.japan_events = None
        self.us_events = None

    def load_events(self, year):
        print("schedulesaver_load_events")
        self.japan_events = JapanEvents(year)
        self.us_events = USEvents(year)
        self.add_specific_events()

    def add_specific_events(self):
        print("schedulesaver_add_specific_events")
        japan_data = self.japan_events.initialize_dates()
        self.japan_events.add_holidays(japan_data)
        self.japan_events.add_event_on_nth_business_day(japan_data, "日本SQ", 2)
        self.japan_events.save_individual_events_to_csv(japan_data, "日本SQ", 'japan_sq_events.csv')

        us_data = self.us_events.initialize_dates()
        self.us_events.add_holidays(us_data)
        self.us_events.add_event_on_nth_business_day(us_data, "米SQ", 3)
        self.us_events.save_individual_events_to_csv(us_data, "米SQ", 'us_sq_events.csv')

        us_data = self.us_events.initialize_dates()
        self.us_events.add_holidays(us_data)
        self.us_events.add_event_on_nth_business_day(us_data, "米国雇用統計", 1)
        self.us_events.save_individual_events_to_csv(us_data, "米国雇用統計", 'us_employment_events.csv')

        us_data = self.us_events.initialize_dates()
        self.us_events.add_holidays(us_data)
        self.us_events.add_event_on_nth_business_day(us_data, "ISM製造業景況感指数", 1)
        self.us_events.save_individual_events_to_csv(us_data, "ISM製造業景況感指数", 'us_ism_manufacturing_events.csv')

        us_data = self.us_events.initialize_dates()
        self.us_events.add_holidays(us_data)
        self.us_events.add_event_on_nth_business_day(us_data, "ISM非製造業景況感指数", 3)
        self.us_events.save_individual_events_to_csv(us_data, "ISM非製造業景況感指数", 'us_ism_nonmanufacturing_events.csv')

class ScheduleLoader:
    def __init__(self, filename):
        self.filename = filename
        print("scheduleloader")

    def load_schedule_from_csv(self):
        print("scheduleloader_load_schedule_from_csv")
        if os.path.exists(self.filename):
            return pd.read_csv(self.filename)
        else:
            print(f"File {self.filename} not found.")
            return pd.DataFrame(columns=config.treeview_columns)

class DataEvents:
    def __init__(self):
        print("dataevents")
        self.data = pd.DataFrame(columns=config.treeview_columns)

    def load_annual_data(self, year):
        print("dataevents_load_annual_data")
        japan_events = JapanEvents(year)
        us_events = USEvents(year)
        
        japan_data = japan_events.initialize_dates()
        japan_events.add_holidays(japan_data)
               
        us_data = us_events.initialize_dates()
        us_events.add_holidays(us_data)
            
        for i in range(len(japan_data)):
            japan_data.at[i, 'event'] += us_data.at[i, 'event']

        self.data = japan_data.copy()

    def merge_data(self, schedule_data):
        print("dataevents_merge_data")
        event_index = 'event'
        for index, row in schedule_data.iterrows():
            mask = (
                (self.data['year'] == row['year']) &
                (self.data['month'] == row['month']) &
                (self.data['day'] == row['day'])
            )
            self.data.loc[mask, event_index] += row[event_index]
    
    def merge_finance_data(self, finance_data):
        print("dataevents_merge_finance_data")
        
        # 数値型変換
        for col in config.finance_columns:
            self.data[col] = pd.to_numeric(self.data[col], errors='coerce').fillna(0)
            finance_data[col] = pd.to_numeric(finance_data[col], errors='coerce').fillna(0)
        
        for index, row in finance_data.iterrows():
            mask = (
                (self.data['year'] == row['year']) &
                (self.data['month'] == row['month']) &
                (self.data['day'] == row['day'])
            )
            for col in config.finance_columns:
                self.data.loc[mask, col] += row[col]

    def load_and_merge_schedules(self, filenames):
        print("dataevents_load_and_merge_schedules")
        for filename in filenames:
            loader = ScheduleLoader(filename)
            schedule_data = loader.load_schedule_from_csv()
            self.merge_data(schedule_data)
            
    def load_finance_and_merge_schedules(self, filename):
        print("dataevents_load_finance_and_merge_schedules")
        loader = ScheduleLoader(filename)
        finance_data = loader.load_schedule_from_csv()
        self.merge_finance_data(finance_data)  

    def display_schedule(self):
        print("dataevents_display_schedule")
        for row in self.data.itertuples():
            print(row)
            
    def get_today_year(self):
        print("dataevents_get_today_year")
        today = datetime.date.today()
        return today.year
    
    def get_data(self):
        print("dataevents_get_data")
        return self.data

if __name__ == "__main__":
    
    print("year : ",config.current_year,type(config.current_year))
    data_events = DataEvents()
    data_events.load_annual_data(config.current_year)
    ss = ScheduleSaver()
    ss.load_events(config.current_year)

    data_events.load_and_merge_schedules(config.event_filenames)

    data_events.display_schedule()