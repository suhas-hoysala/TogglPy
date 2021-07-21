from start import *

def morning_time_entries():
    return time_entries_to_json(dt.strftime(dt.now(), '%m-%d-%y'), morning_times)

def afternoon_time_entries():
    return time_entries_to_json(dt.strftime(dt.now(), '%m-%d-%y'), afternoon_times)

def evening_time_entries():
    return time_entries_to_json(dt.strftime(dt.now(), '%m-%d-%y'), evening_times)

def full_day_time_entries():
    return time_entries_to_json(dt.strftime(dt.now(), '%m-%d-%y'), full_day_times)
