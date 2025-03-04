import os
with open(".cookie.env", "r") as inf:
	projectname = [o.strip("\n").split('=')[1] for o in inf if "projectname=" in o][0]

os.system("rm .cookie.s3inventory") # reset the inventory

for _ in open(".cookie_files.txt"):
	if len(_) > 1:
		cmd = f'''aws s3 cp {_} s3://{projectname} --storage-class DEEP_ARCHIVE'''
		print(cmd)
		os.system(cmd)