#!/usr/bin/env python

# Python imports
import time
import hashlib
import shutil
import os

RSS_TIMESTAMP_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"

VERSION = open("VERSION").read().strip()

# Make a copy of the tarball for posterity
tarball_name = "posix_ipc-%s.tar.gz" % VERSION
shutil.copyfile(os.path.join("dist", tarball_name),
                os.path.join("releases", tarball_name))

tarball_name = "dist/robotexclusionrulesparser-%s.tar.gz" % VERSION
md5_name = "robotexclusionrulesparser-%s.md5.txt" % VERSION
sha1_name = "robotexclusionrulesparser-%s.sha1.txt" % VERSION

# Generate the tarball hashes
s = open(tarball_name).read()

md5 = hashlib.md5(s).hexdigest()
sha1 = hashlib.sha1(s).hexdigest()

open(md5_name, "wb").write(md5)
open(sha1_name, "wb").write(sha1)

print "md5  = " + md5
print "sha1 = " + sha1


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

print 'hg tag rel' + VERSION
