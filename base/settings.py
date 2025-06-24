from datetime import datetime, timedelta
import os
from base.aws_setting import AwsSetting
import json


class Settings:
    aws_credential_path: str = None
    default_profile: str = None
    profiles: dict[str, AwsSetting]

    def __init__(self) -> None:
        with open("settings.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        self.aws_credential_path = data["aws_credential_path"]
        profiles: dict = data["profiles"]
        self.profiles = {}

        self.default_profile = data["default_profile"]

        for key, value in profiles.items():
            aws_setting = AwsSetting()
            aws_setting.set_mfa_info(profile=key, info=value)
            self.profiles[key] = aws_setting

        pass


def __read_profile_time() -> dict[str, datetime]:
    path = f"data/profile_time.json"
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write("{}")
            data = {}
    else:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    return data


def __save_profile_time(profile_time_data: dict[str, str]) -> None:
    path = f"data/profile_time.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile_time_data, f, indent=4)


def set_profile_time(profile: str) -> None:
    now = datetime.now()
    data = __read_profile_time()
    data[profile] = now.timestamp()
    __save_profile_time(data)


def check_profile_expire(profile: str) -> bool:
    data = __read_profile_time()
    timestamp = data.get(profile)
    if timestamp is None:
        return True
    date = datetime.fromtimestamp(float(timestamp))
    if datetime.now()-date > timedelta(hours=12):
        return True
    return False
