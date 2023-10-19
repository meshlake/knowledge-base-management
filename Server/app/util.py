from datetime import datetime
import os
import random
import string
import re
import json
import time


def uniqueFileName(fileName: str):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # 获取当前的日期和时间戳
    new_file_name = f"{os.path.splitext(fileName)[0]}_{timestamp}{os.path.splitext(fileName)[1]}"  # 新的带时间戳的文件名
    return new_file_name


def generate_api_key():
    api_key = ""
    characters = string.ascii_letters + string.digits
    length = 32  # API密钥的长度

    for _ in range(length):
        random_index = random.randint(0, len(characters) - 1)
        api_key += characters[random_index]

    return api_key


def is_path_in_whitelist(path: str, whitelist: list):
    for route in whitelist:
        pattern = re.sub(r"{\w+}", r"(.*)", route)  # 将路径参数替换为通配符
        if re.match(pattern, path):
            return True
    return False


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True


def is_valid_password(password):
    # 校验密码长度
    if len(password) < 8 or len(password) > 20:
        return False

    # 校验密码是否包含数字和字母
    if not (re.search(r"\d", password) and re.search(r"[a-zA-Z]", password)):
        return False

    return True


def get_pages(total: int, size: int):
    if total == 0:
        return 0
    if total % size == 0:
        return total // size
    else:
        return total // size + 1

def retry(func, *args, **kwargs):
    for retry in range(3):
        try:
            result = func(*args, **kwargs)
            return result  # 如果成功执行函数，立即返回结果
        except Exception as e:
            print(f"Attempt {retry + 1} failed with error: {str(e)}")
            if retry < 2:
                print(f"Retrying in 2 seconds...")
                time.sleep(2)
    raise Exception(f"Function failed after 3 retries")