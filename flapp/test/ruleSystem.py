import sys, os
sys.path = [os.path.join(os.getcwd(), "..", "..") ] + sys.path

from flapp.RuleSystem import ruleSystem
from flapp.RuleSystem.ruleSystem import RuleSystem
from flapp.RuleSystem.triggers import *

r = RuleSystem()

global keypressess
keypresses = 0
def CountKeyPresses():
    print "Counting"
    keypresses += 1

r.addTriggerResponse(TriggerWhenKeyPressed("k"), ruleSystem.Response("CountKeys", CountKeyPresses, []))

r.triggerRule(TriggerWhenKeyPressed("k"))

assert(keypresses == 1)
