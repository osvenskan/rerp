# Python modules
import distutils.core as duc

VERSION = file("VERSION").read().strip()

name = "robotexclusionrulesparser"
description = "An alternative to Python's robotparser module"
long_description = file("README").read().strip()
author = "Philip Semanchuk",
author_email = "philip@semanchuk.com",
maintainer = "Philip Semanchuk",
url = "http://nikitathespider.com/python/rerp/",
download_url = "http://nikitathespider.com/python/rerp/rerp-%s.tar.gz" % VERSION,
py_modules = ["robotexclusionrulesparser"]
# http://pypi.python.org/pypi?:action=list_classifiers
classifiers = [ 'Development Status :: 5 - Production/Stable', 
                'Intended Audience :: Developers', 
                'License :: OSI Approved :: Python Software Foundation License',
                'Operating System :: MacOS :: MacOS X',
                'Operating System :: POSIX', 
                'Operating System :: Unix', 
                'Environment :: Win32 (MS Windows)',
                'Programming Language :: Python', 
                'Topic :: Utilities' ]
license = "http://www.python.org/psf/license/"
keywords = "robots.txt robot parser"


duc.setup(name = name,
          version = VERSION,
          description = description,
          long_description = long_description,
          author = author,
          author_email = author_email,
          maintainer = maintainer,
          url = url,
          download_url = download_url,
          classifiers = classifiers,
          license = license,
          keywords = keywords,
          py_modules = py_modules
         )
