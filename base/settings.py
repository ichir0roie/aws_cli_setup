from base.aws_setting import AwsSetting
import json
class Settings:
    aws_credential_path:str=None
    default_profile:str=None
    aws_setting_list:list[AwsSetting]=None
    
    def __init__(self,load_profile:bool=True) -> None:
        with open("settings.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        self.aws_credential_path=data["aws_credential_path"]
        profiles:dict=data["profiles"]
        self.aws_setting_list:list[AwsSetting]=[]
        
        if not load_profile:
            return
        
        self.default_profile=data["default_profile"]
        for key,value in profiles.items():
            aws_setting=AwsSetting()
            aws_setting.set_mfa_info(profile=key,info=value)
            self.aws_setting_list.append(aws_setting)
        
        pass