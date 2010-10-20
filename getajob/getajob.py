#!/usr/bin/env python
# encoding: utf-8
"""
getajob.py

Created by FI$H 2000 on 2010-10-20.
Copyright (c) 2010 OST, LLC. All rights reserved.

Uses the AuthenticJobs API (c) 2010 AuthenticJobs.
All rights reserved, used with permission.
Get your own AuthenticJobs API key here:

	http://www.authenticjobs.com/api/


FYI: 
>>> jobtypes.get('types')                                                                                                                                                           
{u'type': [{u'id': u'1', u'name': u'Full-time'}, {u'id': u'2', u'name': u'Freelance'}, {u'id': u'3', u'name': u'Contract'}]}


"""

import sys, os, re, getopt, urllib2, demjson, subprocess
from django.utils.html import strip_tags, strip_entities

help_message = '''
You are doing it wrong.
'''


class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg


def main(argv=None):
	
	apiroot = "http://www.authenticjobs.com/api/"
	apikey = "NO NO NO"
	urltpl = "%s?api_key=%s&method=aj.jobs.search&keywords=%s&perpage=100&format=json"
	locurltpl = "%s?api_key=%s&method=aj.jobs.getlocations&perpage=100&format=json"
	
	verbose = False
	placefilter = lambda: True
	placefiltering = False
	places = []
	dfilter = None
	ringer = 'Derek Jeter'
	jobtype = 0
	urlview = False
	
	if argv is None:
		argv = sys.argv
	try:
		try:
			opts, args = getopt.getopt(argv, "hvc:s:n:f:a:k:FLCu", [
				"help", "verbose",
				"city=", "state=", "country=", "find=", "findall=",
				"apikey=",
				"full-time", "fulltime", "free-lance", "freelance", "contract",
				"urlview"
			])
		except getopt.error, msg:
			raise Usage(msg)
		for option, value in opts:
			if option in ("-h", "--help"):
				raise Usage(help_message)
			if option in ("-v", "--verbose"):
				verbose = True
			if option in ("-c", "--city"):
				placefilter = lambda p: value == p.get('city', ringer).lower()
				placefiltering = True
			if option in ("-s", "--state"):
				#placefilter = lambda p: value == p.get('state', ringer).lower()
				#placefiltering = True
				places = [str(value).lower()]
			if option in ("-C", "--country"):
				placefilter = lambda p: value == p.get('country', ringer).lower()
				placefiltering = True
			if option in ("-f", "--find"):
				dfilter = re.compile(str(value), re.IGNORECASE)
				placefilter = lambda p: reduce(lambda a,b: a or bool(dfilter.findall(b)), p.values(), False)
				placefiltering = True
			if option in ("-a", "--findall"): # same for now
				dfilter = re.compile(str(value), re.IGNORECASE)
				placefilter = lambda p: reduce(lambda a,b: a or bool(dfilter.findall(b)), p.values(), False)
				placefiltering = True
			if option in ("-k", "--apikey"):
				apikey = str(value)
			
			if option in ("-F", "--full-time", "--fulltime"):
				jobtype = 1
			elif option in ("-L", "--free-lance", "--freelance"):
				jobtype = 2
			elif option in ("-C", "--contract"):
				jobtype = 3
			
			if option in ("-u", "--urlview"):
				urlview = True
			
			
		
		if placefiltering:
			locurl = locurltpl % (
				apiroot, apikey
			)
			try:
				locs_out = urllib2.urlopen(locurl)
				locs_txt = locs_out.read()
				#locs_meta = locs_out.info()
				locs_out.close()
			except urllib2.URLError, urlerr:
				print "===\t URL FAIL: Couldn't open endpoint %s" % str(urlerr)
				return 2
			
			try:
				locs = demjson.decode(locs_txt)
			except demjson.JSONDecodeError, valerr:
				print "===\t JSON FAIL: JSON Decode Error %s\n" % valerr
				return 2
			
			if not locs.get('stat') == 'ok':
				print "===\t API FAIL: API status returned %s\n" % jobs_respdata.get('stat')
				return 2
			
			#cities = [c for c in locs.get('locations').get('location') if c.get('city')]
			places = map(lambda c: c.get('id'),
				filter(placefilter,
					[c for c in locs.get('locations').get('location')]
				)
			)
		
		
		keywords = ",".join(args)
		
		if places:
			keywords += "&location=%s" % ','.join(places)
		if jobtype:
			keywords += "&type=%s" % jobtype
		
		url = urltpl % (
			apiroot, apikey, keywords
		)
		
		try:
			jobs_respout = urllib2.urlopen(url)
			jobs_resptxt = jobs_respout.read()
			#jobs_respmeta = jobs_respout.info()
			jobs_respout.close()
		except urllib2.URLError, urlerr:
			print "===\t URL FAIL: Couldn't open endpoint %s" % str(urlerr)
			return 2
		
		try:
			jobs_respdata = demjson.decode(jobs_resptxt)
		except demjson.JSONDecodeError, valerr:
			print "===\t JSON FAIL: JSON Decode Error %s\n" % valerr
			return 2
		
		if not jobs_respdata.get('stat') == "ok":
			print "===\t API FAIL: API status returned %s\n" % jobs_respdata.get('stat')
			return 2
		
		"""
		print "PLACES:"
		print places
		print ""
		
		print "KEYWORDS:"
		print keywords
		print ""
		
		print "URL:"
		print url
		print ""
		"""
		
		if jobs_respdata:
			if not urlview:
				for job in jobs_respdata.get('listings').get('listing'):
					print "--------------------------------------------------------------------------------------------------------------------"
					print "%s -- %s -- %s" % (job['title'].upper(), job['company']['name'], job['company']['url'])
					print strip_entities(strip_tags(job['description']))[0:100] + " ..."
					#print job.keys()
					print ""
			else:
				urlout = ""
				for job in jobs_respdata.get('listings').get('listing'):
					urlout += "%s -- %s -- %s \n" % (job['title'].upper(), job['company']['name'], job['company']['url'])
					#urlout += "%s \n" % job['description']
				"""
				pp = subprocess.Popen("/opt/local/bin/urlview", env=dict(
					BROWSER="/usr/bin/open -a /Applications/Safari.app %%s"
				))
				"""
				os.system("echo '%s' | BROWSER='/usr/bin/open -a /Applications/Safari.app %%s' /opt/local/bin/urlview" % urlout.encode('utf-8', 'ignore'))
				
		
		
	except Usage, err:
		print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		print >> sys.stderr, "\t for help use --help"
		return 2


if __name__ == "__main__":
	sys.exit(main(sys.argv[1:]))
