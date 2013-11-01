import mote
from moteCache import MoteCache

if __name__ == "__main__":
    cache = MoteCache()
    cache.read()

    # print "GetMotes:", cache.getMotes()

    for mote in cache.getMotes().values():
        print mote.getServices()


# Generally:
"""
[{'protocol': 'L2CAP',
  'name': None,
  'service-id': None,
  'profiles': [('0100', 256)],
  'service-classes': ['1000'],
  'host':
  '00:17:AB:32:BF:EF',
  'provider': None,
  'port': 1,
  'description': None},
 {'protocol': 'L2CAP',
  'name': 'Nintendo RVL-CNT-01',
  'service-id': None,
  'profiles': [('1124', 256)],
  'service-classes': ['1124'],
  'host': '00:17:AB:32:BF:EF',
  'provider': 'Nintendo',
  'port': 17,
  'description': 'Nintendo RVL-CNT-01'},
 {'protocol': 'L2CAP',
 'name': None,
 'service-id': None,
 'profiles': [('1200', 256)],
 'service-classes': ['1200'],
 'host': '00:17:AB:32:BF:EF',
 'provider': None,
 'port': 1,
 'description': None}]
"""
