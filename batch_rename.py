#coding=utf-8
import os
import re

for file in os.listdir("WeNavi_Android"):
	if file.startswith("WeNaiv"):
		os.rename("WeNavi_Android/" + file, "WeNavi_Android/" + file.replace("WeNaiv", "WeNavi"))