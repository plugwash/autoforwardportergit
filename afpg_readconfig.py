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

pathconfigsettings = set(["workingrepo","gitdir","tmp","outputdir","netrcfile"])

def getsuitegroups():
	result = []
	for section in config:
		#print(repr(section))
		if 'upstreamsuite' in config[section]:
			result.append(section)
	return result

def getsuites():
	result = set()
	for section in config:
		#print(repr(section))
		if 'upstreamsuite' in config[section]:
			result.add(section)
			result.add(config[section]['upstreamsuite'])
			if 'stagingsuite' in config[section]:
				result.add(config[section]['stagingsuite'])
	return result


def readconfigentry(section,item):
	item = item.lower()
	if section == '_special_':
		if item == 'suitegroups':
			return ' '.join(getsuitegroups())
		elif item == 'suites':
			return ' '.join(getsuites())
	else:
		#sys.stderr.write('reading config entry '+item+' from section '+section+"\n")
		if item in config[section]:
			value = config[section][item];
			if item in pathconfigsettings:
				if value[0:2] == '~/':
					value = os.path.join(os.getenv('HOME'),value[2:])
				else:
					value = os.path.join(configdir,value)
		else:
			if item == 'stagingsuite':
				value = section
			else:
				sys.stderr.write('config entry '+item+' not found in section '+section+"\n")
				sys.exit(2)
		return value

if __name__ == '__main__': #if we are being run directly rather than imported
	#print(repr(config['main']))
	#print("AFPGCONFIG='"+configdir+"'");
	#for (name,value) in config['main'].items():
	#	print(name+"='"+value+"'");
	for arg in sys.argv[1:]:
		(section,item) = arg.split(':',1)
		print(item+"='"+readconfigentry(section,item)+"'")

