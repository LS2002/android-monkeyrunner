A simple tool running on Mac to test music recognition of multiple applications using Monkeyrunner.

1. Download Android SDK http://developer.android.com/sdk/index.html
2. Put monkeyrunner in the path
   Mac: Edit bash_profile and add below 2 lines via Terminal
   		$nano ~/.bash_profile
        export ANDROID_HOME=/Applications/adt-bundle-mac-x86_64-20130917/sdk
        export PATH=$PATH:$ANDROID_HOME/build-tools/android-4.3:$ANDROID_HOME/platform-tools:$ANDROID_HOME/tools
3. Open Terminal and make new path work
		$source ~/.bash_profile
4. Install Shazam and Soundhound from Google Play
5. Install "easy_install" for Python
	$curl -O http://python-distribute.org/distribute_setup.py
	$sudo python distribute_setup.py
6. Install BeautifulSoup
	$easy_install BeautifulSoup4
7. Install PIL for image processing
	# run below command for Mac OS 10.9 Mavericks
	$ln -s /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.9.sdk/System/Library/Frameworks/Tk.framework/Versions/8.5/Headers/X11 /usr/local/include/X11
	$sudo pip install pil
8. Put required apk file under same folder as qc.py for uninstall/reinstall purpose
	$adb shell pm list packages -f |grep midomiMusicIdentifier
	$adb shell pm list packages -f |grep shazam
	$adb pull /data/app/com.melodis.midomiMusicIdentifier.freemium-2.apk
	$adb pull /data/app/com.shazam.android-2.apk
9. Open another Terminal and run below command
	* run all tests in a row
	$python qc.py

	* run individual test
	$python qc.py shazam
	$python qc.py soundhound

	* run combination test
	$python qc.py shazam soundhound
