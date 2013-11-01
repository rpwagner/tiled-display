from flapp.RuleSystem.ruleSystem import Trigger

class TriggerWhenKeyPressed(Trigger):
    def __init__(self, key):
        self.name = "KeyPress_" + str(key)

class TriggerWhenKeyReleased(Trigger):
    def __init__(self, key):
        self.name = "KeyRelease_" + str(key)

class TriggerWhenAnyKeyPressed(Trigger):
    def __init__(self):
        self.name = "KeyPress"

class TriggerWhenAnyKeyReleased(Trigger):
    def __init__(self):
        self.name = "KeyRelease"

class TriggerOnAnyKeyEvent(Trigger):
    def __init__(self):
        self.name = "KeyEvent"

class TriggerOnMouseEvent(Trigger):
    def __init__(self):
        self.name = "MouseEvent"

class TriggerOnMouseMotionEvent(Trigger):
    def __init__(self):
        self.name = "MouseMotion"

class TriggerOnJoystickButtonEvent(Trigger):
    def __init__(self):
        self.name = "JoyButton"

class TriggerOnJoystickAxisEvent(Trigger):
    def __init__(self):
        self.name = "JoyAxis"

class TriggerOnJoystickThresholdAxisEvent(Trigger):
    def __init__(self):
        self.name = "JoyThresholdAxis"

