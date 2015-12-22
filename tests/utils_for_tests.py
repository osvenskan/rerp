# Python imports
import sys
import calendar
import socket
import os
import time
import threading
import datetime
from wsgiref.handlers import format_date_time as format_as_rfc1123

PY_MAJOR_VERSION = sys.version_info[0]
PY_MINOR_VERSION = sys.version_info[1]

if PY_MAJOR_VERSION < 3:
    from BaseHTTPServer import BaseHTTPRequestHandler
else:
    from http.server import BaseHTTPRequestHandler

# FIXME - resource warning due to this?   https://bugs.python.org/issue19524

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def find_unused_port():
    """Return an unused port. This code was written by Damon Kohler and it's under a PSF license.
    It's from here:
    http://code.activestate.com/recipes/531822-pick-unused-port/
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    addr, port = s.getsockname()
    s.close()
    return port


def format_as_rfc850(a_datetime):
    """Given a UTC datetime.datetime instance, return it formatted in RFC 850 format.

    e.g. - Sunday, 06-Nov-94 08:49:37 GMT
    """
    # I can't do this the obvious way -- using the formatters in strftime() -- because that returns
    # locale-aware weekday and month names, and the HTTP spec requires English-only names.
    RFC850_FORMAT = "{}, {:02}-{}-{:02} {:02}:{:02}:{:02} GMT"

    weekday = WEEKDAYS[a_datetime.weekday()]
    month = MONTHS[a_datetime.month - 1]
    # Years are only 2 digits in RFC 850.
    year = int(str(a_datetime.year)[2:])

    return RFC850_FORMAT.format(weekday, a_datetime.day, month, year, a_datetime.hour,
                                a_datetime.minute, a_datetime.second)


def format_as_asctime(a_datetime):
    """Given a UTC datetime.datetime instance, return it formatted in C's asctime() format.

    e.g. - Sun Nov  6 08:49:37 1994
    """
    # Per Python's documentation, "Locale information is not used by asctime()" which saves me
    # some work.
    return time.asctime(a_datetime.timetuple())


class UTCTimezone(datetime.tzinfo):
    """The UTC timezone, because Python 2 doesn't provide one. Replaced by datetime.timezone.utc
    in Python 3.
    """
    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def dst(self, dt):
        return datetime.timedelta(0)


def get_utc_timezone():
    """Return appropriate UTC timezone based on Python version"""
    return UTCTimezone() if (PY_MAJOR_VERSION < 3) else datetime.timezone.utc


class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    """Handler for HTTP requests from the test code.

    If you are new to Python and tempted to use this code to handle requests from the public
    Internet, stop! It's fine for internal-use test code but full of assumptions that would
    break and/or be dangerous on the public Internet.
    """
    def do_GET(self):
        """Handle GET requests that start with one of the path prefixes that I expect."""
        if self.path.startswith('/encoding/'):
            self._handle_encoding_request()
        elif self.path.startswith('/response_code/'):
            self._handle_response_code_request()
        elif self.path.startswith('/sleep/'):
            self._handle_sleep_request()
        elif self.path.startswith('/expires/'):
            self._handle_expires_request()
        elif self.path.startswith('/die_die_die/'):
            # It's time to quit. This uses code from here:
            # http://stackoverflow.com/questions/10085996/shutdown-socketserver-serve-forver-in-one-thread-python-application/22533929#22533929
            kill_server = lambda server: server.shutdown()

            kill_thread = threading.Thread(target=kill_server, args=(self.server,))
            kill_thread.start()
            self.send_response(200)
            self.end_headers()

    def log_request(self, code='-', size='-'):
        """Override base class log_request() to silence chatter to console"""
        pass

    def _handle_encoding_request(self):
        """Return robots.txt content in a specific encoding.

        The path must be something like '/encoding/utf-8/robots.txt' where the encoding can vary.
        """
        path_elements = self.path.split('/')
        encoding = path_elements[2]

        # Read content from standard data file which is encoded as utf-8.
        filename = os.path.join(os.path.dirname(__file__), 'robots.txt')
        with open(filename) as f:
            content = f.read().decode('utf-8')

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset={}'.format(encoding))
        self.end_headers()
        self.wfile.write(content)

    def _handle_response_code_request(self):
        """Respond with a specific response code (e.g. 200, 404, etc.)

        The path must be something like '/response_code/777/robots.txt' where the code can vary.
        """
        path_elements = self.path.split('/')
        response_code = int(path_elements[2])
        self.send_response(response_code)
        self.end_headers()

    def _handle_sleep_request(self):
        """Sleep (wait) for a specific amount of time before responding with 200.

        The path must be something like '/sleep/2/robots.txt' where the sleep time can vary. The
        sleep time can be a float.
        """
        path_elements = self.path.split('/')
        sleep_time = float(path_elements[2])
        time.sleep(sleep_time)
        self.send_response(200)
        self.end_headers()

    def _handle_expires_request(self):
        """Respond with 200 and includes an Expires header.

        The Expires header will use the date and format encoded in the path. The path must be
        something like '/expires/2015-12-15-01-01-01/rfc1123/robots.txt' where the timestamp and
        format can vary.

        The timestamp is in ISO order but delimited with '-' to make it URL-friendly.

        The format can be one of the 3 specified in the HTTP 1.1 spec: 'rfc1123', 'rfc850', or
        'asctime'.
        """
        path_elements = self.path.split('/')
        # expiration_date is in ISO format ordering, but with all elements delimited by dashes.
        expiration_date = path_elements[2]
        rfc_format = path_elements[3]
        expiration_date = datetime.datetime.strptime(expiration_date, '%Y-%m-%d-%H-%M-%S')

        # Make it a UTC time.
        expiration_date = expiration_date.replace(tzinfo=get_utc_timezone())

        if rfc_format == 'rfc1123':
            expiration_date = format_as_rfc1123(calendar.timegm(expiration_date.timetuple()))
        elif rfc_format == 'rfc850':
            expiration_date = format_as_rfc850(expiration_date)
        elif rfc_format == 'asctime':
            expiration_date = format_as_asctime(expiration_date)

        self.send_response(200)
        self.send_header('Expires', expiration_date)
        self.end_headers()
