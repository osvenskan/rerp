# -*- coding: utf-8 -*-
# Python imports
import sys
import socket
import unittest
import os
import time
import threading
import datetime
import calendar

PY_MAJOR_VERSION = sys.version_info[0]
PY_MINOR_VERSION = sys.version_info[1]

if PY_MAJOR_VERSION < 3:
    import urllib2 as urllib_error
    import urllib2 as urllib_request
    import SocketServer as socketserver
else:
    import urllib.error as urllib_error
    import urllib.request as urllib_request
    import socketserver

# Project imports
import robotexclusionrulesparser
# I add this file's directory to sys.path so that I can find my utils module.
sys.path.insert(0, os.path.dirname(__file__))
import utils_for_tests

# These three variables have to be global so they can be shared by setUpModule(), tearDownModule(),
# and MyHTTPRequestHandler.
http_server_thread = None
PORT = None
HOST_NAME = 'http://localhost:{}'

def setUpModule():
    """Start the HTTP server in another thread"""
    global http_server_thread
    global PORT
    global HOST_NAME

    PORT = utils_for_tests.find_unused_port()
    HOST_NAME = HOST_NAME.format(PORT)

    def run_http_server():
        httpd = socketserver.TCPServer(("", PORT), utils_for_tests.MyHTTPRequestHandler)
        httpd.serve_forever()

    http_server_thread = threading.Thread(target=run_http_server)
    http_server_thread.start()
    # Give time for the new thread to start. If I don't pause here, on some systems the fetch tests
    # begin before this thread has started resulting in spurious fetch failures. It would be
    # better for the threads to share a lock or semaphore to guarantee synchronization. This is the
    # poor man's way of fixing the problem.
    time.sleep(0.5)


def tearDownModule():
    """Tell the HTTP server to shut down and wait for the thread to exit."""
    req = urllib_request.Request(HOST_NAME + "/die_die_die/")
    urllib_request.urlopen(req)

    http_server_thread.join()


class TestFetchFailures(unittest.TestCase):
    """Exercise fetch()'s response in the face of adversity."""
    def setUp(self):
        self.parser = robotexclusionrulesparser.RobotExclusionRulesParser()

    def test_fetch_non_existent_domain(self):
        """Test handling of non-existent domain"""
        url = 'http://ThisDomainIsGuaranteedNotToExistPerRfc2606.invalid'

        with self.assertRaises(urllib_error.URLError):
            self.parser.fetch(url)

    def test_401_handling(self):
        """Test handling of response code 401 (Unauthorized) - everything disallowed"""
        self.parser.fetch(HOST_NAME + "/response_code/{}/robots.txt".format(401))

        self.assertFalse(self.parser.is_allowed("NigelBot", "/"))
        self.assertFalse(self.parser.is_allowed("StigBot", "/foo/bar.html"))
        self.assertFalse(self.parser.is_allowed("BruceBruceBruceBot", "/index.html"))

    def test_403_handling(self):
        """Test handling of response code 403 (Forbidden) - everything disallowed"""
        self.parser.fetch(HOST_NAME + "/response_code/{}/robots.txt".format(403))

        self.assertFalse(self.parser.is_allowed("NigelBot", "/"))
        self.assertFalse(self.parser.is_allowed("StigBot", "/foo/bar.html"))
        self.assertFalse(self.parser.is_allowed("BruceBruceBruceBot", "/index.html"))

    def test_404_handling(self):
        """Test handling of response code 404 (Not Found) - everything allowed"""
        self.parser.fetch(HOST_NAME + "/response_code/{}/robots.txt".format(404))

        self.assertTrue(self.parser.is_allowed("foobot", "/"))
        self.assertTrue(self.parser.is_allowed("javla-foobot", "/stuff"))
        self.assertTrue(self.parser.is_allowed("anybot", "/TotallySecretStuff"))

    def test_other_code_handling(self):
        """Test handling of response other codes, e.g. 500 (Server Error)"""
        for response_code in (409, 410, 500, 501, 502, 503, 504):
            url = HOST_NAME + "/response_code/{}/robots.txt"
            with self.assertRaises(urllib_error.URLError):
                self.parser.fetch(url.format(response_code))


class TestExpiration(unittest.TestCase):
    """Test the parser's expiration features.

    Per MK1996 §3.4, the default expiration is seven days.
    """
    def setUp(self):
        self.parser = robotexclusionrulesparser.RobotExclusionRulesParser()
        # I force the parser to use UTC to keep things simple.
        self.parser.use_local_time = False

    def _get_expires(self):
        """Returns now + 90 minutes in a 2-tuple of (datetime instance, url-friendly string)."""
        expires = datetime.datetime.utcnow() + datetime.timedelta(minutes=90)
        expires_url = expires.strftime('%Y-%m-%d-%H-%M-%S')
        expires_url = expires_url.replace(' ', '-')
        expires_url = expires_url.replace(':', '-')

        return (expires, expires_url)

    def test_default_in_local_time(self):
        """Test default expiration date in local time"""
        self.parser.use_local_time = True
        localtime = time.mktime(time.localtime())
        self.assertTrue((self.parser.expiration_date >
                         localtime + robotexclusionrulesparser.SEVEN_DAYS - 60))
        self.assertTrue((self.parser.expiration_date <
                         localtime + robotexclusionrulesparser.SEVEN_DAYS + 60))

    def test_default_in_utc_time(self):
        """Test default expiration date in UTC"""
        utc = calendar.timegm(time.gmtime())
        self.assertTrue((self.parser.expiration_date >
                         utc + robotexclusionrulesparser.SEVEN_DAYS - 60))
        self.assertTrue((self.parser.expiration_date <
                         utc + robotexclusionrulesparser.SEVEN_DAYS + 60))

    def test_rfc1123_expires_header(self):
        """Test parser's ability to handle expires headers in RFC 1123 (standard) format

        ref: http://www.w3.org/Protocols/rfc2616/rfc2616-sec3.html#sec3.3.1
        """
        # Set an Expires header for 90 minutes from now.
        expires, expires_url = self._get_expires()

        url = HOST_NAME + "/expires/{}/rfc1123/robots.txt".format(expires_url)
        self.parser.fetch(url)

        expiration_date = datetime.datetime.fromtimestamp(self.parser.expiration_date,
                                                          utils_for_tests.get_utc_timezone())

        # Before comparing these timestamps, I null out elements that I don't want to compare.
        expires = expires.replace(microsecond=0)
        expiration_date = expiration_date.replace(tzinfo=None)
        self.assertEqual(expiration_date, expires)

    def test_rfc850_expires_header(self):
        """Test parser's ability to handle expires headers in RFC 850 format

        RFC 850 format is rarely used but support is required by the HTTP 1.1 spec.
        ref: http://www.w3.org/Protocols/rfc2616/rfc2616-sec3.html#sec3.3.1
        """
        # Set an Expires header for 90 minutes from now.
        expires, expires_url = self._get_expires()

        url = HOST_NAME + "/expires/{}/rfc850/robots.txt".format(expires_url)
        self.parser.fetch(url)

        expiration_date = datetime.datetime.fromtimestamp(self.parser.expiration_date,
                                                          utils_for_tests.get_utc_timezone())

        # Before comparing these timestamps, I null out elements that I don't want to compare.
        expires = expires.replace(microsecond=0)
        expiration_date = expiration_date.replace(tzinfo=None)
        self.assertEqual(expiration_date, expires)

    def test_asctime_expires_header(self):
        """Test parser's ability to handle expires headers in asctime format

        asctime format is rarely used but support is required by the HTTP 1.1 spec.
        ref: http://www.w3.org/Protocols/rfc2616/rfc2616-sec3.html#sec3.3.1
        """
        # Set an Expires header for 90 minutes from now.
        expires, expires_url = self._get_expires()

        url = HOST_NAME + "/expires/{}/asctime/robots.txt".format(expires_url)

        self.parser.fetch(url)

        expiration_date = datetime.datetime.fromtimestamp(self.parser.expiration_date,
                                                          utils_for_tests.get_utc_timezone())

        # Before comparing these timestamps, I null out elements that I don't want to compare.
        expires = expires.replace(microsecond=0)
        expiration_date = expiration_date.replace(tzinfo=None)
        self.assertEqual(expiration_date, expires)


@unittest.skipIf(((PY_MAJOR_VERSION <= 2) and (PY_MINOR_VERSION <= 5)),
                 'urlopen() timeout param not supported in this Python version')
class TestTimeout(unittest.TestCase):
    """Exercise the timeout feature of fetch() which is supported in Python >= 2.6"""
    def setUp(self):
        self.parser = robotexclusionrulesparser.RobotExclusionRulesParser()

    @unittest.skip('Skipping due to server failure')
    # The code being tested here works fine, but the test still raises an error. Python's
    # HTTP server raises a socket error when the client code (in this case, self.parser) closes
    # the socket before the connection is complete.
    # The error is raised on the following systems:
    # Linux Mint 17 x64, Python 2.7 and Python 3.2
    # Windows 7 x64, Python 2.7
    # OSX, Python 2.7
    # The error is NOT raised on the following systems:
    # Windows 7 x64, Python 3.5
    # OSX, Python 3.4
    def test_fetch_expiring_timeout(self):
        """Exercise fetch when the timeout expires"""
        url = HOST_NAME + "/sleep/1/robots.txt"

        expected_exception = urllib_error.URLError if (PY_MAJOR_VERSION < 3) else socket.timeout

        with self.assertRaises(expected_exception):
            self.parser.fetch(url, 0.5)

    def test_fetch_non_expiring_timeout(self):
        """Exercise fetch when the timeout does not expire"""
        url = HOST_NAME + "/sleep/0.5/robots.txt"

        # No exception should be raised.
        self.parser.fetch(url, 2)
