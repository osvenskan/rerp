import robotexclusionrulesparser as rerp

s = open("robots.txt", "rb").read()

s = s.decode("utf-8")

p = rerp.RobotExclusionRulesParser()

p.parse(s)



s = str(p)
print(s)
#print(s.encode('utf-8'))
#print str(p)



# p.fetch("http://en.wikipedia.org/robots.txt")

# print "Response code = %d" % p.response_code


# assert(p.is_allowed("Recall", "/") == False)


# p.user_agent = "Mozilla/5.0 (X11; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0"

# p.fetch("http://en.wikipedia.org/robots.txt")

# print "Response code = %d" % p.response_code

# assert(p.is_allowed("Recall", "/") == True)
