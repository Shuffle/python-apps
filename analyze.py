import yaml
import os

basedir = "."
dirs = os.listdir(basedir)
#print(dirs)
#basename = "testing"
for basename in dirs:
    if basename == ".gitignore" or basename == ".github" or basename == "README.md" or basename == ".git" or basename == "unsupported" or ".swp" in basename or ".swo" in basename:
        continue

    print(f"\n[DEBUG] Analyzing: {basename}")
    try:
        versions = os.listdir("./%s" % basename)
    except NotADirectoryError:
        continue

    for version in versions:
        filepath = "%s/%s/api.yaml" % (basename, version)

        try:
            with open(filepath, "r") as tmp:
                ret = yaml.load(tmp.read())

                newname = ret["name"].lower().replace(" ", "-", -1).replace(".", "-", -1)
                if newname != basename:
                    print("Bad name: %s vs %s" % (basename, newname))

                if ret["app_version"] != version:
                    print("Bad version (%s): %s vs %s" % (basename, version, ret["app_version"]))
                #else:
                #    print("%s:%s is valid" % (basename, version))
        except (NotADirectoryError, FileNotFoundError) as e:
            #print("Error inner file: %s" % e)
            pass

    try:
        subfolders = os.listdir(f"{basedir}/{basename}")
    except:
        continue

    for subfolder in subfolders:
        apifile = f"{basedir}/{basename}/{subfolder}/api.yaml"
        pythonfile = f"{basedir}/{basename}/{subfolder}/src/app.py"

        action_names = []
        try:
            with open(apifile, "r") as tmp:
                apidata = yaml.load(tmp.read())
                for item in apidata["actions"]:
                    action_names.append(item["name"])
        except NotADirectoryError as e:
            continue

        with open(pythonfile, "r") as tmp:
            pythondata = tmp.read()
            for action_name in action_names:
                if not action_name in pythondata:
                    print(f"===> Couldn't find action \"{action_name}\" from {apifile} in script {pythonfile}") 


    #break


#for item in 
