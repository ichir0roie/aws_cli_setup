class AwsSetting:
    mode_direct=False
    profile = ""
    serial = ""
    mfa_secret_key =""
    aws_access_key_id = ""
    aws_secret_access_key = ""
    aws_session_token = ""
    region = ""

    aws_access_key_id_default = ""
    aws_secret_access_key_default = ""

    def __init__(self) -> None:
        pass

    def set_mfa_info(self, profile: str, info: dict):
        self.profile = profile
        self.serial = info.get("serial")
        self.region = info["region"]
        self.mfa_secret_key = info.get("mfa_secret_key")
        
        self.aws_access_key_id_default = info.get("aws_access_key_id_default")
        self.aws_secret_access_key_default = info.get("aws_secret_access_key_default")
        
        if "mode_direct" in info.keys():
            self.mode_direct=True
            self.aws_access_key_id=info.get("aws_access_key_id")
            self.aws_secret_access_key=info.get("aws_secret_access_key")

    def set_session_info(self, info: dict):
        credentials = info["Credentials"]
        self.aws_access_key_id = credentials["AccessKeyId"]
        self.aws_secret_access_key = credentials["SecretAccessKey"]
        self.aws_session_token = credentials["SessionToken"]
