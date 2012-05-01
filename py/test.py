#!/bin/env python

from cue import *

if __name__ == '__main__':
    cf = CueParser()
    cf.load('test/archive/Alestorm/Back Through Time.cue')
    print str(cf).rstrip('\n')

