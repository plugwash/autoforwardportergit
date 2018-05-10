#!/usr/bin/python3
#(C) 2018 Peter Michael Green <plugwash@debian.org>
#This software is provided 'as-is', without any express or implied warranty. In
#no event will the authors be held liable for any damages arising from the use
#of this software.
#
#Permission is granted to anyone to use this software for any purpose, including
#commercial applications, and to alter it and redistribute it freely, subject to
#the following restrictions:
#
#1. The origin of this software must not be misrepresented; you must not claim.
#that you wrote the original software. If you use this software in a product,
#an acknowledgment in the product documentation would be appreciated but is.
#not required.
#
#2. Altered source versions must be plainly marked as such, and must not be
#misrepresented as being the original software.
#
#3. This notice may not be removed or altered from any source distribution.

import collections
from difflib import SequenceMatcher

def mergelists(a,b):
	acounts = collections.defaultdict(int)
	bcounts = collections.defaultdict(int)
	mcounts = collections.defaultdict(int)
	sm = SequenceMatcher(a = a, b = b)
	matching_blocks = sm.get_matching_blocks()
	#note: last block is a dummy;
	block = None
	aindex = 0
	bindex = 0
	mergedlist = []
	for nextblock in matching_blocks:
		if block is not None:
			for i in range(0,block.size):
				item = a[block.a+i]
				#logically the counts would be incremented here but
				#it's not actually nesacery because all we do with
				#the counts is compare them to each other, so
				#incrementing none of the counts is equivilent to
				#incrementing all of them.
				#acounts[item] += 1
				#bcounts[item] += 1
				#mcounts[item] += 1
				mergedlist.append(a[block.a+i])
			aindex = block.a + block.size
			bindex = block.b + block.size
		for i in range (aindex,nextblock.a):
			item = a[i]
			acounts[item] += 1
			if acounts[item] > mcounts[item]:
				mcounts[item] +=1
				mergedlist.append(item)
		for i in range (bindex,nextblock.b):
			item = b[i]
			bcounts[item] += 1
			if bcounts[item] > mcounts[item]:
				mcounts[item] +=1
				mergedlist.append(item)
		block = nextblock

	#for entry in mergedlist:
	#	print(entry)
	#exit(1)
	return mergedlist

