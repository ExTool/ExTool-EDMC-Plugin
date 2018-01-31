# -*- encoding: utf-8 -*-

import sys
import datetime
import time
import requests
import os
import key
from winsound import *
#from PriorityQueue import Queue
import Queue as Q
from threading import Thread

import Tkinter as tk
import myNotebook as nb
from ttkHyperlinkLabel import HyperlinkLabel

from config import config
import plug

this = sys.modules[__name__]
this.session = requests.Session()
this.queue = Q.PriorityQueue()
this.SCqueue = Q.Queue()
this.cmdr_name = None

_TIMEOUT = 20
# msdn.microsoft.com/en-us/library/dd375731
VK_TAB  = 0x09
VK_MENU = 0x12
VK_F10 = 0x79

this.time_lastsend = time.time() - 60
this.delay = 10
this.trspdr_delay = 10000

this.SCmode = False
this.SRVmode = False
this.landed = False
this.droped = []

this.system_name = None
this.body_name = None

this.nearloc = {
   'Latitude' : None,
   'Longitude' : None,
   'Time' : None
}
this.nearloc = dict(this.nearloc)

#this.SCnoalt = ""
this.altitude = 0
this.trySC = False
this.ntrySC = 0
this.SCnocoord = 0

this.url_website = "http://elite.laulhere.com/ExTool/"
this.version = "0.8.6.1"
this.update = True
this.update_version = None
this.relog = False

this.altiToggle = "#ExTool ALT"
this.trspdrToggle = "#ExTool TOGGLE"
this.delscToggle = "#ExTool DELSC"
this.ndelsc = 0
this.setdestToggle = "#ExTool DEST"
this.savepointToggle = "#ExTool SAVE"
this.delpointToggle = "#ExTool DEL"

this.label = tk.Label()
this.trspdr_online = False
#if(config.get("ExTool_TrspdrToggle")==None):
#   config.set("ExTool_TrspdrToggle", "#ExTool TOGGLE")
#if(config.get("ExTool_On")==None):
#   config.set("ExTool_On", "#ExTool ON")
#if(config.get("ExTool_DelSC")==None):
#   config.set("ExTool_DelSC", "#ExTool DELSC")
if(config.get("ExTool_SCSound")==None):
   config.set("ExTool_SCSound", "1")
if(config.get("ExTool_TrspdrSound")==None):
   config.set("ExTool_TrspdrSound", "1")
#if(config.get("ExTool_AltiConf")==None):
#   config.set("ExTool_AltiConf", "#ExTool A")
#if(config.get("ExTool_Altitude")==None):
#   config.set("ExTool_Altitude", "0")
if(config.get("ExTool_AltiSound")==None):
   config.set("ExTool_AltiSound", "1")
if(config.get("ExTool_DestSound")==None):
   config.set("ExTool_DestSound", "1")
if(config.get("ExTool_DeleteAutoScreen")==None):
   config.set("ExTool_DeleteAutoScreen", "1")

def plugin_start():
   """
   Load ExTool plugin into EDMC
   """
   
   this.apikey = tk.StringVar(value=config.get("ExTool_APIKey"))
   #this.autoupdate = tk.StringVar(value=config.get("Autoupdate"))
   #this.disablescans = tk.StringVar(value=config.get("ExTool_DisableScans"))
   this.scsound = tk.StringVar(value=config.get("ExTool_SCSound"))
   #this.alticonf = tk.StringVar(value=config.get("ExTool_AltiConf"))
   this.altisound = tk.StringVar(value=config.get("ExTool_AltiSound"))
   #this.altitude = tk.StringVar(value=config.get("ExTool_Altitude"))
   
   this.scdir = tk.StringVar(value=config.get("ExTool_SCDIR"))
   this.deleteautoscreen = tk.StringVar(value=config.get("ExTool_DeleteAutoScreen"))
   this.deletescreen = tk.StringVar(value=config.get("ExTool_DeleteScreen"))
   
   #this.trspdr_toggle = tk.StringVar(value=config.get("ExTool_TrspdrToggle"))
   this.trspdrsound = tk.StringVar(value=config.get("ExTool_TrspdrSound"))
   this.destsound = tk.StringVar(value=config.get("ExTool_DestSound"))

   this.debug = tk.StringVar(value=config.get("ExTool_Debug"))
   #this.extool_on = tk.StringVar(value=config.get("ExTool_On"))
   #this.extool_off = tk.StringVar(value=config.get("ExTool_Off"))
   #this.delsc_toggle = tk.StringVar(value=config.get("ExTool_DelSC"))

   this.thread = Thread(target = worker, name = 'ExTool worker')
   this.thread.daemon = True
   this.thread.start()
   
   check_version()
   
   print("ExTool v"+this.version+" loaded!")
   
   return "ExTool"

def plugin_stop():
   this.queue.put(None)
   this.thread.join()
   this.thread = None
   #print "Farewell cruel world!"

def plugin_prefs(parent, cmdr, is_beta):

   PADX = 10
   BUTTONX = 12
   PADY = 2
   
   frame = nb.Frame(parent)
   frame.columnconfigure(1, weight=1)
   nb.Label(frame, text="Welcome to ExTool v"+this.version+" settings").grid(padx = PADX, pady = PADY, sticky=tk.W)
   #nb.Checkbutton(frame, text="Automatic update", variable=this.autoupdate).grid(padx = 10, pady = 2, sticky=tk.W)

   #disablescan_checkbox = nb.Checkbutton(frame, text="Disable scans data", variable=this.disablescans)
   #disablescan_checkbox.grid(padx = PADX, pady = PADY, sticky=tk.W)

   apikey_label = nb.Label(frame, text="API Key :")
   apikey_label.grid(row=11, padx=PADX, sticky=tk.W)
   apikey_entry = nb.Entry(frame, textvariable=this.apikey)
   apikey_entry.grid(row=11, column=1, padx=PADX, pady=PADY, sticky=tk.EW)
   
   nb.Label(frame).grid(sticky=tk.W)
   scsound_checkbox = nb.Checkbutton(frame, text="Play a sound for each screenshot", variable=this.scsound)
   scsound_checkbox.grid(columnspan=2, padx = BUTTONX, pady = PADY, sticky=tk.W)

   altisound_checkbox = nb.Checkbutton(frame, text="Altitude configuration sound", variable=this.altisound)
   altisound_checkbox.grid(columnspan=2, padx = BUTTONX, pady = PADY, sticky=tk.W)
   
   #altitude_label = nb.Label(frame, text="Altitude in km (between 0 and 200) :")
   #altitude_label.grid(row=11, padx=PADX, sticky=tk.W)
   #altitude_entry = nb.Entry(frame, textvariable=this.altitude)
   #altitude_entry.grid(row=11, column=1, padx=PADX, pady=PADY, sticky=tk.EW)
   
   #alticonf_label = nb.Label(frame, text="Altitude configuration text :")
   #alticonf_label.grid(row=12, padx=PADX, sticky=tk.W)
   #alticonf_entry = nb.Entry(frame, textvariable=this.alticonf)
   #alticonf_entry.grid(row=12, column=1, padx=PADX, pady=PADY, sticky=tk.EW)

   nb.Label(frame).grid(sticky=tk.W)
   delautoscreenshot_checkbox = nb.Checkbutton(frame, text="Delete screenshot taken by ExTool", variable=this.deleteautoscreen)
   delautoscreenshot_checkbox.grid(columnspan=2, padx = BUTTONX, pady = PADY, sticky=tk.W)
   delscreenshot_checkbox = nb.Checkbutton(frame, text="Delete screenshot taken manually (with F10 and used by ExTool)", variable=this.deletescreen)
   delscreenshot_checkbox.grid(columnspan=2, padx = BUTTONX, pady = PADY, sticky=tk.W)
   
   scdir_label = nb.Label(frame, text="Screenshot Directory :")
   scdir_label.grid(row=18, padx=PADX, sticky=tk.W)
   scdir_entry = nb.Entry(frame, textvariable=this.scdir)
   scdir_entry.grid(row=18, column=1, padx=PADX, pady=PADY, sticky=tk.EW)

   #delscdir_label = nb.Label(frame, text="Delete screenshot toggle :")
   #delscdir_label.grid(row=16, padx=PADX, sticky=tk.W)
   #delscdir_entry = nb.Entry(frame, textvariable=this.delsc_toggle)
   #delscdir_entry.grid(row=16, column=1, padx=PADX, pady=PADY, sticky=tk.EW)

   nb.Label(frame).grid(sticky=tk.W)
   trspdrsound_checkbox = nb.Checkbutton(frame, text="Play a sound when activating/deactivating transponder", variable=this.trspdrsound)
   trspdrsound_checkbox.grid(columnspan=2, padx = BUTTONX, pady = PADY, sticky=tk.W)
   
   #trspdrtoggle_label = nb.Label(frame, text="Transponder des/activation toggle :")
   #trspdrtoggle_label.grid(row=19, padx=PADX, sticky=tk.W)
   #trspdrtoggle_entry = nb.Entry(frame, textvariable=this.trspdr_toggle)
   #trspdrtoggle_entry.grid(row=19, column=1, padx=PADX, pady=PADY, sticky=tk.EW)

   #trspdroff_label = nb.Label(frame, text="Transponder deactivation text :")
   #trspdroff_label.grid(row=19, padx=PADX, sticky=tk.W)
   #trspdroff_entry = nb.Entry(frame, textvariable=this.trspdr_off)
   #trspdroff_entry.grid(row=19, column=1, padx=PADX, pady=PADY, sticky=tk.EW)

   destsound_checkbox = nb.Checkbutton(frame, text="Play a sound when destination is set", variable=this.destsound)
   destsound_checkbox.grid(columnspan=2, padx = BUTTONX, pady = PADY, sticky=tk.W)

   nb.Label(frame).grid(sticky=tk.W)
   debug_checkbox = nb.Checkbutton(frame, text="Debug Mode", variable=this.debug)
   debug_checkbox.grid(columnspan=2, padx = BUTTONX, pady = PADY, sticky=tk.W)
   
   return frame

def prefs_changed(cmdr, is_beta):
   #config.set('Autoupdate', this.autoupdate.get())	# Store new value in config
   #config.set("ExTool_DisableScans", this.disablescans.get())
   
   config.set("ExTool_APIKey", this.apikey.get())
   config.set("ExTool_SCSound", this.scsound.get())
   #config.set("ExTool_AltiConf", this.alticonf.get())
   config.set("ExTool_AltiSound", this.altisound.get())
##   try :
##      isnum = int(this.altitude.get())
##      if(isnum>=0 and isnum<=200):
##         config.set("ExTool_Altitude", this.altitude.get())
##      else:
##         int("A")
##   except :
##      config.set("ExTool_Altitude", "0")
##      this.altitude = tk.StringVar(value=config.get("ExTool_Altitude"))
   
   config.set("ExTool_SCDIR", this.scdir.get())
   config.set("ExTool_DeleteAutoScreen", this.deleteautoscreen.get())
   config.set("ExTool_DeleteScreen", this.deletescreen.get())
   #config.set("ExTool_DelSC", this.delsc_toggle.get())
   
   #config.set("ExTool_TrspdrOn", this.trspdr_on.get())
   #config.set("ExTool_TrspdrOff", this.trspdr_off.get())
   #config.set("ExTool_TrspdrToggle", this.trspdr_toggle.get())
   config.set("ExTool_TrspdrSound", this.trspdrsound.get())
   config.set("ExTool_DestSound", this.destsound.get())

   config.set("ExTool_Debug", this.debug.get())

def plugin_app(parent):
   this.parent = parent
   this.frame = tk.Frame(parent)
   this.frame.columnconfigure(2, weight=1)
   this.label = tk.Label(this.frame, text="ExTool:   ")
   
   #this.status1 = tk.Label(this.frame, anchor=tk.W, text="")
   this.status = HyperlinkLabel(this.frame, anchor=tk.W, text="", popup_copy = True)
   this.bearing_status = tk.Label(this.frame, anchor=tk.W, text="")
   this.bearing = False

   this.label.grid(row = 0, column = 0, sticky=tk.W)
   this.status.grid(row = 0, column = 1, sticky=tk.W)
   this.bearing_status.grid(row = 1, column = 0, columnspan=2, sticky=tk.W)

   #this.info = False
   #this.status1.grid_remove()
   #this.infoURL = False
   #this.status2.grid_remove()
   this.bearing = False
   this.bearing_status.grid_remove()
   
   if this.update:
      updateInfo("v"+this.version+" - Need to relog into Elite Dangerous", False)
      #this.status2.grid_remove()
      #this.status1 = tk.Label(this.frame, anchor=tk.W, text="v"+this.version+" - Need to relog into Elite Dangerous")
   else:
      updateInfoURL("Need an update to v"+this.update_version, this.url_website+"EDMC/latest_ExTool.zip")
      #this.status1.grid_remove()
      #this.status2 = HyperlinkLabel(this.frame, url = this.url_website+"EDMC/latest_ExTool.zip", popup_copy = True)
      #this.status2["text"] = "Need an update to v"+this.update_version
   
   return this.frame

def updateInfo(msg, withTime = True):
   #this.status["text"] = ""
   #this.status.grid_remove()
   #this.status = tk.Label(this.frame, anchor=tk.W)
   #if not this.info:
   #   this.status2.grid_remove()
   #   this.infoURL = False
   #   this.status1.grid()
   #   this.info = True
   this.status["url"] = None
   if withTime:
      this.status["text"] = datetime.datetime.now().strftime("%H:%M") + " - " + msg
   else:
      this.status["text"] = msg
   #this.status.grid(row = 0, column = 1, sticky=tk.W)
   
   if(this.debug.get()=="1"):
      print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "updateInfo = {}".format(msg)

def updateInfoURL(msg, url):
   #this.status["text"] = ""
   #this.status.grid_remove()
   #this.status = HyperlinkLabel(this.frame, popup_copy = True)
   #this.status2.grid(row = 0, column = 1, sticky=tk.W)
   #if not this.infoURL:
   #   this.status1.grid_remove()
   #   this.info = False
   #   this.status2.grid()
   #   this.infoURL = True
   this.status["text"] = datetime.datetime.now().strftime("%H:%M") + " - " + msg
   this.status["url"] = url
   #this.status.grid(row = 0, column = 1, sticky=tk.W)
   
   if(this.debug.get()=="1"):
      print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "updateInfoURL = {} ({})".format(msg, url)

def updateBearing(latitude, longitude, bearing = None, distance = None):
   #this.status["text"] = ""
   #this.status.grid_remove()
   #this.status = tk.Label(this.frame, anchor=tk.W)
   if not this.bearing:
      this.bearing = True
      this.bearing_status.grid()
   if(bearing is None):
      this.bearing_status["text"] = "   DEST ({},{}) : Waiting for a screenshot...".format(latitude, longitude)
   else:
      this.bearing_status["text"] = "   DEST ({},{}) : BEARING {} / DIST {} km".format(latitude, longitude, bearing, distance)
   #this.status.grid(row = 0, column = 1, sticky=tk.W)
   
   if(this.debug.get()=="1"):
      print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "updateBearing = {} / {}".format(bearing, distance)

def journal_entry(cmdr, is_beta, system, station, entry, state):
   if this.update:
      if entry['event'] == 'Location':
         this.relog = True
         this.SCmode = False
         update_altitude(0)
         transponder(False)
         if ('StarSystem' in entry):
            this.system_name = entry['StarSystem']
         if ('Body' in entry):
            this.body_name = entry['Body']
         if ('Latitude' in entry) and ('Longitude' in entry):
            this.landed = True
            timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
            update_nearloc(entry['Latitude'], entry['Longitude'], timestamp)
            send_data(cmdr, this.system_name, this.body_name, entry['Latitude'], entry['Longitude'], entry['event'], timestamp)
         updateInfo("v"+this.version+" - Ready", False)

      if entry['event'] == 'StartUp':
            transponder(False)
            update_altitude(0)
            this.SCmode = False
            this.SRVmode = False
            this.landed = False
            this.droped = []
            this.relog = False
            updateInfo("v"+this.version+" - Need to relog into Elite Dangerous", False)
            
      if entry['event'] == 'ShutDown':
            transponder(False)
            update_altitude(0)
            this.SCmode = False
            this.SRVmode = False
            this.landed = False
            this.droped = []
            this.relog = False
            updateInfo("v"+this.version+" - Need to relog into Elite Dangerous", False)

      if this.relog:
         if entry['event'] == 'SendText':
            if entry['Message'][:len(this.delscToggle)].lower() == this.delscToggle.lower():
               if(len(entry['Message'][len(this.delscToggle):])>0):
                  try:
                     this.ndelsc = int(entry['Message'][len(this.delscToggle):])
                  except:
                     this.ndelsc = 0
               else:
                  if this.deletescreen.get()=="1":
                     this.deletescreen = tk.StringVar(value="0")
                  else:
                     this.deletescreen = tk.StringVar(value="1")

            if entry['Message'].lower() == this.trspdrToggle.lower():
               if this.trspdr_online:
                  transponder(False)
               else:
                  transponder(True)

            if entry['Message'][:len(this.altiToggle)].lower() == this.altiToggle.lower():
               update_altitude(entry['Message'][len(this.altiToggle):])
                  
            if entry['Message'][:len(this.setdestToggle)].lower() == this.setdestToggle.lower():
               try:
                  coord_dest = entry['Message'][len(this.setdestToggle)+1:].strip("()").split(",")
                  latitude = coord_dest[0]
                  longitude = coord_dest[1]
                  if this.altisound.get()=="1":
                     soundfile = os.path.dirname(this.__file__)+'\\'+'new_destination.wav'
                     this.queue.put((2,'playsound', soundfile, None))
                  updateInfo("Set destination to ({},{})".format(latitude, longitude))
                  timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
                  queueScreenshot("DEST", timestamp)
                  send_destination(cmdr, 1, latitude, longitude)
                  updateBearing(latitude,longitude)
               except:
                  updateInfo("Unset destination")
                  send_destination(cmdr, 0, 0, 0)
                  if this.bearing:
                     this.bearing = False
                     this.bearing_status.grid_remove()

            if entry['Message'][:len(this.savepointToggle)].lower() == this.savepointToggle.lower():
               timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
               queueScreenshot("SAVE", timestamp)
               send_savepoint(cmdr, entry['Message'][len(this.savepointToggle)+1:], timestamp)
               
            if entry['Message'][:len(this.delpointToggle)].lower() == this.delpointToggle.lower():
               name_point = entry['Message'][len(this.delpointToggle)+1:]
               send_delpoint(cmdr, name_point)

            #if entry['Message'].lower() == "#ExTool BT":
            #   timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
            #   queueScreenshot("SAVE", timestamp)
            #   send_savepoint(cmdr, "Brain Trees", timestamp)
               
            #if entry['Message'].lower() == "#ExTool VOLCA":
            #   timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
            #   queueScreenshot("SAVE", timestamp)
            #   send_savepoint(cmdr, "Volcanism", timestamp)
               
         if entry['event'] == 'Screenshot':
            if ('System' in entry):
               this.system_name = entry['System']
            if ('Body' in entry):
               this.body_name = entry['Body']
            if ('Latitude' in entry) and ('Longitude' in entry):
               this.SCnocoord = 0
               timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
               update_nearloc(entry['Latitude'], entry['Longitude'], timestamp)
               #if(not this.trspdr_online and this.trySC):
               #   this.trySC = False
               #else:
               if('Altitude' in entry) and ('Heading' in entry):
                  send_data(cmdr, entry['System'], entry['Body'], entry['Latitude'], entry['Longitude'], entry['event'], timestamp, entry['Altitude'], entry['Heading'])
               else:
                  send_data(cmdr, entry['System'], entry['Body'], entry['Latitude'], entry['Longitude'], entry['event'], timestamp)
               deleteScreenshot(entry['Filename'], this.trySC)
               if(this.trySC):
                  this.trySC = False
               if(this.scsound.get()=="1") :
                  soundfile = 'snd_good.wav'
                  this.queue.put((2,'playsound', soundfile, None))
            else:
               if(this.trySC):
                  this.SCnocoord += 1
                  deleteScreenshot(entry['Filename'], this.trySC)
                  this.trySC = False
                  if(this.trspdr_online and this.trspdr_count==1):
                     this.SCnocoord = 4
                  if(this.SCnocoord<5):
                     this.trspdr_delay = 10000
                     if(this.scsound.get()=="1") :
                        soundfile = 'snd_bad.wav'
                        this.queue.put((2,'playsound', soundfile, None))
                  else:
                     this.SCnocoord = 0
                     update_altitude(0)
                     transponder(False)
               

         if entry['event'] == 'Touchdown':
            if entry['PlayerControlled']:
               if ('Latitude' in entry) and ('Longitude' in entry):
                  update_altitude(0)
                  transponder(False)
                  this.landed = True
                  timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
                  update_nearloc(entry['Latitude'], entry['Longitude'], timestamp)
                  send_data(cmdr, this.system_name, this.body_name,  entry['Latitude'], entry['Longitude'], entry['event'], timestamp)
            else:
               this.SRVmode = True
         if entry['event'] == 'Liftoff':
            if ('Latitude' in entry) and ('Longitude' in entry):
               if entry['PlayerControlled']:
                  this.landed = False
                  this.droped = []
                  timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
                  send_data(cmdr, this.system_name, this.body_name, entry['Latitude'], entry['Longitude'], entry['event'], timestamp)

         if entry['event'] == 'StartJump':
            this.SCmode = True
            if entry['JumpType'] == 'Hyperspace':
               update_altitude(0)
               transponder(False)
               this.system_name = None
               this.body_name = None
         
         if entry['event'] == 'SupercruiseEntry':
            this.SCmode = True
            this.system_name = entry['StarSystem']
            this.body_name = None
         if entry['event'] == 'SupercruiseExit':
            this.SCmode = False
            this.system_name = entry['StarSystem']
            if ('Body' in entry):
               this.body_name = entry['Body']
         
         if entry['event'] == 'LaunchSRV':
            this.SRVmode = True
         if entry['event'] == 'DockSRV':
            this.SRVmode = False

         if entry['event'] == 'CollectCargo':
            if this.landed:
               if entry['Type'] in this.droped:
                  this.droped.remove(entry['Type'])
               else:
                  timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
                  queueScreenshot("MAT", timestamp)
                  send_material(cmdr, "Cargo", entry['Type'], 1, timestamp)
         if entry['event'] == 'EjectCargo':
            if this.landed:
               for x in range(0, entry['Count']):
                  this.droped.append(entry['Type'])
         if entry['event'] == 'MaterialCollected':
            if this.landed:
               timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
               queueScreenshot("MAT", timestamp)
               send_material(cmdr, entry['Category'], entry['Name'], entry['Count'], timestamp)
         if entry['event'] == 'DatalinkScan':
            if this.landed:
               timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
               queueScreenshot("SCAN", timestamp)
               send_datalink(cmdr, entry['Message'], timestamp)
         if entry['event'] == 'DatalinkVoucher':
            if this.landed:
               timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
               queueScreenshot("SCAN", timestamp)
               send_datavoucher(cmdr, entry['Reward'], entry['VictimFaction'], entry['PayeeFaction'], timestamp)
         if entry['event'] == 'DataScanned':
            if this.landed:
               timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
               queueScreenshot("SCAN", timestamp)
               send_datascan(cmdr, entry['Type'], timestamp)

def update_altitude(altitude):
   if(this.debug.get()=="1"):
      print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "try update altitude from {} to {}".format(this.altitude, altitude)
   if this.landed:
      return
   try:
      altitest = int(altitude)
      if(this.altitude!=altitest):
         if altitest>=0 and altitest<=200 :
            if this.altisound.get()=="1":
               soundfile = os.path.dirname(this.__file__)+'\\'+'new_altitude.wav'
               this.queue.put((2,'playsound', soundfile, None))
            updateInfo("Set altitude to {}km".format(altitest))
            this.altitude = altitest
            if(this.debug.get()=="1"):
               print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "update altitude to {}km".format(altitest)
   except ValueError:
      this.status["text"] = "ERROR : altitude must be an integer between 0 and 200"

def update_nearloc(latitude, longitude, timestamp):
   if(this.debug.get()=="1"):
      print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "update nearloc to ({},{}) at {}".format(latitude,longitude,timestamp)
   this.nearloc['Latitude'] = latitude
   this.nearloc['Longitude'] = longitude
   this.nearloc['Time'] = timestamp

def send_data(cmdr, system, body, latitude, longitude, event, timestamp, altitude = None, heading = None):
   #if (time.time()>this.time_lastsend+this.delay):
   
   url = this.url_website+"send_data"
   
   if(event=='Screenshot') :
      if( this.SCqueue.empty() ):
         SCtype = ""
      else:
         (SCtype) = this.SCqueue.get(False)
      
      if(SCtype==""):
         if(this.landed):
            event += ' L'
         #elif(this.altitude.get()=="0"):
         elif(this.altitude==0):
            event += ' NA'
         elif(this.SCmode):
            event += ' SC'
      else:
         event += ' '+SCtype

   if altitude is None:
      if(event=='Screenshot' or event=='Screenshot SC') :
         #altitude = this.altitude.get()
         altitude = this.altitude
      else:
         altitude = "0"

   if(this.trspdr_online):
      trspdr_status = "1"
   else:
      trspdr_status = "0"

   payload = {
      'system' : system,
      'body' : body,
      'latitude' : '{}'.format(latitude),
      'longitude' : '{}'.format(longitude),
      'altitude' : '{}'.format(altitude),
      'heading' : '{}'.format(heading),
      'trspdr' : trspdr_status,
      'event' : event,
      'timestamp' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
   }

   if(event=='Screenshot' or event=='Screenshot SC') :
      new_text = "ALT {}km - {}".format(altitude, body)
   elif(event=='Screenshot NA') :
      new_text = "NO ALT - {}".format(body)
   elif(event=='Screenshot L') :
      new_text = "Ground - {}".format(body)
   elif(event=='Screenshot MAT') :
      new_text = "Material - {}".format(body)
   elif(event=='Screenshot SCAN') :
      new_text = "Scan - {}".format(body)
   elif(event=='Screenshot SAVE') :
      new_text = "Save - {}".format(body)
   elif(event=='Screenshot DEST') :
      new_text = "Destination - {}".format(body)
   else:
      new_text = event + " - {}".format(body)

   new_url = this.url_website+"index.php?mode=3d&planet={}&goto={},{}".format(body, latitude, longitude)
   updateInfoURL(new_text, new_url)

   if(this.trspdr_online and (event=='Screenshot' or event=='Screenshot NA' or event=='Screenshot SC')) :
      call(cmdr, 'coords', payload, callback=update_velocity)
   else:
      call(cmdr, 'coords', payload)

   #call(cmdr, 'coords', payload)
   #else :
   #   new_text = "Wait {} seconds before resent...".format(round(this.time_lastsend+this.delay-time.time(), 2))
   #   updateInfo(new_text)

def send_material(cmdr, category, name, count, timestamp):
   url = this.url_website+"send_data"
   payload = {
      'system' : this.system_name,
      'body' : this.body_name,
      'category' : category,
      'name' : name,
      'count' : '%d' % count,
      'timestamp' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
   }
   call(cmdr, 'materials', payload)

def send_datalink(cmdr, message, timestamp):
   url = this.url_website+"send_data"
   payload = {
      'system' : this.system_name,
      'body' : this.body_name,
      'message' : message,
      'timestamp' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
   }
   call(cmdr, 'datalink', payload)

def send_datavoucher(cmdr, reward, victim, payee, timestamp):
   url = this.url_website+"send_data"
   payload = {
      'system' : this.system_name,
      'body' : this.body_name,
      'reward' : '%d' % reward,
      'victim' : victim,
      'payee' : payee,
      'timestamp' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
   }
   call(cmdr, 'datavoucher', payload)

def send_datascan(cmdr, typescan, timestamp):
   url = this.url_website+"send_data"
   payload = {
      'system' : this.system_name,
      'body' : this.body_name,
      'typescan' : typescan,
      'timestamp' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
   }
   call(cmdr, 'datascan', payload)

def send_destination(cmdr, setdest, latitude, longitude):
   url = this.url_website+"send_data"
   payload = {
      'system' : this.system_name,
      'body' : this.body_name,
      'setdest' : '%d' % setdest,
      'latitude' : '{}'.format(latitude),
      'longitude' : '{}'.format(longitude)
   }
   call(cmdr, 'destination', payload)

def send_savepoint(cmdr, name_point, timestamp):
   url = this.url_website+"send_data"
   payload = {
      'system' : this.system_name,
      'body' : this.body_name,
      'name_point' : name_point,
      'timestamp' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
   }
   call(cmdr, 'savepoint', payload)

def send_delpoint(cmdr, name_point):
   url = this.url_website+"send_data"
   payload = {
      'system' : this.system_name,
      'body' : this.body_name,
      'name_point' : name_point
   }
   call(cmdr, 'delpoint', payload)

# Worker thread
def worker():
   url = this.url_website+"send_data"
   while True:
      item = this.queue.get()
      if not item:
         return	# Closing
      else:
         (pnum, mode, data, callback) = item

      if(mode=='senddata'):
         if(data['mode']=='savepoint' or data['mode']=='datascan' or data['mode']=='datavoucher' or data['mode']=='datalink' or data['mode']=='materials'):
            data['latitude'] = '{}'.format(this.nearloc['Latitude'])
            data['longitude'] = '{}'.format(this.nearloc['Longitude'])
            timestamp = time.mktime(time.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S'))
            data['time'] = '%d' % round(this.nearloc['Time']-timestamp)

         retrying = 0
         while retrying < 3:
            try:
               r = this.session.post(url, json=data, timeout=_TIMEOUT)
               r.raise_for_status()
               reply = r.json()
               (code, msg) = reply['Status'], reply['StatusMsg']
               if code // 100 != 1:	# 1xx = OK, 2xx = fatal error
                  plug.show_error(_('Error: ExTool {MSG}').format(MSG=msg))
                  if(this.debug.get()=="1"):
                     print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "Error: ExTool {MSG}".format(MSG=msg)
                     print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "Code = {}".format(code)
                     #print datetime.datetime.now().strftime("%H:%M:%S") + " - " + data.encode('ascii', 'ignore')
               else:
                  if(code==100):
                     if ('Bearing' in reply):
                        lat_dest = reply['Latitude_Dest']
                        lon_dest = reply['Longitude_Dest']
                        bearing = reply['Bearing']
                        distance = reply['Distance']
                        updateBearing(lat_dest,lon_dest,bearing,distance)
                        #print "bearing : {}".format(bearing)
                     #else:
                        #updateBearing("","","","")
                        #if this.bearing:
                        #   print "remove bearing {}".format(this.bearing)
                        #   this.bearing = False
                        #   print "remove bearing1 {}".format(this.bearing)
                        #   this.bearing_status.grid_remove()
                        #   time.sleep(0.1)
                        #   print "remove bearing2"
                        #   this.bearing_status.update()
                  if callback:
                     callback(reply)
               break
               
            except:
               retrying += 1
         else:
            plug.show_error(_("Error: Can't connect to ExTool Server"))

      
      elif(mode=='playsound'):
         try:
            if(this.debug.get()=="1"):
               print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "playsound = {}".format(data)
            PlaySound(data, SND_FILENAME)
         except:
            plug.show_error(_("Error: Can't play sound for ExTool"))
            if(this.debug.get()=="1"):
               print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "Error: Can't play sound for ExTool"
               print datetime.datetime.now().strftime("%H:%M:%S") + " - " + data
      
      elif(mode=='takeSC'):
         try:
            if EliteInForeground():
               takeScreenshot()
               time.sleep(2)
               if(this.trySC):
                  this.trySC = False
                  this.ntrySC += 1
                  if(this.debug.get()=="1"):
                     print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "retry SC = {}".format(this.ntrySC)
                  if(this.ntrySC<10):
                     if( this.SCqueue.empty() ):
                        SCtype = ""
                     else:
                        (SCtype) = this.SCqueue.get(False)
                     queueScreenshot(SCtype, data)
                  else:
                     if(this.debug.get()=="1"):
                        print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "cancel SC = {}".format(this.ntrySC)
               else:
                  if(this.debug.get()=="1"):
                     print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "SC taken - stop retry = {}".format(this.ntrySC)
                  this.ntrySC = 0
            else:
               if(this.trySC):
                  this.trySC = False
                  this.ntrySC = 0
               if(this.debug.get()=="1"):
                  print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "takeScreenshot cancel (Elite not in foreground)"
         except:
            plug.show_error(_("Error: Can't take a screenshot for ExTool"))
            if(this.debug.get()=="1"):
               print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "Error: Can't take a screenshot for ExTool"
               print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "this.trySC = {}".format(this.trySC)

def call(cmdr, sendmode, args, callback=None):
   args = dict(args)
   args['cmdr'] = cmdr
   args['mode'] = sendmode
   args['version'] = this.version
   args['apikey'] = this.apikey.get()
   if(this.debug.get()=="1"):
      print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "call : {}".format(sendmode)
   this.queue.put((3,'senddata', args, callback))

def update_velocity(args):
   if(this.debug.get()=="1"):
      print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "TRSPDR : n={} vel={} delay={}".format(this.trspdr_count, args['Velocity'], args['TrspdrDelay']/1000)
   if(this.trspdr_count>1):
      this.trspdr_delay = max(min(args['TrspdrDelay'],100000),5000)
      if(args['TrspdrDelay'] == 0):
         transponder(False)

def check_version():
   url = this.url_website+"EDMC/version"
   rsend = this.session.get(url, verify=False)
   if rsend.content[:5] != this.version[:5]:
      this.update_version = rsend.content
      this.update = False

def transponder(status):
   if(this.debug.get()=="1"):
      print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "TRSPDR status = {}".format(status)
   if status:
      if not this.landed:
         updateInfo("Transponder activated")
         this.trspdr_online = True
         this.trspdr_delay = 10000
         this.trspdr_count = 0
         if this.trspdrsound.get()=="1":
            soundfile = os.path.dirname(this.__file__)+'\\'+'trspdr_on.wav'
            this.queue.put((2,'playsound', soundfile, None))
         transponderStart()
   else:
      if this.trspdr_online:
         this.trspdr_online = False
         updateInfo("Transponder deactivated")
         if this.trspdrsound.get()=="1":
            soundfile = os.path.dirname(this.__file__)+'\\'+'trspdr_off.wav'
            this.queue.put((2,'playsound', soundfile, None))

def transponderStart():
   if not this.trspdr_online:
      return
   if EliteInForeground():
      queueScreenshot("")
      this.label.after(this.trspdr_delay, transponderStart)
   else:
      updateInfo("StandBy Mode - Not in Elite Dangerous")
      this.label.after(5000, transponderStart)

def queueScreenshot(SCtype, timestamp = None):
##   if(this.nearloc['Time']!=None and timestamp!=None):
##      if(timestamp - this.nearloc['Time'] > 5):
##         this.queue.put((1, 'takeSC', timestamp, None))
##         this.SCqueue.put((SCtype))
##         if(this.debug.get()=="1"):
##            print "queue Screenshot : type = {}".format(SCtype)
##   else:
##   try:
##      (pnum, mode, data, callback) = this.queue.get(False)
##      if( pnum != 1 ):
##         this.queue.put((pnum, mode, data, callback))
##         this.queue.put((1, 'takeSC', timestamp, None))
##         this.SCqueue.put((SCtype))
##         if(this.debug.get()=="1"):
##            print "queue Screenshot : type = {}".format(SCtype)
##      else:
##         this.queue.put((pnum, mode, data, callback))
##         if(this.debug.get()=="1"):
##            print "skip queue Screenshot : type = {}".format(SCtype)
##   except Q.Empty:
##      this.queue.put((1, 'takeSC', timestamp, None))
##      this.SCqueue.put((SCtype))
##      if(this.debug.get()=="1"):
##         print "empty queue Screenshot : type = {}".format(SCtype)
   if(this.trySC):
      if(this.debug.get()=="1"):
         print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "skip queue Screenshot : type = {}".format(SCtype)
   else:
      if(this.nearloc['Time']!=None and timestamp!=None):
         if(timestamp - this.nearloc['Time'] > 5):
            this.trySC = True
            this.queue.put((1, 'takeSC', timestamp, None))
            this.SCqueue.put((SCtype))
            if(this.debug.get()=="1"):
               print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "queue Screenshot (last > 5s) : type = {}".format(SCtype)
         else:
            if(this.debug.get()=="1"):
               print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "skip queue Screenshot (last < 5s) : type = {}".format(SCtype)
      else:
         this.trySC = True
         this.queue.put((1, 'takeSC', timestamp, None))
         this.SCqueue.put((SCtype))
         if(this.debug.get()=="1"):
            print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "queue Screenshot : type = {}".format(SCtype)
   

def takeScreenshot():
   if this.trspdr_online and this.ntrySC==0:
      this.trspdr_count = this.trspdr_count + 1
   key.PressKey(VK_F10)   # F10
   time.sleep(0.5)
   key.ReleaseKey(VK_F10) # F10~

def deleteScreenshot(filename, autoSC):
   if this.scdir.get()!="":
      file = this.scdir.get() + '\\'+ filename[13:]
      if(autoSC):
         if(this.deleteautoscreen.get()=="1"):
            try:
               os.remove(file)
            except:
               plug.show_error(_("Error: Can't remove {FILE}".format(FILE=file)))
      else:
         if(this.deletescreen.get()=="1"):
            if(this.ndelsc==0):
               try:
                  os.remove(file)
               except:
                  plug.show_error(_("Error: Can't remove {FILE}".format(FILE=file)))
            else:
               this.ndelsc -= 1
   else:
      plug.show_error(_("Error: Screenshot directory is empty in settings"))

def EliteInForeground():
    active = key.GetForegroundWindow()
    name = key.GetWindowName(active)
    if name and name.startswith('Elite - Dangerous'):
        return True
    return False
