# MIT License

# Copyright (c) 2025 DerKastellan

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import glob
import os
import pathlib
import re
import shutil
import sys

# DISCLAIMER: The names "Toontrack" and "Addictive Drums" are trademarks of their respective owners, which are in no way
# associated or affiliated with the creation or distribution of this script. This script can be used by an owner of Toontrack
# MIDI products to use on their own installed MIDI files at their own discretion.

# NOTE: This script does not change or delete any existing files. It will only create new folders and copy files there.

# NOTE: How to use this script.
#       Install Python (python3) and make sure it's included in your path. (Windows version does this automatically.)
#       Install the Toontrack MIDI packages using the Toontrack Product Manager.
#       Make a folder where you copy the Toontrack packages you want to use in AD2.
#		They look like this: 000332@DOOM_GROOVES or 000334@FUNK
#       Copy this script into the same folder.
#		Open a command prompt (on Windows: Win key+R, then "cmd")
#       Run it like this: python3 convert_toontrack_midi.py <package name> <style>
#       Example: python3 convert_toontrack_midi.py 000353@UK_DANCE Electronic
#       This should print some information for every MIDI file in the package while working.
#       When it's done, a new folder has been created with the converted files.
#       It may look like this: "ToonTrack Uk Dance"
#       There should be .mid files in it like this: "UK DANCE S011 Straight 4#4_V_Groove 01_C_Electronic.mid"
#		You now can copy this for use into AD2. (Right-click the folder and click "Cut".)
#		Open AD2.
#		Navigate to Settings -> Open External MIDI folder (a file explorer should open)
#       Right-click and paste your folder there.
#       Navigate to Settings -> Refresh MIDI Library
#		Your new beats should show up on the left-side tab under EXTERNAL MIDI in the BEATS tab.

# NOTE: For automated MIDI mapping support, do this below.
# 		Navigate here in Addictive Drums 2:
# 		Settings -> MIDI Mapping -> (Selection Dropdown top center) -> Other plugins -> Toontrack EZD3
# 		Then: (Selection Dropdown to center) -> Save -> Save as...
# 		Leave the MIDI Mapping dialog by hitting "Cancel" bottom left (this should restore the default)
# 		Then: Settings -> Open User Folder
# 		You get a file explorer with the same location as the MIDI mapping files - they have the ending/suffix .AD2Map
# 		Copy the EZDrummer one to the same folder you run this script from.
#		The script will copy the .AD2Map file into every package you convert with the right name automatically.
#		When you load the package in AD2 later it should now use the right MIDI mapping automatically.

def convert_package_name(name_string):
	return name_string.split("@")[1].replace("_", " ")

def extract_number(variation):
	return re.search(r'\d+', variation)[0]

# I tried this script on several MIDI packages by Toontrack
# I personally like to rename some like FILLS before using them
# Add any such conversions just here in the same syntax
def convert_type(type):
	type = type.title()
	type = "Fill" if type == "Fills" else type
	type = "Break" if type == "Breaks" else type
	type = "Groove" if type == "Grooves" else type
	return type

def convert_path(path):
	components = path.split("\\")
	package = convert_package_name(components[0])
	[groove, signature] = components[1].split("@")[1].split("_")
	[bpm, temp] = components[2].split("-")
	[group, type] = temp.split("@")
	variation = extract_number(components[3])
	
	return (path, bpm, package, groove.title(), signature, group, convert_type(type), variation)
	
def file_name(package, groove, signature, group, type, number, category):
	# make sure fills are recognized as such (naming convention)
	fill = "_F_" if type == "Fill" else ""
	category = "_C_{}".format(category)
	template = "{} {} {} {}_V_{} {}{}{}.mid"
	# prefixing the package name is necessary, else all the groups of all packages
	# will be grouped together by Addictive Drums, which gives a huge mess quickly
	return template.format(package, group, groove, signature, type, number, category, fill)

def get_all_midi(package):
	paths = glob.glob("{}/**/*.mid".format(package), recursive=True)
	return map(convert_path, paths)

def make_folder_name(package):
	return "ToonTrack {}".format(package.title())

def copy_file(components, category):
	# print params for debug info
	print(repr(components))
	
	# the package name shall be the directory
	dir = make_folder_name(components[2])
	name = file_name(*components[2:], category)
	path = pathlib.Path(dir)
	path.mkdir(exist_ok=True)
	complete = path / name
	shutil.copyfile(components[0], complete)

def copy_optional_mapping_file(package):
	orig = glob.glob("*.AD2Map")
	print(repr(orig))
	if orig != []:
		orig = orig[0] # first match
		dir  = make_folder_name(convert_package_name(package))
		path = pathlib.Path(dir)
		name = "{}.AD2Map".format(dir)
		dest = path / name	
		shutil.copyfile(orig, dest)

if __name__ == "__main__":
	# first argument is the original folder of the original MIDI package
	# please copy this locally, it would for example look like this: 000334@FUNK
	package  = sys.argv[1]
	# second argument is the musical Style seen in AD, for example Funk or Electronic
	category = sys.argv[2]

	for components in get_all_midi(package):
		copy_file(components, category)

	copy_optional_mapping_file(package)
