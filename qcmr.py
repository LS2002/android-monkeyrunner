#!/usr/bin/env python
# -*- coding: utf-8 -*- 

# Imports the monkeyrunner modules used by this program
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice

from threading import Thread
import os, sys, getopt, time, datetime


def main():
	
	appName = str(sys.argv[1])

	currentTrackNumber = str(sys.argv[2])

	screenshotInterval = float(sys.argv[3])
	screenshotTotal = int(sys.argv[4])

	timeForLaunchApp = int(sys.argv[5])
	timeToStopVLC = int(sys.argv[6])

	touchCoordinateX = int(sys.argv[7])
	touchCoordinateY = int(sys.argv[8])

	snapshotFolder = str(sys.argv[9])

	timeForAppSleepBeforeTouch = int(sys.argv[10])

	# Start application depending on specified app name, and music sequence name

	printCurrentTimestamp('#13')

	# if Shazam
	if appName == 'shazam':
		device.startActivity(component='com.shazam.android/com.shazam.android.activities.Splash')
	
	# if Soundhound
	if appName == 'soundhound':
		device.startActivity(component='com.melodis.midomiMusicIdentifier.freemium/com.soundhound.android.appcommon.activity.SoundHound')


	# if Google, no need to launch activity as it's a widget
	if appName == 'google':
		# return Home screen to use the widget manually put there
		device.press('KEYCODE_HOME', MonkeyDevice.DOWN_AND_UP)

	# Create snapshot folder if not exist
	if not os.path.exists('./' + snapshotFolder):
		os.makedirs('./' + snapshotFolder)

	# Step 3 - touch app and take snapshot


	# touch to start listening
	MonkeyRunner.sleep(timeForAppSleepBeforeTouch) # let music play for 3+ seconds before touch & recognize
	device.touch(touchCoordinateX,touchCoordinateY, 'DOWN_AND_UP');

	# take snapshot
	i = 0
	while i < screenshotTotal:
		# take snapshot in another thread
		Thread(target=takeDeviceSnapshot, args=(snapshotFolder,appName,currentTrackNumber,i)).start()

		# pause 1s before take next snapshot
		MonkeyRunner.sleep(screenshotInterval)
		i += 1

	# wait untill all screenshot threads are done
	MonkeyRunner.sleep(screenshotTotal*(2-screenshotInterval))

	# exit app after audio stops, and wait for VLC completely quit
	# MonkeyRunner.sleep(timeForLaunchApp + timeToStopVLC - screenshotTotal*screenshotInterval + 5)
	device.press('KEYCODE_BACK', MonkeyDevice.DOWN_AND_UP)
	MonkeyRunner.sleep(1)
	device.press('KEYCODE_BACK', MonkeyDevice.DOWN_AND_UP)
	MonkeyRunner.sleep(1)
	device.press('KEYCODE_BACK', MonkeyDevice.DOWN_AND_UP)
	printCurrentTimestamp('#16')


def takeDeviceSnapshot(snapshotFolder,appName,currentTrackNumber,count):
	result = device.takeSnapshot()
	fileName = './' + snapshotFolder + '/' + appName + '_' + currentTrackNumber + '_' + str(count) + '.png'
	result.writeToFile(fileName,'png')


def unlockDevice(device):
    device.wake()
    device.drag((130, 620), (350, 620), 1.0, 120)

def backToHome(device):
	device.press('KEYCODE_BACK', MonkeyDevice.DOWN_AND_UP)
	device.press('KEYCODE_BACK', MonkeyDevice.DOWN_AND_UP)
	device.press('KEYCODE_BACK', MonkeyDevice.DOWN_AND_UP)

def printCurrentTimestamp(message):
	print message, datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')



if __name__ == '__main__':
	# Connects to the current device, returning a MonkeyDevice object
	device = MonkeyRunner.waitForConnection()

	# run once to close up any running app
	backToHome(device)

	# call main function
	main()
