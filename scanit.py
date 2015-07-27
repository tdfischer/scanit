#!/usr/bin/env python
import pyinsane.abstract as pyinsane
import subprocess
import tempfile
from PIL import Image
import os
import sys

toolsFound = True
pageCount = 1

try:
  subprocess.call(['pngcrush', '--version'])
except OSError:
  toolsFound = False
  print "Missing: pngcrush"
try:
  subprocess.call(['pngnq', '--version'])
except OSError:
  toolsFound = False
  print "Missing: pngnq"
try:
  subprocess.call(['convert', '--version'])
except OSError:
  toolsFound = False
  print "Missing: convert"

if not toolsFound:
  sys.exit(1)

if len(sys.argv) == 1:
  sessionName = raw_input("What filename will you give this session? [foo.pdf] ")
else:
  sessionName = sys.argv[1]

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

if 'LineArt' in device.options['mode'].constraint:
    device.options['mode'].value = 'LineArt'
elif 'Gray' in device.options['mode'].constraint:
    device.options['mode'].value = 'Gray'

print 'Scanning with Device %s'%(device.name,)


while True:
  session = None
  try:
    session = device.scan(multiple=False)
  except StopIteration:
    pass

  if session is None:
    print "Insert document"
    continue

  try:
    while True:
      session.scan.read()
  except EOFError:
    pass

  fh, tmpfile = tempfile.mkstemp()
  os.close(fh)
  output = "%s-%d.png"%(sessionName, pageNum)
  image = session.images[0]
  image.crop((0, 0, imgWidth, imgHeight)).save(tmpfile, "PNG")
  print "Wrote", tmpfile
  subprocess.call(['pngnq', tmpfile])
  subprocess.call(['pngcrush', tmpfile+'-nq8.png', output])
  print "Saved to", output
  pageNum += 1
  if pageNum >= pageCount:
    break

fnames = map(lambda x:"%s-%d.png"%(sessionName, x), xrange(0, pageNum))

subprocess.call(['convert', ] + fnames + [sessionName+'.pdf'])
for f in fnames:
  os.unlink(f)
print "Wrote %s.pdf"%(sessionName)
