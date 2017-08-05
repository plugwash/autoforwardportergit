#!/usr/bin/python3

import configparser
import os
import sys

configdir = os.getenv('AFPGCONFIG');
if configdir is None:
	configdir = os.path.join(os.getenv('HOME'),'.autoforwardportergit')

if not os.path.isdir(configdir):
	sys.stderr.write('autoforwardportergit config directory '+configdir+" does not exist or is not a directory\n")
	sys.exit(1)

sys.stderr.write('using autoforwardportergit config directory '+configdir+"\n")

#print(repr(configdir))
configfile = os.path.join(configdir,'afpg.ini')
config = configparser.ConfigParser()
config['main'] = {}
config['main']['dosbuild'] = 'no';
config['main']['dodgitpush'] = 'no';
config['main']['AFPGCONFIG'] = configdir;
config.read(configfile)

def readconfigentry(section,item):
	value = config[section][item];
	if ((item == 'workingrepo') | (item == 'gitdir') | (item == 'tmp')):
		value = os.path.join(configdir,value)
	return value

if __name__ == '__main__': #if we are being run directly rather than imported
	#print(repr(config['main']))
	#print("AFPGCONFIG='"+configdir+"'");
	#for (name,value) in config['main'].items():
	#	print(name+"='"+value+"'");
	for arg in sys.argv[1:]:
		(section,item) = arg.split(':',1)
		print(item+"='"+readconfigentry(section,item)+"'")
