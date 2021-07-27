from drivers import *

now = dt.now()
if now.time() > datetime.time(13, 30):
    morning_time_entries()

if now.time() > datetime.time(18, 00):
    afternoon_time_entries()

if now.time() > datetime.time(22, 00):
    evening_time_entries()

if now.time() > datetime.time(3, 00) and now.time() < datetime.time(6, 00):
    full_day_time_entries()

weekly_time_entries()