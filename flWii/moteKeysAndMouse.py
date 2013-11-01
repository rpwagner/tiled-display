import time, sys, os, types
from moteX11 import MoteX11

import Xlib
import Xlib.XK
from Xlib.ext import xtest
from Xlib import X

special_X_keysyms = {
    ' ' : "space",
    '\t' : "Tab",
    '\n' : "Return",  # for some reason this needs to be cr, not lf
    '\r' : "Return",
    '\e' : "Escape",
    '!' : "exclam",
    '#' : "numbersign",
    '%' : "percent",
    '$' : "dollar",
    '&' : "ampersand",
    '"' : "quotedbl",
    '\'' : "apostrophe",
    '(' : "parenleft",
    ')' : "parenright",
    '*' : "asterisk",
    '=' : "equal",
    '+' : "plus",
    ',' : "comma",
    '-' : "minus",
    '.' : "period",
    '/' : "slash",
    ':' : "colon",
    ';' : "semicolon",
    '<' : "less",
    '>' : "greater",
    '?' : "question",
    '@' : "at",
    '[' : "bracketleft",
    ']' : "bracketright",
    '\\' : "backslash",
    '^' : "asciicircum",
    '_' : "underscore",
    '`' : "grave",
    '{' : "braceleft",
    '|' : "bar",
    '}' : "braceright",
    '~' : "asciitilde"
    }

class MoteX11WithKeysAndMouse (MoteX11):
    def __init__(self):
        MoteX11.__init__(self)

    # Help with X11 key code from: http://shallowsky.com/software/crikey/pykey-0.1

    def get_keysym(self, ch) :
        keysym = Xlib.XK.string_to_keysym(ch)
        if keysym == 0 :
            # Unfortunately, although this works to get the correct keysym
            # i.e. keysym for '#' is returned as "numbersign"
            # the subsequent display.keysym_to_keycode("numbersign") is 0.
            keysym = Xlib.XK.string_to_keysym(special_X_keysyms[ch])

        return keysym


    def is_shifted(self, ch) :
        if ch.isupper() :
            return True
        if "~!@#$%^&*()_+{}|:\"<>?".find(ch) >= 0 :
            return True
        return False

    def char_to_keycode(self, ch) :
        keysym = self.get_keysym(ch)
        keycode = self.display.keysym_to_keycode(keysym)
        if keycode == 0 :
            print "Sorry, can't map", ch

        if (self.is_shifted(ch)) :
            shift_mask = Xlib.X.ShiftMask
        else :
            shift_mask = 0

        return keycode, shift_mask

    def sendKeyPress(self, key):
        #xtest.fake_input(self.display.screen().root, X.KeyPress, ord(key))
        os.system("xdotool keydown %s" % key )
        """
        keycode, shift_mask = self.char_to_keycode(key)
        window = self.display.get_input_focus()._data["focus"];
        event = Xlib.protocol.event.KeyPress(
            time = int(time.time()),
            root = self.display.screen().root,
            window = window,
            same_screen = 0, child = Xlib.X.NONE,
            root_x = 0, root_y = 0, event_x = 0, event_y = 0,
            state = shift_mask,
            detail = keycode
            )
        window.send_event(event, propagate = True)
        """

    def sendKeyRelease(self, key):
        #fake_input(self, event_type, detail=0, time=0, root=0, x=0, y=0)
        #xtest.fake_input(self.display.screen().root, X.KeyRelease, ord(key))
        os.system("xdotool keyup %s" % key )
        """
        keycode, shift_mask = self.char_to_keycode(key)
        window = self.display.get_input_focus()._data["focus"];
        event = Xlib.protocol.event.KeyRelease(
            time = int(time.time()),
            root = self.display.screen().root,
            window = window,
            same_screen = 0, child = Xlib.X.NONE,
            root_x = 0, root_y = 0, event_x = 0, event_y = 0,
            state = shift_mask,
            detail = keycode
            )
        window.send_event(event, propagate = True)
        """

    def sendStringPressAndRelease(self, strng):
        for ch in strng:
            keycode, shift_mask = self.char_to_keycode(ch)
            window = self.display.get_input_focus()._data["focus"];
            event = Xlib.protocol.event.KeyPress(
                time = int(time.time()),
                root = self.display.screen().root,
                window = window,
                same_screen = 0, child = Xlib.X.NONE,
                root_x = 0, root_y = 0, event_x = 0, event_y = 0,
                state = shift_mask,
                detail = keycode
                )
            window.send_event(event, propagate = True)
            event = Xlib.protocol.event.KeyRelease(
                time = int(time.time()),
                root = self.display.screen().root,
                window = window,
                same_screen = 0, child = Xlib.X.NONE,
                root_x = 0, root_y = 0, event_x = 0, event_y = 0,
                state = shift_mask,
                detail = keycode
                )
            window.send_event(event, propagate = True)

    def sendMouseButton(self, buttonIndex, isDown):
        if buttonIndex < 1:
            buttonIndex = 1
        if isDown:
            xtest.fake_input(self.display.screen().root, X.ButtonPress, detail=buttonIndex)
            #os.system("xdotool mousedown 1" )
        else:
            xtest.fake_input(self.display.screen().root, X.ButtonRelease, detail=buttonIndex)
            #os.system("xdotool mouseup 1")
        self.display.sync()


class MoteKeys:
    def __init__(self, connectedMote, moteX11, buttonMappings=None):
        self.mote = connectedMote
        self.moteX11 = moteX11
        if buttonMappings == None:
            self.buttonMappings = {}
        else:
            self.buttonMappings = buttonMappings

    def executeAction(self, action, isDown):
        if type(action) in [type([]), types.TupleType]:  # just do a key response
            for a in action:
                self.executeAction(a)
        elif type(action) in [type(""), type(1)]: # just do a key response
            if action.lower().startswith("mousebutton"): # handle mouse buttons
                buttonIndex = int(action.lower().strip("mousebutton"))
                self.moteX11.sendMouseButton(buttonIndex, isDown)
            #self.moteX11.sendStringPressAndRelease(action)
            elif isDown:  # normal keys (not mouse buttons)
                print "executing down action:", action
                self.moteX11.sendKeyPress(action)
            else:
                print "executing up action:", action
                self.moteX11.sendKeyRelease(action)
            print action
        else:  # assume function
            action()

    def processAndUpdateKeys(self):
        events =  self.mote.extractButtonEvents()
        for event in events:
            #print "comparing:", event, event[0][0], type(event[0][0]), "a" == event[0][0], self.buttonMappings
            if event[0] in self.buttonMappings:
                action = self.buttonMappings[event[0]]
                isDown = event[1]
                # print "Executing action:", action
                self.executeAction(action, isDown)
        if len(events) != 0:
            print events


