import os
import sys
import datetime
import time

try:
    import edmcoverlay
    _overlay = None
    _overlay = edmcoverlay.Overlay()
    print "ExTool: EDMCOverlay imported"
except ImportError:
    print "ExTool: EDMCOverlay not imported but that is ok"
    


DEFAULT_OVERLAY_MESSAGE_DURATION = 4

def get_display_ttl():
    try:
        return int(OVERLAY_MESSAGE_DURATION.get())
    except:
        return DEFAULT_OVERLAY_MESSAGE_DURATION


time.sleep(2)
HEADER = 380
INFO = 420
DETAIL1 = INFO + 25
DETAIL2 = DETAIL1 + 25
DETAIL3 = DETAIL2 + 25

def display(text, row=HEADER, col=80, color="yellow", size="large"):
    try:
        _overlay.send_message("extool_{}_{}".format(row, col),
                              text,
                              color,
                              col, row, ttl=get_display_ttl(), size=size)
    except:
        #This is going to fail if EDMCOverlay is missing but we don't care
        pass


def header(text):
    display(text, row=HEADER, size="normal")


def notify(text):
    display(text, row=INFO, color="#00ff00", col=95)


def warn(text):
    display(text, row=INFO, color="red", col=95)


def info(line1, line2=None, line3=None):
    if line1:
        display(line1, row=DETAIL1, col=95, size="normal")
    if line2:
        display(line2, row=DETAIL2, col=95, size="normal")
    if line3:
        display(line3, row=DETAIL3, col=95, size="normal")
