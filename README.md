# splinify
![Splinify_img1](https://raw.githubusercontent.com/wayneyip/splinify/master/splinify_gif1.gif)

Maya Python tool to automate spline IK joint chain setup on two given joints.

## Features
- Automatic setup of up to 100 sub-joints within 1 second
- Interpolated coloring of control curves based on user-input colors
- Custom attribute to adjust length of joint chain along spline

## Instructions

- Place `wy_splinify.py` and `wy_splinifyUI.py` in your Maya Scripts folder, found in:
    - Windows: `C:\Users\<Your-Username>\Documents\maya\<20xx>\scripts`
    - OSX: `/Users/<Your-Username>/Library/Preferences/Autodesk/maya/<20xx>/scripts`
    - Linux: `/home/<Your-Username>/maya/<20xx>/scripts`
- Restart/open Maya, then open the Script Editor by:
	- Going to `Windows > General Editors > Script Editor`

		**or**
	- Left-clicking the `{;}` icon at the bottom-right of your Maya window
- Copy/paste and run the following code in your Script Editor:

	```
	import wy_splinifyUI
	reload (wy_splinifyUI)
	wy_splinifyUI.splinifyUI()
	```
	to launch the Splinify tool UI.

- (Extra) Save the UI launch code to a shelf button:
	- Go to `File > Save Script to Shelf` in the Script Editor
	- Type in a name for the button (e.g. "Splinify"), and hit OK
	- Splinify should now be saved as a button in your shelf.

## Details

**Technologies**: Maya, Python

**Developer**: Wayne Yip

**Contact**: yipw@usc.edu

