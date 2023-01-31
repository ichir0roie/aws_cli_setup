from base.credentials_updator import CredentialsUpdator
import os
import sys
dir=os.path.dirname(__file__)

sys.path.append(dir)

os.chdir(dir)


cu = CredentialsUpdator()
if len(sys.argv) == 1:
    cu.setup(None)  # XXX
else:
    arg = sys.argv[1]
    if arg == "view":  # XXX
        cu.view()
    else:
        profile = sys.argv[1] if len(sys.argv) > 1 else None
        cu.setup(profile)
