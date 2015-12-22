import time
import tarfile
import os
import os.path
import hashlib
import shutil

RSS_TIMESTAMP_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"

VERSION = open("VERSION").read().strip()

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

s = open("./" + tarball_name).read()

s = hashlib.md5(s).hexdigest()

print "md5 = " + s

open(md5_name, "w").write(s)


# Print an RSS item suitable for pasting into rss.xml
timestamp = time.strftime(RSS_TIMESTAMP_FORMAT, time.gmtime())

print """

		<item>
			<guid isPermaLink="false">%s</guid>
			<title>Robotexclusionrulesparser %s Released</title>
			<pubDate>%s</pubDate>
			<link>http://nikitathespider.com/python/rerp/</link>
			<description>Version %s of robotexclusionrulesparser has been released.
			</description>
		</item>

""" % (VERSION, VERSION, timestamp, VERSION)

