import calendar
import datetime #datetime, timedelta
import jpholiday
import holidays
import os

class Date_Events:
    def __init__(self):
        self.year = ''
        self.data = []

    def display_data(self):
        for d in self.data:
            print(d)

    def load_events(self,year):
        self.year = year
        self.load_holidays()
        self.calendar_calc()
        self.load_boj()
        self.load_fomc()
        self.get_first_business_day()
        self.get_third_business_day()

        return self.data
    
    def load_boj(self):
        filename = 'boj-' + str(self.year) + '.csv'
        if os.path.exists(filename):
            with open(filename, encoding='utf-8') as f:
                data = f.readlines()
                self.set_data(data)
        else:
            pass

    def load_fomc(self):
        filename = 'fomc-' + str(self.year) + '.csv'
        if os.path.exists(filename):
            with open(filename, encoding='utf-8') as f:
                data = f.readlines()
                self.set_data(data)
        else:
            pass

    def set_data(self,datas):
        num = len(self.data)
        for n in range(num):
            for bd in datas:
                d = bd.split(',')
                if int(d[1]) == int(self.data[n][2]):
                    if int(d[2]) == int(self.data[n][3]):
                        self.data[n][4] += d[3].replace('\n','') + '　'

    def load_holidays(self):
        us_holidays = holidays.UnitedStates(years=self.year)
        data = []
        for month in range(1, 13):
            month_days = calendar.monthrange(self.year, month)[1]
            for day in range(1, month_days + 1):
                date = datetime.datetime(self.year, month, day)
                weekday = date.strftime("%a").lower()
                event = ""
                if jpholiday.is_holiday(date):
                    holiday_name = jpholiday.is_holiday_name(date)
                    event += f"祝日: {holiday_name}　"
                if date in us_holidays:
                    holiday_name = us_holidays.get(date)
                    event += f"米国祝日: {holiday_name}　"
                data.append([weekday, self.year, month, day, event])
        self.data = data

    def get_nth_weekday(self, nth_week, target_weekday):
        nth_weekdays = []
        for month in range(1, 13):
            month_calendar = calendar.monthcalendar(self.year, month)
            target_day = None
        
            # 指定された週目と曜日に基づいて日付を検索
            count = 0
            for week in month_calendar:
                if week[target_weekday] != 0:
                    count += 1
                    if count == nth_week:
                        target_day = week[target_weekday]
                        break
        
            if target_day is not None:
                nth_weekdays.append(f"{self.year},{month},{target_day}")

        return nth_weekdays

    def get_first_business_day(self):
        first_b = []
        #self.year = 2025
        for month in range(1,13):
            first_day = datetime.datetime(self.year,month,1)
            weekday = first_day.weekday()
            d = ''
            if weekday == 5: #土曜日
                d = first_day + datetime.timedelta(days=2)

            elif weekday == 6: #日曜日
                d = first_day + datetime.timedelta(days=1)
            else: #平日
                d = first_day
            data = d.strftime("%a,%#m,%#d") + ",ISM製造業景況感指数　"
            first_b.append(data)
        self.set_data(first_b)
        #return first_b

    def get_third_business_day(self):
        third_b = [] 
        #self.year = 2025 
        for month in range(1, 13): 
            first_day = datetime.datetime(self.year, month, 1) 
            weekday = first_day.weekday() # 第1営業日を計算 
            if weekday == 5: # 土曜日 
                first_business_day = first_day + datetime.timedelta(days=2) 
            elif weekday == 6: # 日曜日 
                first_business_day = first_day + datetime.timedelta(days=1) 
            else: 
                first_business_day = first_day 
            
            # 第3営業日を計算 
            third_business_day = first_business_day 
            business_days_count = 0 
            while business_days_count < 3: 
                if third_business_day.weekday() < 5: # 平日（月～金） 
                    business_days_count += 1 
                if business_days_count < 3: 
                    third_business_day += datetime.timedelta(days=1) 
            data = third_business_day.strftime("%a,%#m,%#d") + ",ISM非製造業景況感指数　"
            third_b.append(data)
        self.set_data(third_b)
        #return third_b



    def get_sq(self):
        return self.get_nth_weekday( 2, calendar.FRIDAY)

    def get_ussq(self):
        return self.get_nth_weekday( 3, calendar.FRIDAY)

    def get_CES(self):
        return self.get_nth_weekday( 1, calendar.FRIDAY)

    def get_ism_s(self):
        return self.get_nth_weekday( 1, calendar.MONDAY)

    def add_calendar(self, datelist, word):
        for d in datelist:
            year, month, day = map(int, d.split(','))
            for row in self.data:
                if row[1] == year and row[2] == month and row[3] == day:
                    row[4] += word

    def calendar_calc(self):
        self.add_calendar(self.get_sq(), "日本SQ　")
        self.add_calendar(self.get_ussq(), "米SQ　")
        self.add_calendar(self.get_CES(), "米国雇用統計　")   

    def get_today_year(self):
        today = datetime.date.today()
        return today.year
        

de = Date_Events()
#print(de.get_first_business_day())
#print(de.get_third_business_day())
#data = de.load_events(2025)
#de.load_boj()