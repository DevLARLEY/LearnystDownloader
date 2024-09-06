import glob
import json
import logging
from os import remove
from os.path import exists, join
from urllib.parse import urlparse

import requests


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
    bin_dir = "bin"
    return (
            exists(join(bin_dir, exe)) or
            exists(join(bin_dir, f"{exe}.exe"))
    )


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
