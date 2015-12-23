# Python imports
import unittest

# Project imports
import robotexclusionrulesparser


class TestSitemapDeprecation(unittest.TestCase):
    def setUp(self):
        self.parser = robotexclusionrulesparser.RobotExclusionRulesParser()

    def test_sitemap(self):
        """Ensure the 'sitemap' attribute is deprecated"""
        with self.assertRaises(DeprecationWarning):
            self.parser.sitemap
