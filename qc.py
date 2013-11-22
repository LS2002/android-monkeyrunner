#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from BeautifulSoup import BeautifulSoup
from threading import Thread
	
import time
import urllib2
import shutil
import urlparse
import os
import re
import sys
import getopt
import datetime
import errno


def main():

	global appNames
	global reportFileName, reportFileNamePrev
	global htmlHeaders, htmlFooters
	global url_array
	global url_base

	url_array.append(['US',	url_base + 'us.xml'])
	url_array.append(['UK',	url_base + 'uk.xml'])
	url_array.append(['FR',	url_base + 'fr.xml'])
	url_array.append(['IT',	url_base + 'it.xml'])
	url_array.append(['DE',	url_base + 'de.xml'])
	url_array.append(['ES',	url_base + 'es.xml'])
	url_array.append(['JP',	url_base + 'jp.xml'])

	# url_array.reverse()

	global timeToStopMonkeyrunner
	timeToStopMonkeyrunner = screenshotTotal*screenshotInterval*timeToTakeSingleScreenshot + timeForLaunchApp + timeForAppSleepBeforeTouch + 1 + 1 # here 2 seconds for monkeyrunner take snapshot
	
	# if there's one or more parameters(app name) after "python qc.py" then test those in a row
	if len(sys.argv)==1:
		appNames = ["shazam","soundhound","google"]
	else:
		i = 1
		while i < len(sys.argv):
			appNames.append(sys.argv[i])
			i += 1

	# TEST AREA - BEGIN
	# print ','.join(['Track #','Track-Artist','coverart url','audio url']) + '\n'
	# restartADB()
	# sys.exit(0)
	# TEST AREA - END


	for country in url_array:

		reportFileName = 'QC_' + country[0] + '_' + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')
		reportFileNamePrev = reportFileName

		htmlHeaders  = '<html><head><title>QC - ' + country[0] + ' @ ' + ' '.join(appNames) + '</title>'
		htmlHeaders += '<style>.cell_header60px {display: table-cell; padding:5px; vertical-align: middle; width:60px; border-bottom:1px solid black; text-align: center;} .cell_header180px {display: table-cell; padding:5px; vertical-align: middle; width:180px; border-bottom:1px solid black; text-align: center;white-space:normal;min-width:180px; overflow:auto;} .cell_screenshot {display: table-cell; padding:5px; vertical-align: middle; width:180px; border-bottom:1px solid black;} </style>'
		htmlHeaders += '</head><body><center><p>QC - '+ country[0] + ' @ ' + ' '.join(appNames) + '</p></center><div style="display: table; border:1px solid black;">'
		htmlHeaders += '<div style="display: table-row;"><div class="cell_header60px">#</div><div class="cell_header180px">Track - Artist</div><div class="cell_header180px">Cover@RSS</div><div class="cell_header60px">audio</div>'

		htmlTemp = '<div>'
		i = 0
		while i < screenshotTotal:
			htmlTemp += '<div class="cell_header180px">' + str(i * screenshotInterval) + 's</div>'
			i += 1

		htmlHeaders += htmlTemp+'</div></div>'

		htmlFooters = '</div></body></html>'

		# start to test on each app
		startAppTest(getRSSContent(country[1]), country[0])

	
def test_Shazam(appName,currentTrackNumber):
	touchCoordinateX = 600
	touchCoordinateY = 960
	startSingleTest(appName,currentTrackNumber,touchCoordinateX,touchCoordinateY)


def test_Soundhound(appName,currentTrackNumber):
	# Nexus 7
	# touchCoordinateX = 600
	# touchCoordinateY = 350

	# SS-GS4
	touchCoordinateX = 600
	touchCoordinateY = 600

	startSingleTest(appName,currentTrackNumber,touchCoordinateX,touchCoordinateY)


def test_Google(appName,currentTrackNumber):
  # need to place Music widget on Desktop at the coordinate specified below
	touchCoordinateX = 560
	touchCoordinateY = 1040
	startSingleTest(appName,currentTrackNumber,touchCoordinateX,touchCoordinateY)


def getRSSContent(url):
	html_page = urllib2.urlopen(url).read()
	return BeautifulSoup(html_page)


def startAppTest(bs4_content, countryName):

	global reportFileName, reportFileNamePrev
	# header of csv file
	writeCSV('	'.join(['Country','Track #','Track-Artist','Coverart Url','Audio Url']) + '\n')


	currentTrackNumber = 0
	for entry in bs4_content.findAll("entry"):
		if currentTrackNumber == 0:
			assembleHTML(htmlHeaders)

		link = entry.find("link", attrs={"type":"audio/x-m4a"})
		global audioUrl
		audioUrl = link.get('href')

		nameTrackArtist = entry.find('title').next
		coverImageUrl = entry.find("im:image", attrs={"height":"170"}).next

		print ','.join([countryName, str(currentTrackNumber+1),nameTrackArtist,coverImageUrl,audioUrl])
		writeCSV('	'.join([str(currentTrackNumber+1), nameTrackArtist, coverImageUrl, audioUrl]) + '\n')

		# write to html
		assembleHTML('<div style="display: table-row;"><div class="cell_header60px">' + str(currentTrackNumber+1) + '</div><div class="cell_header180px">' + nameTrackArtist + '</div><div class="cell_screenshot"><img src=' + coverImageUrl + ' /></div><div class="cell_header60px"><a href=' + audioUrl + '>m4a</a></div>')

		for id, appName in enumerate(appNames):

			if appName == 'shazam':
				test_Shazam(appName,currentTrackNumber)
			elif appName == 'soundhound':
				test_Soundhound(appName,currentTrackNumber)
			elif appName == 'google':
				test_Google(appName,currentTrackNumber)
			else:
				break


			htmlTemp  = '<div>'
			i = 0
			while i < screenshotTotal:
				htmlTemp += '<div class="cell_screenshot"><a target="_blank" href="./'+ reportFileName + '/' + appName + '_' + str(currentTrackNumber) + '_' + str(i)+ '.png"><img width=170 src="./'+ reportFileName + '/' + appName + '_' + str(currentTrackNumber) + '_' + str(i)+ '.png" /></a></div>'
				i += 1
			# close up app html div block
			assembleHTML(htmlTemp+'</div>')

			# resize screenshot after monkeyrunner is done
			Thread(target=resizeScreenshotImageAll, args=(appName,currentTrackNumber)).start()

			# wait for resize image complete
			time.sleep(timeToResizeImages) 


		# close up the div table-row block
		assembleHTML('</div>')
	
		# increment count
		currentTrackNumber += 1

		if currentTrackNumber % dividReportAtTrackCount == 0:
			assembleHTML(htmlFooters)
			if currentTrackNumber < 100:
				reportFileNamePrev = reportFileName + '_' + str(currentTrackNumber / dividReportAtTrackCount)
				assembleHTML(htmlHeaders)
	
				# uninstall and install app to bypass the ANR issue
				reinstall_soundhound_in_thread()
	
				# sleep main to allow app be fully uninstalled then reinstalled
				time.sleep(timeToReinstallApp)
	
				# restart adb to avoid of connection erro
				restartADB()

	print 'QC is done for',countryName,'!'


def startSingleTest(appName, currentTrackNumber, touchCoordinateX, touchCoordinateY):

		# Step 1 - Call qcmr.py right before play audio via VLC
		command = ['monkeyrunner','qcmr.py', appName, str(currentTrackNumber), str(screenshotInterval), str(screenshotTotal), str(timeForLaunchApp), str(timeToStopVLC), str(touchCoordinateX), str(touchCoordinateY), reportFileName, str(timeForAppSleepBeforeTouch)]
		# print command
		run_monkeyrunner_in_thread(command)

		# wait till app fully launch on device
		time.sleep(timeForLaunchApp)

		# Step 2 - play audio in parallel, audio will stop at 15 seconds
		playAudioFile(audioUrl)

		# wait for monkeyrunner finish, otherwise cause image processing thread fail at open the unsaved image file
		time.sleep(timeToStopMonkeyrunner - timeToStopVLC - timeForLaunchApp - 12)


def playAudioFile(audio_path):
	vlc_path = '/Applications/VLC.app/Contents/MacOS/VLC'
	# audio_path = 'http://a1819.phobos.apple.com/us/r1000/013/Music/v4/f5/d2/05/f5d205c6-1bc1-affa-0a4b-028442640e01/mzaf_5120003320374674708.plus.aac.p.m4a'
	run_command_with_timeout([vlc_path, audio_path, '--play-and-exit','--stop-time='+ str(timeToStopVLC)],timeToStopVLC)

def reinstall_soundhound_in_thread():
	Thread(target=reinstall_soundhound, args=()).start()

def reinstall_soundhound():
	run_command(['adb','uninstall','com.melodis.midomiMusicIdentifier.freemium'])
	run_command(['adb','install','com.melodis.midomiMusicIdentifier.freemium-1.apk'])

def run_monkeyrunner_in_thread(command):
	Thread(target=run_monkeyrunner, args=(command,)).start()

def run_monkeyrunner(command):
	run_command(command)

def run_command_in_thread(command):
	Thread(target=run_command, args=(command,)).start()

def run_command(command):
	import subprocess
	subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def run_command_with_timeout(command, timeout):
	"""call shell-command and either return its output or kill it
	if it doesn't normally exit within timeout seconds and return None"""
	import subprocess, datetime, os, time, signal
	start = datetime.datetime.now()
	process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	while process.poll() is None:
		time.sleep(0.1)
		now = datetime.datetime.now()
		if (now - start).seconds > timeout:
			os.kill(process.pid, signal.SIGKILL)
			os.waitpid(-1, os.WNOHANG)
			return None
	return process.stdout.read()


def assembleHTML(htmlstr):
	with open(reportFileNamePrev + ".html", "a+") as html_file:
		html_file.write(htmlstr.encode('utf8'))


def writeCSV(line):
	with open(reportFileName + ".csv", "a+") as csv_file:
		csv_file.write(line.encode('utf8'))


def resizeScreenshotImageAll(appName, currentTrackNumber):
	i = 0
	while i < screenshotTotal:
		resizeScreenshotImageSingle(appName, currentTrackNumber, i)
		i += 1

def resizeScreenshotImageSingle(appName, currentTrackNumber, count):
	import PIL
	from PIL import Image
	fileName = './' + reportFileName + '/' + appName + '_' + str(currentTrackNumber) + '_' + str(count) + '.png'

	resizedHeight = 720
	img = None
	try:
		img = Image.open(fileName)
	except IOError as e:
		print 'IOError @ Track #', currentTrackNumber

	if img != None:
		hpercent = (resizedHeight / float(img.size[1]))
		wsize = int((float(img.size[0]) * float(hpercent)))
		img = img.resize((wsize, resizedHeight), PIL.Image.ANTIALIAS)
		img.save(fileName)
		del img


def printCurrentTimestamp(message):
	# print message, datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')
	i = 0

def restartADB():
	import os
	printCurrentTimestamp('restart ADB begins')
	# os.system("kill $(ps -fe | grep 'adb' | grep -v grep | awk '{print $2}')")
	os.system("ps -fe | grep 'adb' | grep -v grep | awk '{print $2}' | xargs kill -9")
	os.system('android update adb;adb kill-server;adb start-server;adb devices')
	printCurrentTimestamp('restart ADB ends')


if __name__ == '__main__':
	# Extract top 100 tracks from iTunes RSS
	# url_itunes = 'https://itunes.apple.com/us/rss/topsongs/limit=100/xml'
	url_array = []
	url_base = 'http://<my-host-server>/qc/'

	appNames = []
	
	reportFileName = None
	reportFileNamePrev = None

	htmlHeaders = None
	htmlFooters = None

	# set this to desired value to divide the report to multiple files to avoid of browser crash
	dividReportAtTrackCount = 2

	nameTrackArtist = None
	coverImageUrl = None
	audioUrl = None

	timeForLaunchApp = 10
	timeForAppSleepBeforeTouch = 12
	timeToStopVLC = 20
	timeToStopMonkeyrunner = 60 # timeForLaunchApp + MonkeyRunner.sleep (2+1+1+1) + 3 * screenshotTotal (10+(2+1+1+1)+15*3)
	timeToReinstallApp = 15
	timeToResizeImages = 6
	timeToTakeSingleScreenshot = 3

	screenshotInterval = 1 # save screenshot every 1 second
	screenshotTotal = 15 # save 8 screenshot for each track played

	# run main function
	main()
