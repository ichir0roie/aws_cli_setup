from base.credentials_updator import CredentialsUpdator
import os
import sys
dir=os.path.dirname(__file__)

sys.path.append(dir)

os.chdir(dir)

from base.settings import Settings
s=Settings()



cmd=f"code {s.aws_credential_path}"

import subprocess

subprocess.run(
    cmd,shell=True
)