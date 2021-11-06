from typing import List
from .secrets import api_token
from types import *
from multipledispatch.core import dispatch
import requests
from datetime import datetime as dt, timezone
from datetime import date, timedelta
from dateutil import parser
import datetime
from arrow import Arrow
from pathlib import Path
import json
import tenacity
from typing import Union
from requests.models import Response
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class TogglWrapper:
    def __init__(self, auth):
        self.auth=auth
    class ErrException(Exception):
        pass
    def get_new_session():
        session = requests.Session()
        retry = Retry(total=100, connect=100, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def delete(
        self, path: str, raw: bool = False, **kwargs
    ) -> Union[list, dict, Response]:
        """makes a put request to the API"""
        s = TogglWrapper.get_new_session()
        request = s.delete(path, auth=self.auth, **kwargs).json()
        return request

    def get(self, path: str, raw: bool = False, **kwargs
            ) -> Union[list, dict, Response]:
        s = TogglWrapper.get_new_session()
        request = s.get(path, auth=self.auth, **kwargs).json()
        return request

    def post(self, path: str, **kwargs
             ) -> Union[list, dict, Response]:
        s = TogglWrapper.get_new_session()
        request = s.post(path, auth=self.auth, **kwargs).json()
        return request

    def put(self, path: str, **kwargs
            ) -> Union[list, dict, Response]:
        s = TogglWrapper.get_new_session()
        request = s.put(path, auth=self.auth, **kwargs).json()
        return request

auth = (api_token, 'api_token')
toggl_wrapper = TogglWrapper(auth)
workspace_id = toggl_wrapper.get(
    'https://api.track.toggl.com/api/v8/workspaces')[0]['id']


def get_project_id_from_name(name: str = 'General', wid: int = workspace_id):
    projects = get_projects(wid)
    project_list = [rec for rec in projects if rec['name'] == name]
    return project_list[0]['id'] if project_list else None


def create_time_entry(description: str, start: datetime, duration: int, wid: int = workspace_id,
                      pid: int = None, tags: List[str] = []):
    fmt_string = '%m-%d-%y %I:%M %p'
    iso1 = Arrow.strptime(dt.strftime(start, fmt_string), fmt_string,
                          tzinfo='America/New_York').isoformat()
    task = {
        'time_entry': {
            'description': description,
            'wid': wid,
            'start': iso1,
            'duration': duration,
            'created_with': 'togglmethods',
            'tags': tags
        }
    }
    if pid != None:
        task['pid'] = pid

    print(json.dumps(task, indent=4))

    uri = 'https://api.track.toggl.com/api/v8/time_entries'
    return toggl_wrapper.post(uri, json=task)


@dispatch(str, str)
def time_entries_in_range(start_time, end_time):
    iso1 = Arrow.strptime(start_time, '%m-%d-%y %I:%M %p',
                          tzinfo='America/New_York').isoformat()
    iso2 = Arrow.strptime(end_time, '%m-%d-%y %I:%M %p',
                          tzinfo='America/New_York').isoformat()

    uri = f'https://api.track.toggl.com/api/v8/time_entries?start_date={iso1}&end_date={iso2}'

    return toggl_wrapper.get(uri)


@dispatch(dt, dt)
def time_entries_in_range(start_time, end_time):
    return time_entries_in_range(dt.strftime(start_time, '%m-%d-%y %I:%M %p'),
                                 dt.strftime(end_time, '%m-%d-%y %I:%M %p'))


def get_date_change(day: str = None, start_day: str = 'Wed'):
    if not day:
        day = date.today()
    else:
        day = parser.parse(day)

    start_day = parser.parse(start_day).weekday()

    start_day_offset = (day.weekday() - start_day) % 7
    end_day_offset = -(day.weekday() - (start_day-1)) % 7
    start_day_date = day - timedelta(days=start_day_offset)
    end_day_date = day + timedelta(days=end_day_offset)

    return (f'{start_day_date.month}-{start_day_date.day}-{str(start_day_date.year)[-2:]}',
            f'{end_day_date.month}-{end_day_date.day}-{str(end_day_date.year)[-2:]}')


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


def weekly_times(date: str = None, start_day: str = None):
    if not date:
        date = dt.strftime(dt.now(), '%m-%d-%y')

    date1, date2 = get_date_change(
        date, start_day) if start_day else get_date_change(date)

    return by_times(date1, date2, '12:00 am', '11:59 pm')


def get_projects(wid: int = workspace_id):
    uri_projects = f'https://api.track.toggl.com/api/v8/workspaces/{wid}/projects'
    return toggl_wrapper.get(uri_projects)


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

    write_file = Path(__file__).parent / \
        f'./data/{file_name}'.replace(':', '').replace(' ', '_')

    write_file.parent.mkdir(parents=True, exist_ok=True)
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

    write_file = Path(__file__).parent / \
        f'./data/{file_name}.json'.replace(':', '').replace(' ', '_')

    write_file.parent.mkdir(parents=True, exist_ok=True)
    json.dump(return_dict, write_file.open('w+'))

    return return_dict


@dispatch(str, str)
def time_entries_to_json(date1, date2):
    return time_entries_to_json(date1, date2, '12:00 am', '11:59 pm')
