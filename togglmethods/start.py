from secrets import api_token
from types import *
from multipledispatch.core import dispatch
import requests
from datetime import datetime as dt
from datetime import date, timedelta
from dateutil import parser
import datetime
from arrow import Arrow
from pathlib import Path
import json
from json.decoder import JSONDecodeError

auth = (api_token, 'api_token')

workspace_id = requests.get(
    'https://api.track.toggl.com/api/v8/workspaces', auth=auth).json()[0]['id']


def time_entries_in_range(start_time, end_time):
    iso1 = Arrow.strptime(start_time, '%m-%d-%y %I:%M %p',
                          tzinfo='America/New_York').isoformat()
    iso2 = Arrow.strptime(end_time, '%m-%d-%y %I:%M %p',
                          tzinfo='America/New_York').isoformat()

    uri = f'https://api.track.toggl.com/api/v8/time_entries?start_date={iso1}&end_date={iso2}'

    try:
        return requests.get(uri, auth=auth).json()
    except(ValueError, JSONDecodeError):
        return {}

def get_date_change(day: str = None, start_day: str = 'Wed'):
    if not day:
        day = date.today()
    else:
        day = parser.parse(day)
    
    start_day = parser.parse(start_day)

    start_day_offset = (day.weekday() - start_day) % 7
    end_day_offset = -(day.weekday() - (start_day-1)) % 7
    start_day_date = day - timedelta(days=start_day_offset)
    end_day_date = day + timedelta(days=end_day_offset)

    return f'{start_day_date.month}-{start_day_date.day}-{start_day_date.year}', f'{end_day_date.month}-{end_day_date.day}-{end_day_date.year}'

def by_times(date1, date2, time1, time2):
    start_time = f'{date1} {time1}'
    end_time = f'{date2} {time2}'
    return time_entries_in_range(start_time, end_time)

def morning_times(date=None):
    if not date:
        date = dt.strftime(dt.now(), '%m-%d-%y')
    return by_times(date, date, '3:00 am', '1:30 pm')


def afternoon_times(date=None):
    if not date:
        date = dt.strftime(dt.now(), '%m-%d-%y')
    return by_times(date, date, '1:30 pm', '6:00 pm')

def evening_times(date=None):
    if not date:
        date = dt.strftime(dt.now(), '%m-%d-%y')
    return by_times(date, date, '6:00 pm', '10:00 pm')

def full_day_times(date=None):
    if not date:
        date = dt.strftime(dt.now() - datetime.timedelta(days=1), '%m-%d-%y')
    return by_times(date, date, '12:00 am', '11:59 pm')

def weekly_times(date: str =None, start_day: str = None):
    if not date:
        date = dt.strftime(dt.now(), '%m-%d-%y')
    
    date1, date2 = get_date_change(date, start_day)
    
    return by_times(date1, date2, '12:00 am', '11:59 pm')

def get_projects():
    uri_projects = f'https://api.track.toggl.com/api/v8/workspaces/{workspace_id}/projects'
    try:
        return requests.get(uri_projects, auth=auth).json()
    except(ValueError, JSONDecodeError):
        return {}

def proj_id_from_name(proj_name):
    project_list = get_projects()
    for proj_rec in project_list:
        if proj_rec['name'] == proj_name:
            proj_id = proj_rec['id']
            break

    return proj_id


def time_entry_list_from_proj_name(proj_name, time_entries_list):
    return_list = []

    proj_id = proj_id_from_name(proj_name)

    for entry_rec in time_entries_list:
        if entry_rec.get('pid') == proj_id:
            return_list.append(entry_rec)

    return return_list


def time_entry_list_from_proj_id(proj_id, time_entries_list):
    return_list = []

    for entry_rec in time_entries_list:
        if entry_rec.get('pid') == proj_id:
            return_list.append(entry_rec)

    return return_list


@dispatch(str)
def time_entry_list_by_project(date):
    start_time = dt.strftime(dt.strptime(
        date, '%m-%d-%y'), '%m-%d-%y 12:00 am')
    end_time = dt.strftime(dt.strptime(date, '%m-%d-%y'), '%m-%d-%y 11:59 pm')

    return time_entries_in_range(start_time, end_time)


@dispatch()
def time_entry_list_by_project():
    start_time = dt.strftime(datetime.date.today(), '%m-%d-%y 12:00 am')
    end_time = dt.strftime(datetime.date.today(), '%m-%d-%y 11:59 pm')

    return time_entries_in_range(start_time, end_time)

@dispatch(str, LambdaType)
def time_entries_to_json(date, get_method):
    project_list = get_projects()
    time_entries_list = get_method(date)
    method_name = get_method.__name__
    file_name = f'{date}_{method_name}.json'

    return_dict = {}
    for project_rec in project_list:
        proj_name = project_rec['name']
        proj_id = project_rec['id']
        return_dict[proj_name] = time_entry_list_from_proj_id(
            proj_id, time_entries_list)

    write_file = Path(__file__).parent / f'../data/{file_name}'
    json.dump(return_dict, write_file.open('w+'))

    return return_dict


@dispatch(str, str, str, str)
def time_entries_to_json(date1, date2, time1, time2):
    time_entries_list = by_times(date1, date2, time1, time2)
    project_list = get_projects()
    file_name = f'{date1}_{time1}_to_{date2}_{time2}'
    return_dict = {}
    for project_rec in project_list:
        proj_name = project_rec['name']
        proj_id = project_rec['id']
        return_dict[proj_name] = time_entry_list_from_proj_id(
            proj_id, time_entries_list)

    write_file = Path(__file__).parent / f'../data/{file_name}.json'.replace(':', '').replace(' ', '_')
    json.dump(return_dict, write_file.open('w+'))

    return return_dict

@dispatch(str, str)
def time_entries_to_json(date1, date2):
    return time_entries_to_json(date1, date2, '12:00 am', '11:59 pm')

