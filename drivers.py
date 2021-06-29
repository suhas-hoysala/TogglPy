from start import *

def morning_time_entries():
    return time_entries_to_json(dt.strftime(dt.now(), '%m-%d-%y'), morning_times)

def afternoon_time_entries():
    return time_entries_to_json(dt.strftime(dt.now(), '%m-%d-%y'), afternoon_times)

