#!/usr/bin/env python

import sys

def main(args):
  arguments = dict(zip(args[0::2], args[1::2]))
  
  print "name,value"
  
  for name, value in arguments.items():
    print "%s,%s" % (name, value)
  
  return 0

if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))