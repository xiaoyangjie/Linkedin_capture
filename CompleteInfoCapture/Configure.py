# coding=utf-8


################mongodb数据库#################################

MONGOHOST = "mongodb://mongo:123456@121.49.99.14"

ACCOUNT = {'mongo': MONGOHOST, 'db' : 'Linkedin', 'col' : 'LinkedinAccount', 'name' : 'account'}

LINKEDINURL = {'mongo': MONGOHOST, 'db' : 'Linkedin', 'col' : 'urlNew', 'name' : 'linkedinUrl'}

LINKEDINUSERS = {'mongo': MONGOHOST, 'db' : 'Linkedin', 'col' : 'usersNew', 'name' : 'linkedinUsers'}

LINKEDINPOSTSURL = {'mongo': MONGOHOST, 'db' : 'Linkedin', 'col' : 'PostsUrl', 'name' : 'linkedinPostsUrl'}

##################redis数据库#############################

REDISURL = {'redisHost': '121.49.99.14','port':6000,'password':'yj123456', 'key' : 'linkedinUrlName'}

#########################################################

PRECESSNUM = 3

URLLIMIT = 1000