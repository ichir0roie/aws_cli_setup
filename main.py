from base.credentials_updator_2 import CredentialsUpdator
import os
import sys
dir = os.path.dirname(__file__)

sys.path.append(dir)

os.chdir(dir)


cu = CredentialsUpdator()

args = sys.argv
print(args)

profile = args[1] if len(args) > 1 else None
reload = True if len(args) > 2 else False
cu.setup(profile, reload)
