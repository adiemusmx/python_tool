#coding=utf-8
import urllib
import re
import os
import sys

def getHtml(url):
	page = urllib.urlopen(url)
	html = page.read()
	return html

def getCurrentJobs(html, keyword):
	jobre = re.compile(r'view/Git-DL/job/' + keyword + '/([0123456789]+)')
	jobsList = re.findall(jobre, html)
	return list(set(jobsList))

def downloadHtml(jobs, keyword):
	print "Detecting jobs : "
	print jobs 
	for i in jobs:
		html = getHtml("http://10.20.0.18:8081/view/Git-DL/job/" + keyword + "/" + i + "/consoleText")
		end = html.strip('\n')[-7:]
		if end != "SUCCESS" and end != "FAILURE" and end != "ABORTED":
			continue
		filename = keyword + "/" + keyword + "_" + i + "_(" + end  + ").txt"
		if os.path.exists(filename):
			continue
		print "downloading job[" + i + "]"
		
		file = open(filename, "wb")
		file.write(html)
		file.close

def getBuildInfo(filename, keyword):
	oneLine = ''
	results = []
	file = open(filename, 'r')
	lines = file.readlines()
	file.close
	
	repoRe = re.compile(r'--progress (.+).git')
	branchRe = re.compile(r'\((.+)\)')
	revRe = re.compile(r'Checking out Revision (.+) \(')
	
	for line in lines:
		line = line.strip('\n')
		if re.findall(repoRe, line):
			oneLine = oneLine + re.findall(repoRe, line)[0] + ".git,"
		elif re.findall(revRe, line):
			oneLine = oneLine + re.findall(branchRe, line)[0] + "," + re.findall(revRe, line)[0] + "\n"
			results.append(oneLine)
			oneLine = ''
		elif line.startswith('Updating '):
			results.append('navicore-lib_BJ,' + line[9:] + '\n')
		elif line.startswith('Switching to '):
			results.append('navicore-lib_BJ,' + line[13:] + '\n')
		elif line.startswith('[' + keyword + ']'):
			break
			
	return results

def saveCSV(filename, results):
	
	if not os.path.exists(filename):
		print "Converting " + filename
		file = open(filename, "wb")
		for line in results:
			file.write(line)
		file.close
	
def analysis(keyword):
	url = "http://10.20.0.18:8081/view/Git-DL/job/" + keyword + "/"
	print "-------------------------------------"
	print url
	html = getHtml(url)
	jobs = getCurrentJobs(html, keyword)

	if not os.path.exists(keyword):
		os.makedirs(keyword)
		
	downloadHtml(jobs, keyword)

	for i in jobs:
		if os.path.exists(keyword + "/" + keyword + "_" + i + "_(SUCCESS).txt"):
			newFilename = keyword + "/" + keyword + "_" + i + "_(SUCCESS).txt"
		elif os.path.exists(keyword + "/" + keyword + "_" + i + "_(FAILURE).txt"):
			newFilename = keyword + "/" + keyword + "_" + i + "_(FAILURE).txt"
		elif os.path.exists(keyword + "/" + keyword + "_" + i + "_(ABORTED).txt"):
			newFilename = keyword + "/" + keyword + "_" + i + "_(ABORTED).txt"
		else:
			continue
		
		csvfilename =newFilename.replace('.txt', '.csv')
		if not os.path.exists(csvfilename):
			saveCSV(csvfilename, getBuildInfo(newFilename, keyword))
		
for arg in sys.argv[1:]:
	analysis(arg)
