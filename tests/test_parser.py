# -*- coding: utf-8 -*-
# Python imports
import sys
PY_MAJOR_VERSION = sys.version_info[0]
import unittest

if PY_MAJOR_VERSION < 3:
    import robotparser
else:
    import urllib.robotparser as robotparser

# Project imports
import robotexclusionrulesparser


class TestStandardLibraryParserComparion(unittest.TestCase):
    """Verify that this parser agrees with the parser from the standard lib"""
    def setUp(self):
        self.parser = robotexclusionrulesparser.RobotFileParserLookalike()
        self.std_lib_parser = robotparser.RobotFileParser()

        s = """
        # robots.txt for http://www.example.com/

        User-agent: *
        Disallow:    /

        User-agent: foobot
        Disallow:

        """
        self.parser.parse(s)

        self.std_lib_parser.parse(s.split('\n'))

    def test_parsers_agree(self):
        """Verify that this parser agrees with the parser from the standard lib"""
        for user_agent, url in (("foobot", "/"), ("Foobot", "/bar.html"), ("SomeOtherBot", "/"),
                                ("SomeOtherBot", "/blahblahblah"), ):
            self.assertEqual(self.parser.can_fetch(user_agent, url),
                             self.std_lib_parser.can_fetch(user_agent, url))


class TestClassicSyntax(unittest.TestCase):
    """Exercise compliance with classic (MK1994/96) syntax"""
    def setUp(self):
        self.parser = robotexclusionrulesparser.RobotExclusionRulesParser()

        s = """
        # robots.txt for http://www.example.com/

        # In the classic syntax, * is treated literally, not as a wildcard.
        # A Webmaster might expect the line below to disallow everything, but
        # that's not how it works.
        User-agent: foobot
        Disallow: *

        User-agent: barbot
        Disallow: /private/*
        """
        self.parser.parse(s)

    def test_classic_syntax(self):
        """Exercise compliance with classic (MK1994/96) syntax"""
        # Note how results are completely opposite for the different syntaxes.
        self.assertTrue(self.parser.is_allowed("foobot", "/something.html",
                                               robotexclusionrulesparser.MK1996))
        self.assertFalse(self.parser.is_allowed("foobot", "/something.html",
                                                robotexclusionrulesparser.GYM2008))
        self.assertTrue(self.parser.is_allowed("barbot", "/private/xyz.html",
                                               robotexclusionrulesparser.MK1996))
        self.assertFalse(self.parser.is_allowed("barbot", "/private/xyz.html",
                                                robotexclusionrulesparser.GYM2008))


class TestGYM2008Syntax(unittest.TestCase):
    """Exercise compliance with the GYM2008 (Google-Yahoo-Microsoft 2008) syntax.

    It's described here:
    http://www.google.com/support/webmasters/bin/answer.py?answer=40367

    Announced here:
    http://googlewebmastercentral.blogspot.com/2008/06/improving-on-robots-exclusion-protocol.html
    http://ysearchblog.com/2008/06/03/one-standard-fits-all-robots-exclusion-protocol-for-yahoo-google-and-microsoft/
    http://blogs.msdn.com/webmaster/archive/2008/06/03/robots-exclusion-protocol-joining-together-to-provide-better-documentation.aspx
    mk1994 = the 1994 robots.txt draft spec (http://www.robotstxt.org/orig.html)
    mk1996 = the 1996 robots.txt draft spec (http://www.robotstxt.org/norobots-rfc.txt)
    """
    def setUp(self):
        self.parser = robotexclusionrulesparser.RobotExclusionRulesParser()

    def test_mk1994(self):
        """Test the parser with the example from MK1994"""
        robots_txt = """
# robots.txt for http://www.example.com/

User-agent: *
Disallow: /cyberworld/map/ # This is an infinite virtual URL space
Disallow: /tmp/ # these will soon disappear
Disallow: /foo.html
        """
        self.parser.parse(robots_txt)

        user_agent = "CrunchyFrogBot"

        self.assertTrue(self.parser.is_allowed(user_agent, "/"))
        self.assertFalse(self.parser.is_allowed(user_agent, "/foo.html"))
        self.assertTrue(self.parser.is_allowed(user_agent, "/foo.htm"))
        self.assertTrue(self.parser.is_allowed(user_agent, "/foo.shtml"))
        self.assertFalse(self.parser.is_allowed(user_agent, "/foo.htmlx"))
        self.assertTrue(self.parser.is_allowed(user_agent, "/cyberworld/index.html"))
        self.assertFalse(self.parser.is_allowed(user_agent, "/tmp/foo.html"))
        # Since it is the caller's responsibility to make sure the host name
        # matches, the parser disallows foo.html regardless of what I pass for
        # host name and protocol.
        self.assertFalse(self.parser.is_allowed(user_agent, "http://example.com/foo.html"))
        self.assertFalse(self.parser.is_allowed(user_agent, "http://www.example.com/foo.html"))
        self.assertFalse(self.parser.is_allowed(user_agent, "http://www.example.org/foo.html"))
        self.assertFalse(self.parser.is_allowed(user_agent, "https://www.example.org/foo.html"))
        self.assertFalse(self.parser.is_allowed(user_agent, "ftp://example.net/foo.html"))

    def test_mk1996_example_a(self):
        """Test the parser with example A from MK1996"""
        robots_txt = """
# robots.txt for http://www.example.com/

User-agent: 1bot
Allow: /tmp
Disallow: /

User-agent: 2bot
Allow: /tmp/
Disallow: /

User-agent: 3bot
Allow: /a%3cd.html
Disallow: /

User-agent: 4bot
Allow: /a%3Cd.html
Disallow: /

User-agent: 5bot
Allow: /a%2fb.html
Disallow: /

User-agent: 6bot
Allow: /a/b.html
Disallow: /

User-agent: 7bot
Allow: /%7ejoe/index.html
Disallow: /

User-agent: 8bot
Allow: /~joe/index.html
Disallow: /

        """
        self.parser.parse(robots_txt)

        self.assertTrue(self.parser.is_allowed("1bot", "/tmp"))
        self.assertTrue(self.parser.is_allowed("1bot", "/tmp.html"))
        self.assertTrue(self.parser.is_allowed("1bot", "/tmp/a.html"))
        self.assertFalse(self.parser.is_allowed("2bot", "/tmp"))
        self.assertTrue(self.parser.is_allowed("2bot", "/tmp/"))
        self.assertTrue(self.parser.is_allowed("2bot", "/tmp/a.html"))
        self.assertTrue(self.parser.is_allowed("3bot", "/a%3cd.html"))
        self.assertTrue(self.parser.is_allowed("3bot", "/a%3Cd.html"))
        self.assertTrue(self.parser.is_allowed("4bot", "/a%3cd.html"))
        self.assertTrue(self.parser.is_allowed("4bot", "/a%3Cd.html"))
        self.assertTrue(self.parser.is_allowed("5bot", "/a%2fb.html"))
        self.assertFalse(self.parser.is_allowed("5bot", "/a/b.html"))
        self.assertFalse(self.parser.is_allowed("6bot", "/a%2fb.html"))
        self.assertTrue(self.parser.is_allowed("6bot", "/a/b.html"))
        self.assertTrue(self.parser.is_allowed("7bot", "/~joe/index.html"))
        self.assertTrue(self.parser.is_allowed("8bot", "/%7Ejoe/index.html"))

    def test_mk1996_example_b(self):
        """Test the parser with example B from MK1996 with the domain changed to example.org"""
        robots_txt = """
# /robots.txt for http://www.example.org/
# comments to webmaster@example.org

User-agent: unhipbot
Disallow: /

User-agent: webcrawler
User-agent: excite
Disallow:

User-agent: *
Disallow: /org/plans.html
Allow: /org/
Allow: /serv
Allow: /~mak
Disallow: /

        """
        self.parser.parse(robots_txt)

        self.assertFalse(self.parser.is_allowed("unhipbot", "http://www.example.org/"))
        self.assertTrue(self.parser.is_allowed("webcrawler", "http://www.example.org/"))
        self.assertTrue(self.parser.is_allowed("excite", "http://www.example.org/"))
        self.assertFalse(self.parser.is_allowed("OtherBot", "http://www.example.org/"))
        self.assertFalse(self.parser.is_allowed("unhipbot", "http://www.example.org/index.html"))
        self.assertTrue(self.parser.is_allowed("webcrawler", "http://www.example.org/index.html"))
        self.assertTrue(self.parser.is_allowed("excite", "http://www.example.org/index.html"))
        self.assertFalse(self.parser.is_allowed("OtherBot", "http://www.example.org/index.html"))
        # The original document contains tests for robots.txt. I dropped them. I presume that no
        # one will fetch robots.txt to see if they're allowed to fetch robots.txt. Sheesh...
        #   assert(parser.is_allowed("unhipbot", "http://www.example.org/robots.txt") == True)
        #   assert(parser.is_allowed("webcrawler", "http://www.example.org/robots.txt") == True)
        #   assert(parser.is_allowed("excite", "http://www.example.org/robots.txt") == True)
        #   assert(parser.is_allowed("OtherBot", "http://www.example.org/robots.txt") == True)
        self.assertFalse(self.parser.is_allowed("unhipbot", "http://www.example.org/server.html"))
        self.assertTrue(self.parser.is_allowed("webcrawler", "http://www.example.org/server.html"))
        self.assertTrue(self.parser.is_allowed("excite", "http://www.example.org/server.html"))
        self.assertTrue(self.parser.is_allowed("OtherBot", "http://www.example.org/server.html"))
        self.assertFalse(self.parser.is_allowed("unhipbot",
                                                "http://www.example.org/services/fast.html"))
        self.assertTrue(self.parser.is_allowed("webcrawler",
                                               "http://www.example.org/services/fast.html"))
        self.assertTrue(self.parser.is_allowed("excite",
                                               "http://www.example.org/services/fast.html"))
        self.assertTrue(self.parser.is_allowed("OtherBot",
                                               "http://www.example.org/services/fast.html"))
        self.assertFalse(self.parser.is_allowed("unhipbot",
                                                "http://www.example.org/services/slow.html"))
        self.assertTrue(self.parser.is_allowed("webcrawler",
                                               "http://www.example.org/services/slow.html"))
        self.assertTrue(self.parser.is_allowed("excite",
                                               "http://www.example.org/services/slow.html"))
        self.assertTrue(self.parser.is_allowed("OtherBot",
                                               "http://www.example.org/services/slow.html"))
        self.assertFalse(self.parser.is_allowed("unhipbot",
                                                "http://www.example.org/orgo.gif"))
        self.assertTrue(self.parser.is_allowed("webcrawler",
                                               "http://www.example.org/orgo.gif"))
        self.assertTrue(self.parser.is_allowed("excite",
                                               "http://www.example.org/orgo.gif"))
        self.assertFalse(self.parser.is_allowed("OtherBot",
                                                "http://www.example.org/orgo.gif"))
        self.assertFalse(self.parser.is_allowed("unhipbot",
                                                "http://www.example.org/org/about.html"))
        self.assertTrue(self.parser.is_allowed("webcrawler",
                                               "http://www.example.org/org/about.html"))
        self.assertTrue(self.parser.is_allowed("excite",
                                               "http://www.example.org/org/about.html"))
        self.assertTrue(self.parser.is_allowed("OtherBot",
                                               "http://www.example.org/org/about.html"))
        self.assertFalse(self.parser.is_allowed("unhipbot",
                                                "http://www.example.org/org/plans.html"))
        self.assertTrue(self.parser.is_allowed("webcrawler",
                                               "http://www.example.org/org/plans.html"))
        self.assertTrue(self.parser.is_allowed("excite",
                                               "http://www.example.org/org/plans.html"))
        self.assertFalse(self.parser.is_allowed("OtherBot",
                                                "http://www.example.org/org/plans.html"))
        self.assertFalse(self.parser.is_allowed("unhipbot",
                                                "http://www.example.org/%7Ejim/jim.html"))
        self.assertTrue(self.parser.is_allowed("webcrawler",
                                               "http://www.example.org/%7Ejim/jim.html"))
        self.assertTrue(self.parser.is_allowed("excite",
                                               "http://www.example.org/%7Ejim/jim.html"))
        self.assertFalse(self.parser.is_allowed("OtherBot",
                                                "http://www.example.org/%7Ejim/jim.html"))
        self.assertFalse(self.parser.is_allowed("unhipbot",
                                                "http://www.example.org/%7Emak/mak.html"))
        self.assertTrue(self.parser.is_allowed("webcrawler",
                                               "http://www.example.org/%7Emak/mak.html"))
        self.assertTrue(self.parser.is_allowed("excite",
                                               "http://www.example.org/%7Emak/mak.html"))
        self.assertTrue(self.parser.is_allowed("OtherBot",
                                               "http://www.example.org/%7Emak/mak.html"))

    def test_blank_or_not_present(self):
        """Test behavior with a blank or non-existent robots.txt"""
        self.parser.parse('')

        self.assertTrue(self.parser.is_allowed("foobot", "/"))
        self.assertTrue(self.parser.is_allowed("anybot", "/foo.html"))
        self.assertTrue(self.parser.is_allowed("anybot", "/TheGoldenAgeOfBallooning/"))
        self.assertTrue(self.parser.is_allowed("anybot", "/TheGoldenAgeOfBallooning/claret.html"))

    def test_generosity(self):
        """See that the parser is forgiving"""
        utf8_byte_order_mark = chr(0xef) + chr(0xbb) + chr(0xbf)
        robots_txt = """%sUSERAGENT: FOOBOT
%suser-agent:%s%s%sbarbot%s
disallow: /foo/
        """ % (utf8_byte_order_mark, '\t', '\t', '\t', '\t', chr(0xb))
        self.parser.parse(robots_txt)

        self.assertTrue(self.parser.is_allowed("foobot", "/"))
        self.assertFalse(self.parser.is_allowed("foobot", "/foo/bar.html"))
        self.assertTrue(self.parser.is_allowed("AnotherBot", "/foo/bar.html"))
        self.assertFalse(self.parser.is_allowed("Foobot Version 1.0", "/foo/bar.html"))
        self.assertFalse(self.parser.is_allowed("Mozilla/5.0 (compatible; Foobot/2.1)",
                                                "/foo/bar.html"))
        self.assertFalse(self.parser.is_allowed("barbot", "/foo/bar.html"))
        self.assertTrue(self.parser.is_allowed("barbot", "/tmp/"))

    def test_non_ascii(self):
        """Test the parser's ability to handle non-ASCII"""
        robots_txt = """
# robots.txt for http://www.example.com/

UserAgent: Jävla-Foobot
Disallow: /

UserAgent: \u041b\u044c\u0432\u0456\u0432-bot
Disallow: /totalitarianism/

"""
        if PY_MAJOR_VERSION < 3:
            robots_txt = robots_txt.decode("utf-8")
        self.parser.parse(robots_txt)

        user_agent = "jävla-fanbot"
        if PY_MAJOR_VERSION < 3:
            user_agent = user_agent.decode("utf-8")
        self.assertTrue(self.parser.is_allowed(user_agent, "/foo/bar.html"))
        self.assertFalse(self.parser.is_allowed(user_agent.replace("fan", "foo"),
                                                "/foo/bar.html"))
        self.assertTrue(self.parser.is_allowed("foobot", "/"))
        user_agent = "Mozilla/5.0 (compatible; \u041b\u044c\u0432\u0456\u0432-bot/1.1)"
        self.assertTrue(self.parser.is_allowed(user_agent, "/"))
        self.assertFalse(self.parser.is_allowed(user_agent, "/totalitarianism/foo.htm"))

    def test_implicit_allow(self):
        """Test implicit allow rule"""
        robots_txt = """
# robots.txt for http://www.example.com/

User-agent: *
Disallow:    /

User-agent: foobot
Disallow:
"""
        self.parser.parse(robots_txt)

        self.assertTrue(self.parser.is_allowed("foobot", "/"))
        self.assertTrue(self.parser.is_allowed("foobot", "/bar.html"))
        self.assertFalse(self.parser.is_allowed("SomeOtherBot", "/"))
        self.assertFalse(self.parser.is_allowed("SomeOtherBot", "/blahblahblah"))

    def test_GYM2008_wildcards(self):
        """Test parsing of GYM2008 wildcard syntax"""
        robots_txt = """
# robots.txt for http://www.example.com/

User-agent: Rule1TestBot
Disallow:  /foo*

User-agent: Rule2TestBot
Disallow:  /foo*/bar.html

# Disallows anything containing the letter m!
User-agent: Rule3TestBot
Disallow:  *m

User-agent: Rule4TestBot
Allow:  /foo/bar.html
Disallow: *

User-agent: Rule5TestBot
Disallow:  /foo*/*bar.html

User-agent: Rule6TestBot
Allow:  /foo$
Disallow:  /foo
        """
        self.parser.parse(robots_txt)

        self.assertTrue(self.parser.is_allowed("Rule1TestBot", "/fo.html"))
        self.assertFalse(self.parser.is_allowed("Rule1TestBot", "/foo.html"))
        self.assertFalse(self.parser.is_allowed("Rule1TestBot", "/food"))
        self.assertFalse(self.parser.is_allowed("Rule1TestBot", "/foo/bar.html"))

        self.assertTrue(self.parser.is_allowed("Rule2TestBot", "/fo.html"))
        self.assertFalse(self.parser.is_allowed("Rule2TestBot", "/foo/bar.html"))
        self.assertFalse(self.parser.is_allowed("Rule2TestBot", "/food/bar.html"))
        self.assertFalse(self.parser.is_allowed("Rule2TestBot", "/foo/a/b/c/x/y/z/bar.html"))
        self.assertTrue(self.parser.is_allowed("Rule2TestBot", "/food/xyz.html"))

        self.assertFalse(self.parser.is_allowed("Rule3TestBot", "/foo.htm"))
        self.assertFalse(self.parser.is_allowed("Rule3TestBot", "/foo.html"))
        self.assertTrue(self.parser.is_allowed("Rule3TestBot", "/foo"))
        self.assertFalse(self.parser.is_allowed("Rule3TestBot", "/foom"))
        self.assertFalse(self.parser.is_allowed("Rule3TestBot", "/moo"))
        self.assertFalse(self.parser.is_allowed("Rule3TestBot", "/foo/bar.html"))
        self.assertTrue(self.parser.is_allowed("Rule3TestBot", "/foo/bar.txt"))

        self.assertFalse(self.parser.is_allowed("Rule4TestBot", "/fo.html"))
        self.assertFalse(self.parser.is_allowed("Rule4TestBot", "/foo.html"))
        self.assertFalse(self.parser.is_allowed("Rule4TestBot", "/foo"))
        self.assertTrue(self.parser.is_allowed("Rule4TestBot", "/foo/bar.html"))
        self.assertFalse(self.parser.is_allowed("Rule4TestBot", "/foo/bar.txt"))

        self.assertFalse(self.parser.is_allowed("Rule5TestBot", "/foo/bar.html"))
        self.assertFalse(self.parser.is_allowed("Rule5TestBot", "/food/rebar.html"))
        self.assertTrue(self.parser.is_allowed("Rule5TestBot", "/food/rebarf.html"))
        self.assertFalse(self.parser.is_allowed("Rule5TestBot", "/foo/a/b/c/rebar.html"))
        self.assertFalse(self.parser.is_allowed("Rule5TestBot", "/foo/a/b/c/bar.html"))

        self.assertTrue(self.parser.is_allowed("Rule6TestBot", "/foo"))
        self.assertFalse(self.parser.is_allowed("Rule6TestBot", "/foo/"))
        self.assertFalse(self.parser.is_allowed("Rule6TestBot", "/foo/bar.html"))
        self.assertFalse(self.parser.is_allowed("Rule6TestBot", "/fooey"))

    def test_GYM2008_crawl_delay_and_sitemap(self):
        """Test parsing of the GYM2008-specific directives crawl-delay and sitemap"""
        robots_txt = """
# robots.txt for http://www.example.com/

User-agent: Foobot
Disallow:  *
Crawl-Delay: 5

Sitemap: http://www.example.org/banana.xml

User-agent: Somebot
Allow: /foo.html
Crawl-Delay: .3
Allow: /bar.html
Disallow: *

User-agent: AnotherBot
Disallow:  *
Sitemap: http://www.example.net/sitemap.xml
Sitemap: http://www.example.com/another_sitemap.xml

User-agent: CamelBot
Disallow: /foo.html
Crawl-Delay: go away!
"""
        self.parser.parse(robots_txt)

        self.assertFalse(self.parser.is_allowed("Foobot", "/foo.html"))
        self.assertEqual(self.parser.get_crawl_delay("Foobot"), 5)
        self.assertIsNone(self.parser.get_crawl_delay("Blahbot"))
        self.assertTrue(self.parser.is_allowed("Somebot", "/foo.html"))
        self.assertTrue(self.parser.is_allowed("Somebot", "/bar.html"))
        self.assertFalse(self.parser.is_allowed("Somebot", "/x.html"))
        self.assertEqual(self.parser.get_crawl_delay("Somebot"), .3)
        self.assertFalse(self.parser.is_allowed("AnotherBot", "/foo.html"))
        self.assertEqual(self.parser.sitemaps[1], "http://www.example.net/sitemap.xml")
        self.assertIsNone(self.parser.get_crawl_delay("CamelBot"))

    def test_bad_syntax(self):
        """Test parsing of malformed robots.txt files"""
        robots_txt = """
# robots.txt for http://www.example.com/

# This is nonsense; UA most come first.
Disallow: /
User-agent: *

# With apologies to Dr. Seuss, this syntax won't act as the author expects.
# It will only match UA strings that contain "onebot twobot greenbot bluebot".
# To match multiple UAs to a single rule, use multiple "User-agent:" lines.
User-agent: onebot twobot greenbot bluebot
Disallow: /

# Blank lines indicate an end-of-record so the first UA listed here is ignored.
User-agent: OneTwoFiveThreeSirBot

# Note from Webmaster: add new user-agents below:
User-agent: WotBehindTheRabbitBot
User-agent: ItIsTheRabbitBot
Disallow: /HolyHandGrenade/
"""
        self.parser.parse(robots_txt)

        self.assertTrue(self.parser.is_allowed("onebot", "/"))
        self.assertTrue(self.parser.is_allowed("onebot", "/foo/bar.html"))
        self.assertTrue(self.parser.is_allowed("bluebot", "/"))
        self.assertTrue(self.parser.is_allowed("bluebot", "/foo/bar.html"))
        self.assertTrue(self.parser.is_allowed("OneTwoFiveThreeSirBot",
                                               "/HolyHandGrenade/Antioch.html"))
        self.assertFalse(self.parser.is_allowed("WotBehindTheRabbitBot",
                                                "/HolyHandGrenade/Antioch.html"))

    def test_case_insensitivity(self):
        """Test that user agents are not case sensitive"""
        robots_txt = """
# robots.txt for http://www.example.com/

User-agent: Foobot
Disallow: /
"""
        self.parser.parse(robots_txt)

        self.assertFalse(self.parser.is_allowed("Foobot", "/"))
        self.assertFalse(self.parser.is_allowed("FOOBOT", "/"))
        self.assertFalse(self.parser.is_allowed("FoOBoT", "/"))
        self.assertFalse(self.parser.is_allowed("foobot", "/"))
