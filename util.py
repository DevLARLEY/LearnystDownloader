import glob, os
import json
import logging
from os import remove
from os.path import exists
from urllib.parse import urlparse

import requests
from timeit import default_timer as timer


def handle(result, error: str):
    if not bool(result):
        logging.error(error)
        exit(1)


def ensure_list(element: dict | list):
    if isinstance(element, dict):
        return [element]
    return element


def is_token_valid(token: str) -> bool:
    response = requests.get(
        'https://api.learnyst.com/learner/v4/stats',
        headers={
            'Authorization': f'Bearer {token}'
        }
    )
    return response.status_code == 200


def executable_exists(exe: str) -> bool:
    directory = 'binary/'
    exe_path = os.path.join(directory, exe)
    exe_path_with_extension = os.path.join(directory, f"{exe}.exe")
    return os.path.exists(exe_path) or os.path.exists(exe_path_with_extension)


def try_parse(to_parse: str):
    try:
        return json.loads(to_parse)
    except Exception:
        pass


def remove_query(url: str) -> str:
    parsed = urlparse(url)
    return parsed.scheme + "://" + parsed.netloc + parsed.path


def clean(files: list):
    for file in files:
        for globs in glob.glob(file):
            if exists(globs):
                remove(globs)
