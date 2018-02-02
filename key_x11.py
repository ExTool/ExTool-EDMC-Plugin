import sys
import os

from Xlib.display import Display
from Xlib import X
from Xlib.ext.xtest import fake_input
import Xlib.XK

if not sys.platform.startswith('Linux'):
    raise Exception('The key_x11 module should only be loaded on a Unix system that supports X11.')

# Functions

_display = Display(os.environ['DISPLAY'])

VK_F10 = _display.keysym_to_keycode(Xlib.XK.string_to_keysym('F10'))

def PressKey(hexKeyCode):
    fake_input(_display, X.KeyPress, hexKeyCode)
    _display.sync()

def ReleaseKey(hexKeyCode):
    fake_input(_display, X.KeyRelease, hexKeyCode)
    _display.sync()
    

#def GetWindowName(h):
#    b = ctypes.create_unicode_buffer(255)
#    GetWindowText(h,b,255)
#    return b.value

#def AltTab():
#    """Press Alt+Tab and hold Alt key for 2 seconds
#    in order to see the overlay.
#    """
#    PressKey(VK_MENU)   # Alt
#    PressKey(VK_TAB)    # Tab
#    ReleaseKey(VK_TAB)  # Tab~
#    time.sleep(2)
#    ReleaseKey(VK_MENU) # Alt~

#if __name__ == "__main__":
#AltTab()
