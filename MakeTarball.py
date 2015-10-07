import tarfile
import os
import os.path
import hashlib
import shutil

VERSION = file("VERSION").read().strip()

shutil.copyfile("robotexclusionrulesparser.py", "robotexclusionrulesparser-%s.py" % VERSION) 

filenames = (
    "LICENSE",
    "INSTALL",
    "README",
    "VERSION",
    "ReadMe.html",
    "setup.py",
    "robotexclusionrulesparser.py",
    "parser_test.py",
)


tarball_name = "robotexclusionrulesparser-%s.tar.gz" % VERSION
md5_name = "robotexclusionrulesparser-%s.md5.txt" % VERSION

if os.path.exists(tarball_name):
    os.remove(tarball_name)

SourceDir = "./"
BundleDir = "robotexclusionrulesparser-%s/" % VERSION

tarball = tarfile.open("./" + tarball_name, "w:gz")
for name in filenames:
    SourceName = SourceDir + name
    BundledName = BundleDir + name

    print "Adding " + SourceName

    tarball.add(SourceName, BundledName, False)
tarball.close()

s = file("./" + tarball_name).read()

s = hashlib.md5(s).hexdigest()

print "md5 = " + s

file(md5_name, "w").write(s)



