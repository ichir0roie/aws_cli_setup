from genericpath import exists
import profile
import shutil
import subprocess as sp
import os
import ast

import pyotp

from base.aws_setting import AwsSetting
from base.settings import Settings

from base.const import *

import time

import os


class CredentialsUpdator:
    def __init__(self):
        self.replace_profile = "default"  # XXX
        self.mode_replace = False
        self.settings: Settings = Settings(load_profile=True)
        self.text_all = None
        self.replace_region=None
        pass

    def __backup_credential(self):
        shutil.copy(self.settings.aws_credential_path, self.settings.aws_credential_path + "_bk")

    def __initialize_credential(self):
        all_text = ""
        for st in self.settings.aws_setting_list:
            all_text += init_format.format(st.profile, st.aws_access_key_id_default, st.aws_secret_access_key_default)
        with open(self.settings.aws_credential_path, "w", encoding="utf-8") as f:
            f.write(all_text)

    def generate_session_info_text(self) -> None:
        self.text_all = ""
        text_default = ""
        for aws_setting in self.settings.aws_setting_list:
            self.text_all += self.__generate_update_text(aws_setting)
            if self.settings.default_profile == aws_setting.profile:
                text_default = self.__generate_update_text(aws_setting, "default")
                # self.export_env(aws_setting)
        self.text_all = text_default + self.text_all

    def export_env(self, aws_setting: AwsSetting, os_type="win") -> str:
        format_cmds = [
            # "setx {key} {value}",
            # "set {key}={value}",
            "{key}={value}",
        ]
        if os_type != "win":
            format_cmd = ""
        cmds_keys = {
            "AWS_ACCESS_KEY_ID": aws_setting.aws_access_key_id,
            "AWS_SECRET_ACCESS_KEY": aws_setting.aws_secret_access_key,
            "AWS_DEFAULT_REGION": aws_setting.region,
            "AWS_SESSION_TOKEN": aws_setting.aws_session_token,
        }
        print(f"profile : {aws_setting.profile}")
        for fmt in format_cmds:
            for key, value in cmds_keys.items():
                cmd = fmt.format(
                    key=key,
                    value=value
                )
                print(cmd)
                # sp.run(
                #     cmd,
                #     shell=True, capture_output=True, text=True
                # )
                # os.environ[key]=value
        print()

    def __update_session_info(self):
        with open(self.settings.aws_credential_path, "w", encoding="utf-8") as f:
            f.write(self.text_all)

    def __generate_update_text(self, aws_setting: AwsSetting, override_profile_name: str = None) -> str:
        profile_name = aws_setting.profile if override_profile_name is None else override_profile_name
        if self.replace_region is not None:
            aws_setting.region=self.replace_region
        if aws_setting.mode_direct:
            text=update_format_direct.format()
        else:
            text= update_format.format(
            profile_name, aws_setting.aws_access_key_id, aws_setting.aws_secret_access_key, aws_setting.aws_session_token, aws_setting.region
        )
        return text

    def set_session_info(self):
        for aws_setting in self.settings.aws_setting_list:
            if aws_setting.mode_direct:
                continue
            self.__get_session_info(aws_setting)
            time.sleep(1)
        pass

    def __get_session_info(self, aws_setting: AwsSetting) -> None:
        totp = pyotp.TOTP(aws_setting.mfa_secret_key)
        mfa_code = totp.now()

        print(mfa_code)

        cmd_get_mfa = "aws sts get-session-token --serial-number {serial} --profile {profile} --token-code {token}".format(
            # cmd_get_mfa='aws sts get-session-token --serial-number {serial} --token-code {token}'.format(
            serial=aws_setting.serial,
            profile=aws_setting.profile,
            token=mfa_code,
        )
        print(cmd_get_mfa)
        res = sp.run(cmd_get_mfa, shell=True, capture_output=True, text=True)
        print(res.stderr)
        if res.stdout == "":
            raise Exception("can't get token")
        key_sets = ast.literal_eval(res.stdout)

        aws_setting.set_session_info(key_sets)

    def generate_windows_set_text(self):
        all_text = ""
        for stgs in self.settings.aws_setting_list:
            all_text += win_set_format.format(stgs.profile, stgs.aws_access_key_id, stgs.aws_secret_access_key, stgs.aws_session_token, stgs.region)
        os.makedirs("output/", exist_ok=True)
        with open("output/win_set.txt", "w", encoding="utf-8") as f:
            f.write(all_text)

    def load_credential_from_file(self):
        self.settings.aws_setting_list: list[AwsSetting] = []
        self.settings.default_profile = self.replace_profile
        with open(self.settings.aws_credential_path, "r", encoding="utf-8") as f:
            data = f.read()
        data = data.replace("]", "")
        items = [group.split("\n") for group in data.split("[")]
        item: str
        for item in items:
            if len(item) < 5:
                continue
            a_s = AwsSetting()
            skip = False
            info={}
            for line in item:
                if line == "default":
                    skip = True
                    break
                if line == "":
                    continue
                values = line.split(" = ")
                if len(values) == 1:
                    a_s.profile = values[0]
                else:
                    key, value = values
                    if key == "":
                        pass
                    info[key]=value
            
            self.set_info(a_s,info)
            
            if not skip:
                self.settings.aws_setting_list.append(a_s)


    def set_info(self,a_s:AwsSetting,info:dict):
        if "mode_direct"in info.keys():
            self.set_info_direct(a_s,info)
            a_s.mode_direct=True
        else :
            self.set_info_as_mfa(a_s,info)
            
    def set_info_as_mfa(self,a_s:AwsSetting,info:dict):
        for key,value in info.items():
            if key == "aws_access_key_id":
                a_s.aws_access_key_id = value
            elif key == "aws_secret_access_key":
                a_s.aws_secret_access_key = value
            elif key == "aws_session_token":
                a_s.aws_session_token = value
            elif key == "region":
                a_s.region = value  
                    
    def set_info_direct(self,a_s:AwsSetting,info:dict):
        for key,value in info.items():
            if key == "aws_access_key":
                a_s.aws_access_key_id = value
            elif key == "aws_secret_access_key":
                a_s.aws_secret_access_key = value
            elif key == "region":
                a_s.region = value
            
    def setup(self, replace_profile: str,region:str=None):
        self.replace_profile = replace_profile
        self.mode_replace = True if replace_profile != None else False
        self.replace_region=region
        self.settings: Settings = Settings(load_profile=not self.mode_replace)
        self.text_all = None

        self.__backup_credential()
        if self.mode_replace:
            self.load_credential_from_file()
        else:
            self.__initialize_credential()

            self.set_session_info()

        self.generate_session_info_text()
        self.__update_session_info()

        # self.generate_windows_set_text()

    def view(self):
        self.load_credential_from_file()
        for s in self.settings.aws_setting_list:
            self.export_env(s)
        pass

if __name__ == "__main__":
    # cu = CredentialsUpdator()
    # cu.set_session_info()
    # cu.generate_session_info_text()
    # print(cu.text_all)

    cu = CredentialsUpdator(replace_profile="main")

    cu.setup()
