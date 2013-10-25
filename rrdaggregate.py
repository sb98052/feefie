#!/usr/bin/python

import yaml
import argparse
import os
from aggmgr import AggManager

expressions="""
(node\d+.princeton.vicci.org)/cpu-\d/.*
"""

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-datadir',help='Directory location of your rrd files',default='/usr/var/lib/collectd/rrd')
	parser.add_argument('-rrdopts',help='Option string passed verbatim to rrdtool',default='--start now-1h --end now --json')
	parser.add_argument('-pretend',help='Debug only',default=False,action='store_true')
	parser.add_argument('program',help='Program in YAML that specifies the required aggregation.')
	values = parser.parse_args()

	aggp = AggManager(values.program)
	aggp.match_on_directory(values.datadir)
	aggp.gen_defs()

	options = {'verbatim':values.rrdopts, 'defs':' '.join(aggp.defs), 'cdefs':' '.join(aggp.cdefs), 'xports':' '.join(aggp.xports)}
	#print "Defs = %s\nCDefs=%s\nXports=%s"%(aggp.defs,aggp.cdefs,aggp.xports)
	os.chdir(values.datadir)
	cmdline = """
	rrdtool xport %(verbatim)s %(defs)s %(cdefs)s %(xports)s
	"""%options

	if (not values.pretend):
		os.system(cmdline)
	else:
		print cmdline
	


if __name__=='__main__':
	main ()
