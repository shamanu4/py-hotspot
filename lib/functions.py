# -*- coding: utf-8 -*-

def date_formatter(date=None):
    import datetime

    if not date:
        date = datetime.datetime.now()

    day = date.day
    weekday = date.weekday()
    month = date.month
    year = date.year
    thisday = datetime.datetime(year, month, day)
    thisweek = datetime.datetime(year, month, day)-datetime.timedelta(weekday)
    thismonth = datetime.datetime(year, month, 1)
    thisyear = datetime.datetime(year, 1, 1)

    return { 'day':thisday, 'week':thisweek, 'month':thismonth, 'year':thisyear }

def add_months(sourcedate,months):
    import datetime
    import calendar
    
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month / 12
    month = month % 12 + 1
    day = min(sourcedate.day,calendar.monthrange(year,month)[1])
    return datetime.date(year,month,day)

