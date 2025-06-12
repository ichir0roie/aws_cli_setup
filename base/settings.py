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
