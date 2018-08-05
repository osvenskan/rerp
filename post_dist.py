#!/usr/bin/env python

# Python imports
import time
import hashlib
import shutil
import os

RSS_TIMESTAMP_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"

with open("VERSION") as f:
    VERSION = f.read().strip()

# Make a copy of the tarball for posterity
tarball_name = "robotexclusionrulesparser-%s.tar.gz" % VERSION
shutil.copyfile(os.path.join("dist", tarball_name),
                os.path.join("releases", tarball_name))

tarball_name = "dist/robotexclusionrulesparser-%s.tar.gz" % VERSION
md5_name = "robotexclusionrulesparser-%s.md5.txt" % VERSION
sha1_name = "robotexclusionrulesparser-%s.sha1.txt" % VERSION

# Generate the tarball hashes
with open(tarball_name) as f:
    s = f.read()

md5 = hashlib.md5(s).hexdigest()
sha1 = hashlib.sha1(s).hexdigest()

with open(md5_name, "wb") as f:
    f.write(md5)
with open(sha1_name, "wb") as f:
    f.write(sha1)

print("md5  = " + md5)
print("sha1 = " + sha1)


# Print an RSS item suitable for pasting into rss.xml
timestamp = time.strftime(RSS_TIMESTAMP_FORMAT, time.gmtime())

print("""

        <item>
            <guid isPermaLink="false">%s</guid>
            <title>Robotexclusionrulesparser %s Released</title>
            <pubDate>%s</pubDate>
            <link>http://nikitathespider.com/python/rerp/</link>
            <description>Version %s of robotexclusionrulesparser has been released.
            </description>
        </item>

""" % (VERSION, VERSION, timestamp, VERSION))

print('hg tag rel' + VERSION)
