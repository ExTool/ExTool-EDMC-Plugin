import time
import sys

if sys.platform !=  'darwin':
    raise Exception('The key_osx module should only be loaded on an OS X system.')

try:
    import Quartz
except:
    assert False, "You must first install pyobjc-core and pyobjc"
import AppKit

# Functions

VK_F10 = 0x6d #kVK_F10

def PressKey(hexKeyCode):
    event = Quartz.CGEventCreateKeyboardEvent(None, hexKeyCode, True)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)
    time.sleep(0.01)

def ReleaseKey(hexKeyCode):
    event = Quartz.CGEventCreateKeyboardEvent(None, hexKeyCode, False)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)
    time.sleep(0.01)

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
