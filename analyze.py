import yaml
import os

dirs = os.listdir(".")
#print(dirs)
#basename = "testing"
for basename in dirs:
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
#for item in 
