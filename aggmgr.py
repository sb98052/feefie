import yaml
import os
import re

FIND_PATH='find'

class AggManager:
	def __init__(self, program):
		self.parsed = yaml.load(open(program))['entries']

		self.matches = {}
		for e in self.parsed:
			e['compiled_regex'] = re.compile(r'%s'%e['regex'])
			self.matches[e['name']]={}
	
	def match_on_file(self, f):
		for e in self.parsed:
			r = e['compiled_regex']
			m = re.match(r, f)
			if m:
				key = '###'.join(m.groups())
				try:
					self.matches[e['name']][key].append(f)
				except KeyError:
					self.matches[e['name']][key]=[f]

	def match_on_directory(self, dirname):
		cmdline = '%s %s -printf "%%P\n"'%(FIND_PATH, dirname)
		files = [line.rstrip() for line in os.popen(cmdline)]

		for f in files:
			self.match_on_file(f)

	def gen_defs(self):
		for e in self.parsed:
			n = e['name']
			i0 = 0
			i1 = 0
			self.defs = []
			self.cdefs = []
			self.xports = []
			psexp = []
			for k,l in self.matches[n].items():
				xvar='x%d'%i1
				for v in l:
					svar='s%d'%i0
					self.defs.append('DEF:%s=%s:value:AVERAGE'%(svar,v))
					if (psexp):
						psexp.extend([svar,'+'])
					else:
						psexp=[svar]
					i0+=1

				self.cdefs.append('CDEF:%s=%s'%(xvar,','.join(psexp)))
				i1+=1
				self.xports.append('XPORT:%s:"%s"'%(xvar,k))
				
			




