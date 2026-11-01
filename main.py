from datetime import datetime
from icalendar import Calendar, Event
from lunar_python import Solar

def generate_ics():
    current_year = datetime.now().year
    years = [current_year - 1, current_year, current_year + 1] # 去年、今年、明年
    
    # 初始化两个日历对象
    cal_yi = Calendar()
    cal_yi.add('prodid', '-//Lunar Yi Calendar//cn//')
    cal_yi.add('version', '2.0')
    cal_yi.add('X-WR-CALNAME', '黄历宜忌 - 宜')

    cal_ji = Calendar()
    cal_ji.add('prodid', '-//Lunar Ji Calendar//cn//')
    cal_ji.add('version', '2.0')
    cal_ji.add('X-WR-CALNAME', '黄历宜忌 - 忌')

    for year in years:
        # 判断闰年以确定天数
        start_date = datetime(year, 1, 1)
        end_date = datetime(year + 1, 1, 1)
        
        delta = (end_date - start_date).days
        for i in range(delta):
            d = start_date.fromordinal(start_date.toordinal() + i)
            solar = Solar.fromYmd(d.year, d.month, d.day)
            lunar = solar.getLunar()
            
            yi_list = lunar.getDayYi() # 获取宜
            ji_list = lunar.getDayJi() # 获取忌
            
            date_str = d.strftime('%Y%m%d')

            # 添加“宜”事件
            if yi_list:
                event_yi = Event()
                event_yi.add('summary', f"宜: {' '.join(yi_list)}")
                event_yi.add('dtstart', d.date())
                event_yi.add('dtend', d.date())
                event_yi.add('description', f"农历{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}，宜：{', '.join(yi_list)}")
                cal_yi.add_component(event_yi)

            # 添加“忌”事件
            if ji_list:
                event_ji = Event()
                event_ji.add('summary', f"忌: {' '.join(ji_list)}")
                event_ji.add('dtstart', d.date())
                event_ji.add('dtend', d.date())
                event_ji.add('description', f"农历{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}，忌：{', '.join(ji_list)}")
                cal_ji.add_component(event_ji)

    # 保存文件
    with open('yi.ics', 'wb') as f:
        f.write(cal_yi.to_ical())
    with open('ji.ics', 'wb') as f:
        f.write(cal_ji.to_ical())
    
    print("ICS files generated successfully for years:", years)

if __name__ == '__main__':
    generate_ics()
