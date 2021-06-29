from drivers import *

now = dt.now()
if now.time() > datetime.time(13, 30):
    morning_time_entries()

if now.time() > datetime.time(18, 00):
    afternoon_times()