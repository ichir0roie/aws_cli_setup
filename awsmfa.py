dir = "/".join(__file__.split("\\")[:-1])
import sys

sys.path.append(dir)
import os

os.chdir(dir)

from base.credentials_updator import CredentialsUpdator

profile = sys.argv[1] if len(sys.argv) > 1 else None

cu = CredentialsUpdator(profile)

cu.run()
