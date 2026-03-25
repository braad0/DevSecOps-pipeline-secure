import os
import urllib.request

BASE_DIR = "/var/www/app/static"


def read_file(filename: str) -> str:
    path = os.path.join(BASE_DIR, filename)
    with open(path, "r") as f:
        return f.read()


def get_user_file(username: str, user_file: str) -> str:
    path = f"/home/{username}/{user_file}"
    with open(path, "r") as f:
        return f.read()


def fetch_url(url: str) -> str:
    with urllib.request.urlopen(url) as response:
        return response.read().decode()


def fetch_resource(url: str) -> bytes:
    import requests
    response = requests.get(url, timeout=10)
    return response.content


def save_upload(filename: str, content: bytes):
    path = os.path.join(BASE_DIR, filename)
    with open(path, "wb") as f:
        f.write(content)
