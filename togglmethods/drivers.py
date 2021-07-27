from start import *

def morning_time_entries(date: str=None):
    if not date:
        date = dt.now()
    else:
        date = parser.parse(date)
    return time_entries_to_json(dt.strftime(date, '%m-%d-%y'), morning_times)

def afternoon_time_entries(date: str=None):
    if not date:
        date = dt.now()
    else:
        date = parser.parse(date)
    return time_entries_to_json(dt.strftime(date, '%m-%d-%y'), afternoon_times)

def evening_time_entries(date: str=None):
    if not date:
        date = dt.now()
    else:
        date = parser.parse(date)
    return time_entries_to_json(dt.strftime(date, '%m-%d-%y'), evening_times)

def full_day_time_entries(date: str=None):
    if not date:
        date = dt.now()
    else:
        date = parser.parse(date)
    return time_entries_to_json(dt.strftime(date, '%m-%d-%y'), full_day_times)

def weekly_time_entries(date: str=None):
    if not date:
        date = dt.now()
    else:
        date = parser.parse(date)
    return time_entries_to_json(dt.strftime(date, '%m-%d-%y'), weekly_times)

def run_all(date:str=None):
    if not date:
        date = dt.now()
    else:
        date = parser.parse(date)
    
    return [morning_time_entries(date), afternoon_time_entries(date), evening_time_entries(date), 
    full_day_time_entries(date), weekly_time_entries(date)]

