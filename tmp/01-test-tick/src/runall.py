#!/usr/bin/env python

import os, stat, sys, datetime

thisScript = sys.argv[0]
srcDIR     = os.path.normpath(sys.argv[1])
outDIR     = os.path.normpath(sys.argv[2])

# append module path with srcDIR
sys.path.append(srcDIR)

# change directory to outDIR
os.chdir(outDIR)

time_string = str(datetime.datetime.now())
tz_string   = datetime.datetime.now(datetime.timezone.utc).astimezone().tzname()
print( "\n### system time: " + time_string + " " + tz_string )
print( "\n########################################" )

#################################################
#################################################
import sinfo, IPython

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
from testHawkesEM import test_HawkesEM
#test_HawkesEM()

#################################################
#################################################
print("\n\n########################################" )

print("\n### IPython.sys_info():")
print(       IPython.sys_info()  )

print("\n### sinfo.info():")
print(       sinfo.sinfo(print_std_lib = True, print_implicit = True)  )

print("\n########################################" )
time_string = str(datetime.datetime.now())
tz_string   = datetime.datetime.now(datetime.timezone.utc).astimezone().tzname()
print( "\n### system time: " + time_string + " " + tz_string + "\n" )
sys.exit(0)

