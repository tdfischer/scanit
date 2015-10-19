#!/usr/bin/env python
import pyinsane.abstract as pyinsane
import subprocess
import tempfile
from PIL import Image
import os
import sys

import threading
import argparse

parser = argparse.ArgumentParser(description='Scan It')
parser.add_argument('name', default=None, type=unicode, help='Session name')
parser.add_argument('-n', default=0, type=int, dest='page_count', help='Number of pages to scan')
parser.add_argument('--color', action='store_true', default=False)
parser.add_argument('--grey', action='store_true', default=False)
parser.add_argument('--gray', action='store_true', dest='grey')
parser.add_argument('--crop', action='store_true', dest='crop', default=True)
parser.add_argument('--no-crop', action='store_false', dest='crop')

args = parser.parse_args()

toolsFound = True
pageCount = args.page_count

def processPage(src, dst):
  subprocess.call(['pngnq', src])
  subprocess.call(['pngcrush', src+'-nq8.png', dst])
  print "Saved to", dst

try:
  subprocess.call(['pngcrush', '-version'])
except OSError:
  toolsFound = False
  print "Missing: pngcrush"
try:
  subprocess.call(['pngnq', '-V'])
except OSError:
  toolsFound = False
  print "Missing: pngnq"
try:
  subprocess.call(['convert', '-version'])
except OSError:
  toolsFound = False
  print "Missing: convert"

if not toolsFound:
  sys.exit(1)

if args.name is None:
  sessionName = raw_input("What filename will you give this session? [foo.pdf] ")
else:
  sessionName = args.name

if sessionName == '':
  sessionName = 'foo.pdf'

pageNum = 0

devices = pyinsane.get_devices()

device = pyinsane.Scanner(name=devices[0].name)

for o in device.options:
    print o, device.options[o].constraint

if device.name.startswith('v4l'):
    device = pyinsane.Scanner(name=devices[1].name)

dpi = 300
imgWidth = int(dpi * 8.5)
imgHeight = int(dpi * 11)

if 'resolution' in device.options:
  device.options['resolution'].value = dpi

if args.color:
    device.options['mode'].value = 'Color'
elif args.grey:
    device.options['mode'].value = 'Gray'
else:
    if 'LineArt' in device.options['mode'].constraint:
        device.options['mode'].value = 'LineArt'
    elif 'Gray' in device.options['mode'].constraint:
        device.options['mode'].value = 'Gray'

print 'Scanning with Device %s'%(device.name,)

processThreads = []

def scanPage():
  session = None
  nag = False
  while session is None:
    if not nag:
      print "Insert document"
      nag = True
    try:
      session = device.scan(multiple=False)
    except StopIteration:
      pass

  try:
    while True:
      session.scan.read()
  except EOFError:
    pass

  fh, tmpfile = tempfile.mkstemp()
  os.close(fh)
  image = session.images[0]
  if args.crop:
      image.crop((0, 0, imgWidth, imgHeight)).save(tmpfile, "PNG")
  else:
      image.save(tmpfile, "PNG")
  return tmpfile

try:
  while True:
    tmpfile = scanPage()
    print "Wrote", tmpfile
    output = "%s-%d.png"%(sessionName, pageNum)
    t = threading.Thread(target=processPage, args=[tmpfile, output])
    processThreads.append(t)
    t.start()
    pageNum += 1
    if pageNum >= pageCount:
      break
except KeyboardInterrupt:
  pass

for t in processThreads:
  print "Waiting for threads to finish processing..."
  t.join()

fnames = map(lambda x:"%s-%d.png"%(sessionName, x), xrange(0, pageNum))

subprocess.call(['convert', ] + fnames + [sessionName+'.pdf'])
for f in fnames:
  os.unlink(f)
print "Wrote %s.pdf"%(sessionName)
