from base.credentials_updator import CredentialsUpdator
import os
import sys
dir=os.path.dirname(__file__)

sys.path.append(dir)

os.chdir(dir)


cu = CredentialsUpdator()

# env_args= os.environ.get("ARGS")

# if env_args:
#     values=env_args.split(",")
#     values.insert(0,sys.argv[0])
#     args=values
# else:
#     args=sys.argv
args=sys.argv
print(args)

if len(args) == 1:
    cu.setup(None)  # XXX
else:
    arg = args[1]
    if arg == "view":  # XXX
        cu.view()
    else:
        profile = args[1] if len(args) > 1 else None
        region=args[2] if len(args)>2 else None
        cu.setup(profile,region)
