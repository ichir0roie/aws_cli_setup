from genericpath import exists
import profile
import shutil
import subprocess as sp
import os
import ast

import pyotp

from base.aws_setting import AwsSetting
from base.settings import *

from base.const import *

import time

import os


class CredentialsUpdator:
    def __init__(self):
        self.settings: Settings = Settings()

    def backup_cred_file(self):
        shutil.copy(self.settings.aws_credential_path,
                    self.settings.aws_credential_path + "_bk")

    def reset_cred_file(self):
        with open(self.settings.aws_credential_path, "w", encoding="utf-8") as f:
            f.write("")

    def overwrite_session_info(self, default_profile: str = None, preset: bool = False) -> None:
        cred_text = self.__generate_session_info_text(default_profile, preset)
        with open(self.settings.aws_credential_path, "w", encoding="utf-8") as f:
            f.write(cred_text)

    def __generate_session_info_text(self, default_profile: str = None, preset: bool = False) -> str:
        text_all = ""
        text_default = ""
        default_profile = default_profile if default_profile is not None else self.settings.default_profile
        for key, aws_setting in self.settings.profiles.items():
            text_all += self.__generate_update_text(aws_setting, None, preset)
            if key == default_profile:
                text_default = self.__generate_update_text(
                    aws_setting, "default", preset)
                # self.export_env(aws_setting)
        text_all = text_default + text_all
        return text_all

    def __generate_update_text(self, aws_setting: AwsSetting, override_profile_name: str = None, preset: bool = False) -> str:
        profile_name = aws_setting.profile if override_profile_name is None else override_profile_name
        if aws_setting.mode_direct:
            text = update_format_direct.format(
                profile_name,
                aws_setting.aws_access_key_id,
                aws_setting.aws_secret_access_key,
                aws_setting.aws_session_token,
                aws_setting.region
            )
        elif preset:
            text = init_format.format(
                profile_name,
                aws_setting.aws_access_key_id_default,
                aws_setting.aws_secret_access_key_default
            )
        else:
            text = update_format.format(
                profile_name, aws_setting.aws_access_key_id, aws_setting.aws_secret_access_key, aws_setting.aws_session_token, aws_setting.region
            )
        return text

    def update_all_session_token(self) -> None:
        for key, aws_setting in self.settings.profiles.items():
            self.update_session_token(aws_setting)

    def update_session_token(self, aws_setting: AwsSetting) -> None:
        totp = pyotp.TOTP(aws_setting.mfa_secret_key)
        mfa_code = totp.now()

        print(mfa_code)

        cmd_get_mfa = "aws sts get-session-token --serial-number {serial} --profile {profile} --token-code {token} --region {region}".format(
            # cmd_get_mfa = "aws sts get-session-token --serial-number {serial} --token-code {token}".format(
            serial=aws_setting.serial,
            profile=aws_setting.profile,
            token=mfa_code,
            region=aws_setting.region
        )
        print(cmd_get_mfa)
        res = sp.run(cmd_get_mfa, shell=True, capture_output=True, text=True)
        print(res.stderr)
        if res.stdout == "":
            raise Exception("can't get token")
        key_sets = ast.literal_eval(res.stdout)

        aws_setting.set_session_info(key_sets)

        set_profile_time(aws_setting.profile)

        time.sleep(1)

    def load_cred_file(self):
        with open(self.settings.aws_credential_path, "r", encoding="utf-8") as f:
            data = f.read()
        data = data.replace("]", "")
        items = [group.split("\n") for group in data.split("[")]
        item: str
        for item in items:
            if len(item) < 4:
                continue
            skip = False
            info = {}
            profile_name = None
            for line in item:
                if line == "default":
                    skip = True
                    break
                if line == "":
                    continue
                values = line.split(" = ")
                if len(values) == 1:
                    profile_name = values[0]
                else:
                    key, value = values
                    if key == "":
                        pass
                    info[key] = value

            if skip:
                continue

            a_s = self.settings.profiles.get(profile_name)
            a_s = self.set_info(a_s, info)

    def set_info(self, a_s: AwsSetting, info: dict):
        if not "aws_session_token" in info.keys():
            a_s = self.set_info_direct(a_s, info)
            a_s.mode_direct = True
        else:
            a_s = self.set_info_as_mfa(a_s, info)
        return a_s

    def set_info_as_mfa(self, a_s: AwsSetting, info: dict):
        for key, value in info.items():
            if key == "aws_access_key_id":
                a_s.aws_access_key_id = value
            elif key == "aws_secret_access_key":
                a_s.aws_secret_access_key = value
            elif key == "aws_session_token":
                a_s.aws_session_token = value
        return a_s

    def set_info_direct(self, a_s: AwsSetting, info: dict):
        for key, value in info.items():
            if key == "aws_access_key_id":
                a_s.aws_access_key_id = value
            elif key == "aws_secret_access_key":
                a_s.aws_secret_access_key = value
        a_s.mode_direct = True
        return a_s

    def setup(self, replace_profile: str):
        self.backup_cred_file()
        self.load_cred_file()

        self.overwrite_session_info(
            default_profile=None, preset=True
        )

        if check_profile_expire(replace_profile):
            self.update_session_token(self.settings.profiles[replace_profile])

        self.overwrite_session_info(
            default_profile=replace_profile, preset=False
        )
