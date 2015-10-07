import robotexclusionrulesparser

rerp = robotexclusionrulesparser.RobotExclusionRulesParser()
#rerp = robotexclusionrulesparser.ClassicRobotExclusionRulesParser()


s = """
User-agent: *
Disallow: /*x$
"""
rerp.parse(s)
print rerp

assert(rerp.is_allowed("CrunchyFrogBot", "/foop/bark.htmlx") == True)

