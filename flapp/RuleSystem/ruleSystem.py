
# Univesity of Chicago,
# Feb 2, 2008
# Eric Olson
# adapted from home version written by Eric.

import traceback

class Trigger:
    def __init__(self, name="DefaultTriggerName"):
        self.name = name

class Response:
    def __init__(self, name="GenericResponse", callback = None, firstArgs = []):
        self.name = name
        self.callback = callback
        self.firstArgs = firstArgs
    def execute(self, trigger, args=[]):
        if self.callback != None:
            apply(self.callback, [trigger, self.firstArgs + args])

class Rule:
    def __init__(self, trigger, response):
        self.trigger = trigger
        self.response = response

class RuleSystem:
    def __init__(self, name="DefaultRuleSystemName"):
        self.name = name
        self.rules = dict()

    def addRule(self, rule):
        if rule.trigger.name not in self.rules:
            self.rules[rule.trigger.name] = [rule]
        else:
            self.rules[rule.trigger.name].append(rule)
        print "(" + self.name + ") Added rule", rule.trigger.name, ", ", rule.response.name
    def addTriggerResponse(self, trigger, response):
        self.addRule(Rule(trigger, response))

    def removeRule(self, rule):
        # Does not require the same "Rule" instance.
        #   but so far, does require the same response instance
        if rule.trigger.name in self.rules:
            rule_list = self.rules[rule.trigger.name]
            # Remove response
            try:
                for rl in rule_list:
                    if rl.response == rule.response:
                        rule_list.remove(rl)
                        break
            except ValueError:
                import traceback
                traceback.print_exc()
                print rule.trigger.name, " response: ", rule.response, " list:", rule_list, "in? ", rule.response in rule_list, "equal?", rule.response == rule_list[0], "equal_same?", rule.response == rule.response
                import sys
                sys.exit()
            # If no responses left with trigger name, remove the entire rule
            if len(self.rules[rule.trigger.name]) == 0:
                del self.rules[rule.trigger.name]
        print "Removed rule", rule.trigger.name, ", ", rule.response.name

    def triggerRule(self, trigger_name, args=[]):
        try:
            # print "triggerRule", trigger_name, self.rules.keys(), trigger_name in self.rules.keys()
            if trigger_name in self.rules.keys():
                for triggered_rule in self.rules[trigger_name]:
                    triggered_rule.response.execute(triggered_rule.trigger, args)
            else:
                pass # print "no response for", trigger_name
        except:
            traceback.print_exc()


