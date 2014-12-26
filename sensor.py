#!/usr/bin/python
import Adafruit_DHT
import rrdtool
import sys


SENSOR = Adafruit_DHT.AM2302
PIN = 4

class SensorError(Exception):
  pass

class ArgumentError(Exception):
  pass

def do_create(*args):
  if len(args) != 1:
    raise ArgumentError('Usage: create RRDFILE')

  rrdtool.create(args[0], '--step', '60',
    'DS:temperature:GAUGE:600:-50:100',
    'DS:humidity:GAUGE:600:0:100',
    'RRA:AVERAGE:0.5:1:1440',
    'RRA:MIN:0.5:1:1440',
    'RRA:MAX:0.5:1:1440',
    'RRA:AVERAGE:0.5:30:17520',
    'RRA:MIN:0.5:30:17520',
    'RRA:MAX:0.5:30:17520')

def readsensor():
  humidity, temperature = Adafruit_DHT.read_retry(SENSOR, PIN)
  if humidity is not None and temperature is not None:
    return humidity, round(temperature * 2) / 2
  else:
    raise SensorError('Could not read sensor')

def do_update(*args):
  if len(args) != 1:
    raise ArgumentError('Usage: update RRDFILE')

  humidity, temperature = readsensor()
  rrdtool.update(args[0], 'N:{:0.1f}:{:0.1f}'.format(temperature, humidity))

def do_read(*args):
  humidity, temperature = readsensor()
  print 'Temperature: {:0.1f}C, humidity={:0.1f}%'.format(temperature, humidity)

if __name__ == '__main__':
  COMMANDS = {'read': do_read, 'create': do_create, 'update': do_update}
  if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
    print 'Usage: {} COMMAND OPTIONS'.format(sys.argv[0])
    print '  commands: {}'.format(', '.join(COMMANDS))
    sys.exit(1)
  else:
    COMMANDS[sys.argv[1]](*sys.argv[2:])
