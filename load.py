# -*- encoding: utf-8 -*-

import sys
import datetime
import time
import requests
import os
import key
import math
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
this.queue = Q.Queue()
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
this.lat_dest = None
this.lon_dest = None
this.radius = None

this.nearloc = {
   'Latitude' : None,
   'Longitude' : None,
   'Altitude' : None,
   'Heading' : None,
   'Time' : None
}
this.nearloc = dict(this.nearloc)

this.lastloc = {
   'Latitude' : None,
   'Longitude' : None,
   'Altitude' : None,
   'Heading' : None,
   'Time' : None
}
this.lastloc = dict(this.lastloc)

#this.SCnoalt = ""
#this.altitude = 0
#this.trySC = False
#this.ntrySC = 0
#this.SCnocoord = 0

this.url_website = "http://elite.laulhere.com/ExTool/"
this.version = "0.9.1"
this.update = True
this.new_version = False
this.update_version = None
#this.relog = False

#this.altiToggle = "#ExTool ALT"
this.trspdrToggle = "#ExTool TOGGLE"
this.surveyToggle = "#ExTool SURVEY"
this.delscToggle = "#ExTool DELSC"
this.ndelsc = 0
this.setdestToggle = "#ExTool DEST"
this.savepointToggle = "#ExTool SAVE"
this.delpointToggle = "#ExTool DEL"

this.label = tk.Label()
this.trspdr_online = False
this.survey_online = False
#if(config.get("ExTool_TrspdrToggle")==None):
#   config.set("ExTool_TrspdrToggle", "#ExTool TOGGLE")
#if(config.get("ExTool_On")==None):
#   config.set("ExTool_On", "#ExTool ON")
#if(config.get("ExTool_DelSC")==None):
#   config.set("ExTool_DelSC", "#ExTool DELSC")
#if(config.get("ExTool_SCSound")==None):
#   config.set("ExTool_SCSound", "1")
if(config.get("ExTool_TrspdrSound")==None):
   config.set("ExTool_TrspdrSound", "0")
if(config.get("ExTool_AutoTrspdr")==None):
   config.set("ExTool_AutoTrspdr", "1")
if(config.get("ExTool_SurveySound")==None):
   config.set("ExTool_SurveySound", "1")
if(config.get("ExTool_AutoSurvey")==None):
   config.set("ExTool_AutoSurvey", "1")
#if(config.get("ExTool_AltiConf")==None):
#   config.set("ExTool_AltiConf", "#ExTool A")
#if(config.get("ExTool_Altitude")==None):
#   config.set("ExTool_Altitude", "0")
#if(config.get("ExTool_AltiSound")==None):
#   config.set("ExTool_AltiSound", "1")
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
   #this.scsound = tk.StringVar(value=config.get("ExTool_SCSound"))
   #this.alticonf = tk.StringVar(value=config.get("ExTool_AltiConf"))
   #this.altisound = tk.StringVar(value=config.get("ExTool_AltiSound"))
   #this.altitude = tk.StringVar(value=config.get("ExTool_Altitude"))
   
   this.scdir = tk.StringVar(value=config.get("ExTool_SCDIR"))
   #this.deleteautoscreen = tk.StringVar(value=config.get("ExTool_DeleteAutoScreen"))
   this.deletescreen = tk.StringVar(value=config.get("ExTool_DeleteScreen"))
   
   #this.trspdr_toggle = tk.StringVar(value=config.get("ExTool_TrspdrToggle"))
   this.trspdrsound = tk.StringVar(value=config.get("ExTool_TrspdrSound"))
   this.autotrspdr = tk.StringVar(value=config.get("ExTool_AutoTrspdr"))
   
   this.surveysound = tk.StringVar(value=config.get("ExTool_SurveySound"))
   this.autosurvey = tk.StringVar(value=config.get("ExTool_AutoSurvey"))

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
   
   #nb.Label(frame).grid(sticky=tk.W)
   #scsound_checkbox = nb.Checkbutton(frame, text="Play a sound for each screenshot", variable=this.scsound)
   #scsound_checkbox.grid(columnspan=2, padx = BUTTONX, pady = PADY, sticky=tk.W)

   #altisound_checkbox = nb.Checkbutton(frame, text="Altitude configuration sound", variable=this.altisound)
   #altisound_checkbox.grid(columnspan=2, padx = BUTTONX, pady = PADY, sticky=tk.W)
   
   #altitude_label = nb.Label(frame, text="Altitude in km (between 0 and 200) :")
   #altitude_label.grid(row=11, padx=PADX, sticky=tk.W)
   #altitude_entry = nb.Entry(frame, textvariable=this.altitude)
   #altitude_entry.grid(row=11, column=1, padx=PADX, pady=PADY, sticky=tk.EW)
   
   #alticonf_label = nb.Label(frame, text="Altitude configuration text :")
   #alticonf_label.grid(row=12, padx=PADX, sticky=tk.W)
   #alticonf_entry = nb.Entry(frame, textvariable=this.alticonf)
   #alticonf_entry.grid(row=12, column=1, padx=PADX, pady=PADY, sticky=tk.EW)

   autotrspdr_checkbox = nb.Checkbutton(frame, text="Autoactivate transponder when you are in orbit of a landable planet", variable=this.autotrspdr)
   autotrspdr_checkbox.grid(columnspan=2, padx = BUTTONX, pady = PADY, sticky=tk.W)
   
   #autosurvey_checkbox = nb.Checkbutton(frame, text="Autoactivate survey when transponder is below 200km", variable=this.autosurvey)
   #autosurvey_checkbox.grid(columnspan=2, padx = BUTTONX, pady = PADY, sticky=tk.W)
   
   nb.Label(frame).grid(sticky=tk.W)
   #delautoscreenshot_checkbox = nb.Checkbutton(frame, text="Delete screenshot taken by ExTool", variable=this.deleteautoscreen)
   #delautoscreenshot_checkbox.grid(columnspan=2, padx = BUTTONX, pady = PADY, sticky=tk.W)
   delscreenshot_checkbox = nb.Checkbutton(frame, text="Delete screenshot taken manually (with F10 and used by ExTool)", variable=this.deletescreen)
   delscreenshot_checkbox.grid(columnspan=2, padx = BUTTONX, pady = PADY, sticky=tk.W)
   
   scdir_label = nb.Label(frame, text="Screenshot Directory :")
   scdir_label.grid(row=15, padx=PADX, sticky=tk.W)
   scdir_entry = nb.Entry(frame, textvariable=this.scdir)
   scdir_entry.grid(row=15, column=1, padx=PADX, pady=PADY, sticky=tk.EW)

   #delscdir_label = nb.Label(frame, text="Delete screenshot toggle :")
   #delscdir_label.grid(row=16, padx=PADX, sticky=tk.W)
   #delscdir_entry = nb.Entry(frame, textvariable=this.delsc_toggle)
   #delscdir_entry.grid(row=16, column=1, padx=PADX, pady=PADY, sticky=tk.EW)

   nb.Label(frame).grid(sticky=tk.W)
   trspdrsound_checkbox = nb.Checkbutton(frame, text="Play sound when using transponder", variable=this.trspdrsound)
   trspdrsound_checkbox.grid(columnspan=2, padx = BUTTONX, pady = PADY, sticky=tk.W)

   surveysound_checkbox = nb.Checkbutton(frame, text="Play sound when using survey", variable=this.surveysound)
   surveysound_checkbox.grid(columnspan=2, padx = BUTTONX, pady = PADY, sticky=tk.W)
   
   #trspdrtoggle_label = nb.Label(frame, text="Transponder des/activation toggle :")
   #trspdrtoggle_label.grid(row=19, padx=PADX, sticky=tk.W)
   #trspdrtoggle_entry = nb.Entry(frame, textvariable=this.trspdr_toggle)
   #trspdrtoggle_entry.grid(row=19, column=1, padx=PADX, pady=PADY, sticky=tk.EW)

   #trspdroff_label = nb.Label(frame, text="Transponder deactivation text :")
   #trspdroff_label.grid(row=19, padx=PADX, sticky=tk.W)
   #trspdroff_entry = nb.Entry(frame, textvariable=this.trspdr_off)
   #trspdroff_entry.grid(row=19, column=1, padx=PADX, pady=PADY, sticky=tk.EW)

   destsound_checkbox = nb.Checkbutton(frame, text="Play sound when destination is set", variable=this.destsound)
   destsound_checkbox.grid(columnspan=2, padx = BUTTONX, pady = PADY, sticky=tk.W)

   nb.Label(frame).grid(sticky=tk.W)
   debug_checkbox = nb.Checkbutton(frame, text="Debug Mode", variable=this.debug)
   debug_checkbox.grid(columnspan=2, padx = BUTTONX, pady = PADY, sticky=tk.W)
   
   return frame

def prefs_changed(cmdr, is_beta):
   #config.set('Autoupdate', this.autoupdate.get())	# Store new value in config
   #config.set("ExTool_DisableScans", this.disablescans.get())
   
   config.set("ExTool_APIKey", this.apikey.get())
   #config.set("ExTool_SCSound", this.scsound.get())
   #config.set("ExTool_AltiSound", this.altisound.get())
   config.set("ExTool_AutoTrspdr", this.autotrspdr.get())
   config.set("ExTool_TrspdrSound", this.trspdrsound.get())
   
   config.set("ExTool_AutoSurvey", this.autosurvey.get())
   config.set("ExTool_SurveySound", this.trspdrsound.get())
   
   config.set("ExTool_SCDIR", this.scdir.get())
   #config.set("ExTool_DeleteAutoScreen", this.deleteautoscreen.get())
   config.set("ExTool_DeleteScreen", this.deletescreen.get())
   
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

   this.bearing = False
   this.bearing_status.grid_remove()
   
   if this.update:
      if this.new_version:
         updateInfoURL("New version v"+this.update_version+" available", "https://github.com/ExTool/ExTool-EDMC-Plugin/releases/latest", False)
      else:
         updateInfo("v"+this.version+" - Ready", False)
      #this.status2.grid_remove()
      #this.status1 = tk.Label(this.frame, anchor=tk.W, text="v"+this.version+" - Need to relog into Elite Dangerous")
   else:
      updateInfoURL("Need an update to v"+this.update_version, "https://github.com/ExTool/ExTool-EDMC-Plugin/releases/latest", False)
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

def updateInfoURL(msg, url, withTime = True):
   #this.status["text"] = ""
   #this.status.grid_remove()
   #this.status = HyperlinkLabel(this.frame, popup_copy = True)
   #this.status2.grid(row = 0, column = 1, sticky=tk.W)
   #if not this.infoURL:
   #   this.status1.grid_remove()
   #   this.info = False
   #   this.status2.grid()
   #   this.infoURL = True
   #this.status["text"] = datetime.datetime.now().strftime("%H:%M") + " - " + msg
   if withTime:
      this.status["text"] = datetime.datetime.now().strftime("%H:%M") + " - " + msg
   else:
      this.status["text"] = msg
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

def dashboard_entry(cmdr, is_beta, entry):
   if this.update:
      timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
      this.landed = entry['Flags'] & 1<<1 and True or False
      this.SCmode = entry['Flags'] & 1<<4 and True or False
      this.SRVmode = entry['Flags'] & 1<<26 and True or False
      this.landed = this.landed or this.SRVmode
      #print "LatLon = {}".format(entry['Flags'] & 1<<21 and True or False)
      #print entry
      if(entry['Flags'] & 1<<21 and True or False):
         if('Altitude' in entry):
            update_nearloc(entry['Latitude'], entry['Longitude'], round(entry['Altitude'] / 1000.,3), entry['Heading'], timestamp)
         else:
            update_nearloc(entry['Latitude'], entry['Longitude'], 0, entry['Heading'], timestamp)
         
         if this.autotrspdr.get()=="1":
            if not this.trspdr_online:
               transponder(True, cmdr)
               #print "Survey = {}".format(this.survey_online)

         if this.trspdr_online:
            if(this.debug.get()=="1"):
               print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "TRSPDR count = {}".format(this.trspdr_count)
            if this.trspdr_count>=1:
               dist = calc_distance(this.nearloc['Latitude'], this.nearloc['Longitude'], this.lastloc['Latitude'], this.lastloc['Longitude'], this.radius)
               if(this.SRVmode):
                  maxalt = 0.5
               else:
                  maxalt = 2.
               if(this.debug.get()=="1"):
                  print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "TRSPDR try = {} >= {}".format(dist,max(maxalt,this.nearloc['Altitude']))
               if (dist >= max(maxalt,this.nearloc['Altitude'])):
                  this.trspdr_count += 1
                  update_lastloc(this.nearloc['Latitude'], this.nearloc['Longitude'], this.nearloc['Altitude'], this.nearloc['Heading'], this.nearloc['Time'])
                  send_data(cmdr, this.nearloc['Latitude'], this.nearloc['Longitude'], this.nearloc['Altitude'], this.nearloc['Heading'], "Screenshot", this.nearloc['Time'])
            else:
               this.trspdr_count += 1
               update_lastloc(this.nearloc['Latitude'], this.nearloc['Longitude'], this.nearloc['Altitude'], this.nearloc['Heading'], this.nearloc['Time'])
               send_data(cmdr, this.nearloc['Latitude'], this.nearloc['Longitude'], this.nearloc['Altitude'], this.nearloc['Heading'], "Screenshot", this.nearloc['Time'])

         if (this.lat_dest is not None) and (this.lon_dest is not None):
            dist = calc_distance(this.nearloc['Latitude'], this.nearloc['Longitude'], this.lat_dest, this.lon_dest, this.radius)
            brng = calc_bearing(this.nearloc['Latitude'], this.nearloc['Longitude'], this.lat_dest, this.lon_dest, this.radius)
            updateBearing(this.lat_dest, this.lon_dest, round(brng,2), round(dist,3))
         else:
            if this.bearing:
               this.bearing = False
               this.bearing_status.grid_remove()
         
      else:
         this.body_name = None
         update_nearloc(None, None, None, None, timestamp)
         transponder(False)
      #print "landed = {}".format(this.landed)

def journal_entry(cmdr, is_beta, system, station, entry, state):
   if is_beta:
      updateInfo("v"+this.version+" - This version is only working on ED v3.0", False)
      time.sleep(0.01)
      return
   
   if this.update:
      if entry['event'] == 'Location':
         transponder(False)
         if ('StarSystem' in entry):
            this.system_name = entry['StarSystem']
            #print "SystemAddress = {}".format(entry['SystemAddress'])
         if ('Body' in entry):
            this.body_name = entry['Body']
            #print "BodyID = {}".format(entry['BodyID'])
         if ('Latitude' in entry) and ('Longitude' in entry):
            this.landed = True
            timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
            send_data(cmdr, entry['Latitude'], entry['Longitude'], None, None, entry['event'], timestamp)
         updateInfo("v"+this.version+" - Ready", False)

      if entry['event'] == 'StartUp':
         transponder(False)
         if ('StarSystem' in entry):
            this.system_name = entry['StarSystem']
         if ('Body' in entry):
            this.body_name = entry['Body']
         this.droped = []
         updateInfo("v"+this.version+" - Ready", False)

      if entry['event'] == 'ShutDown':
         transponder(False)
         this.system_name = None
         this.body_name = None
         this.droped = []
         updateInfo("v"+this.version+" - Ready", False)

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

         if entry['Message'][:len(this.surveyToggle)].lower() == this.surveyToggle.lower():
            if this.survey_online:
               this.survey_online = False
               if this.trspdrsound.get()=="1":
                  soundfile = os.path.dirname(this.__file__)+'\\'+'survey_off.wav'
                  this.queue.put(('playsound', soundfile, None))
            else:
               this.survey_online = True
               if this.trspdrsound.get()=="1":
                  soundfile = os.path.dirname(this.__file__)+'\\'+'survey_on.wav'
                  this.queue.put(('playsound', soundfile, None))
                  
         if entry['Message'].lower() == this.trspdrToggle.lower():
            if this.autotrspdr.get()=="1":
               this.autotrspdr = tk.StringVar(value="0")
               transponder(False)
            else:
               this.autotrspdr = tk.StringVar(value="1")
               #transponder(True, cmdr)
            #if this.trspdr_online:
            #   transponder(False)
            #else:
            #   if this.autosurvey.get()=="1":
            #      this.survey_online = True
            #   transponder(True, cmdr)
               
         if entry['Message'][:len(this.setdestToggle)].lower() == this.setdestToggle.lower():
            try:
               if(this.nearloc['Latitude'] is not None and this.nearloc['Longitude'] is not None):
                  coord_dest = entry['Message'][len(this.setdestToggle)+1:].strip("()").split(",")
                  latitude = coord_dest[0]
                  longitude = coord_dest[1]
                  if this.destsound.get()=="1":
                     soundfile = os.path.dirname(this.__file__)+'\\'+'new_destination.wav'
                     this.queue.put(('playsound', soundfile, None))
                  updateInfo("Set destination to ({},{})".format(latitude, longitude))
                  timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
                  send_destination(cmdr, 1, latitude, longitude)
                  send_data(cmdr, this.nearloc['Latitude'], this.nearloc['Longitude'], this.nearloc['Altitude'], this.nearloc['Heading'], "Screenshot DEST", this.nearloc['Time'])
               else:
                  plug.show_error(_('Error: #ExTool DEST need to have lat lon'))
                  if(this.debug.get()=="1"):
                     print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "Error: #ExTool DEST need to have lat lon"
            except:
               updateInfo("Unset destination")
               this.lat_dest = None
               this.lon_dest = None
               send_destination(cmdr, 0, 0, 0)
               if this.bearing:
                  this.bearing = False
                  this.bearing_status.grid_remove()

         if entry['Message'][:len(this.savepointToggle)].lower() == this.savepointToggle.lower():
            if(this.nearloc['Latitude'] is not None and this.nearloc['Longitude'] is not None):
               timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
               send_data(cmdr, this.nearloc['Latitude'], this.nearloc['Longitude'], this.nearloc['Altitude'], this.nearloc['Heading'], "Screenshot SAVE", this.nearloc['Time'])
               send_savepoint(cmdr, entry['Message'][len(this.savepointToggle)+1:], timestamp)
            else:
               plug.show_error(_('Error: #ExTool SAVE need to have lat lon'))
               if(this.debug.get()=="1"):
                  print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "Error: #ExTool SAVE need to have lat lon"
            
         if entry['Message'][:len(this.delpointToggle)].lower() == this.delpointToggle.lower():
            name_point = entry['Message'][len(this.delpointToggle)+1:]
            send_delpoint(cmdr, name_point)

         #if entry['Message'].lower() == "#ExTool BT".lower():
         #   timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
         #   send_data(cmdr, this.nearloc['Latitude'], this.nearloc['Longitude'], this.nearloc['Altitude'], this.nearloc['Heading'], "Screenshot SAVE", this.nearloc['Time'])
         #   send_savepoint(cmdr, "Brain Trees", timestamp)
            
         #if entry['Message'].lower() == "#ExTool VOLCA".lower():
         #   timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
         #   send_data(cmdr, this.nearloc['Latitude'], this.nearloc['Longitude'], this.nearloc['Altitude'], this.nearloc['Heading'], "Screenshot SAVE", this.nearloc['Time'])
         #   send_savepoint(cmdr, "Volcanism", timestamp)
            
      if entry['event'] == 'Screenshot':
         if ('Latitude' in entry) and ('Longitude' in entry):
            this.system_name = entry['System']
            this.body_name = entry['Body']
            if ('Altitude' in entry):
               altitude = round(entry['Altitude'] / 1000.,3)
            else:
               altitude = None
            if ('Heading' in entry):
               heading = entry['Heading']
            else:
               heading = None
            timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
            #if(not this.trspdr_online and this.trySC):
            #   this.trySC = False
            #else:
            send_data(cmdr, entry['Latitude'], entry['Longitude'], altitude, heading, entry['event']+" NA", timestamp)
            deleteScreenshot(entry['Filename'])

      if entry['event'] == 'Touchdown':
         if entry['PlayerControlled']:
            if ('Latitude' in entry) and ('Longitude' in entry):
               this.landed = True
               timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
               send_data(cmdr, entry['Latitude'], entry['Longitude'], None, None, entry['event'], timestamp)
      if entry['event'] == 'Liftoff':
         if entry['PlayerControlled']:
            if ('Latitude' in entry) and ('Longitude' in entry):
               this.landed = False
               this.droped = []
               timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
               send_data(cmdr, entry['Latitude'], entry['Longitude'], None, None, entry['event'], timestamp)

      if entry['event'] == 'StartJump':
         this.SCmode = True
         if entry['JumpType'] == 'Hyperspace':
            transponder(False)
            this.system_name = entry['StarSystem']
            this.body_name = None
      
      if entry['event'] == 'SupercruiseEntry':
         this.SCmode = True
         this.system_name = entry['StarSystem']
      if entry['event'] == 'SupercruiseExit':
         this.SCmode = False
         this.system_name = entry['StarSystem']
         if ('Body' in entry):
            this.body_name = entry['Body']
      
      if entry['event'] == 'LaunchSRV':
         this.SRVmode = True
      if entry['event'] == 'DockSRV':
         this.SRVmode = False

      if entry['event'] == 'ApproachBody':
         this.system_name = entry['StarSystem']
         this.body_name = entry['Body']
      if entry['event'] == 'LeaveBody':
         transponder(False)
         this.system_name = entry['StarSystem']
         this.body_name = None
         
      if entry['event'] == 'CollectCargo':
         if this.landed:
            if entry['Type'] in this.droped:
               this.droped.remove(entry['Type'])
            else:
               timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
               send_data(cmdr, this.nearloc['Latitude'], this.nearloc['Longitude'], this.nearloc['Altitude'], this.nearloc['Heading'], "Screenshot MAT", this.nearloc['Time'])
               send_material(cmdr, "Cargo", entry['Type'], 1, timestamp)
      if entry['event'] == 'EjectCargo':
         if this.landed:
            for x in range(0, entry['Count']):
               this.droped.append(entry['Type'])
      if entry['event'] == 'MaterialCollected':
         if this.landed:
            timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
            send_data(cmdr, this.nearloc['Latitude'], this.nearloc['Longitude'], this.nearloc['Altitude'], this.nearloc['Heading'], "Screenshot MAT", this.nearloc['Time'])
            send_material(cmdr, entry['Category'], entry['Name'], entry['Count'], timestamp)
      if entry['event'] == 'DatalinkScan':
         if this.landed:
            timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
            send_data(cmdr, this.nearloc['Latitude'], this.nearloc['Longitude'], this.nearloc['Altitude'], this.nearloc['Heading'], "Screenshot SCAN", this.nearloc['Time'])
            send_datalink(cmdr, entry['Message'], timestamp)
      if entry['event'] == 'DatalinkVoucher':
         if this.landed:
            timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
            send_data(cmdr, this.nearloc['Latitude'], this.nearloc['Longitude'], this.nearloc['Altitude'], this.nearloc['Heading'], "Screenshot SCAN", this.nearloc['Time'])
            send_datavoucher(cmdr, entry['Reward'], entry['VictimFaction'], entry['PayeeFaction'], timestamp)
      if entry['event'] == 'DataScanned':
         if this.landed:
            timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
            send_data(cmdr, this.nearloc['Latitude'], this.nearloc['Longitude'], this.nearloc['Altitude'], this.nearloc['Heading'], "Screenshot SCAN", this.nearloc['Time'])
            send_datascan(cmdr, entry['Type'], timestamp)

def update_nearloc(latitude, longitude, altitude, heading, timestamp):
   this.nearloc['Latitude'] = latitude
   this.nearloc['Longitude'] = longitude
   this.nearloc['Altitude'] = altitude
   this.nearloc['Heading'] = heading
   this.nearloc['Time'] = timestamp
   #if(this.debug.get()=="1"):
   #   print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "update nearloc to ({},{}) A{} H{} at {}".format(this.nearloc['Latitude'],this.nearloc['Longitude'],this.nearloc['Altitude'],this.nearloc['Heading'],this.nearloc['Time'])

def update_lastloc(latitude, longitude, altitude, heading, timestamp):
   this.lastloc['Latitude'] = latitude
   this.lastloc['Longitude'] = longitude
   this.lastloc['Altitude'] = altitude
   this.lastloc['Heading'] = heading
   this.lastloc['Time'] = timestamp

def send_data(cmdr, latitude, longitude, altitude, heading, event, timestamp):
   #if (time.time()>this.time_lastsend+this.delay):
   
   url = this.url_website+"send_data"
   
   if(event=='Screenshot') :

      if(this.trspdr_online):
         trspdr_status = "1"
      else:
         trspdr_status = "0"
      if(not EliteInForeground() or not this.survey_online or altitude is None):
         event += ' NA'
      elif(this.landed):
         event += ' L'
      #elif(this.altitude.get()=="0"):
      elif(this.SCmode):
         event += ' SC'
   elif(event=='Screenshot NA') :
      trspdr_status = "0"
      if(this.landed):
         event = 'Screenshot L'
   else:
      trspdr_status = "0"

   if altitude is None:
      altitude = "0"
   if heading is None:
      heading = ""

   payload = {
      'system' : this.system_name,
      'body' : this.body_name,
      'latitude' : '{}'.format(latitude),
      'longitude' : '{}'.format(longitude),
      'altitude' : '{}'.format(altitude),
      'heading' : '{}'.format(heading),
      'trspdr' : trspdr_status,
      'event' : event,
      'timestamp' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
   }

   if(event=='Screenshot' or event=='Screenshot SC' or event=='Screenshot NA') :
      if(altitude == "0"):
         new_text = "NO ALT - {}".format(this.body_name)
      else:
         new_text = "ALT {}km - {}".format(altitude, this.body_name)
   elif(event=='Screenshot L') :
      new_text = "Ground - {}".format(this.body_name)
   elif(event=='Screenshot MAT') :
      new_text = "Material - {}".format(this.body_name)
   elif(event=='Screenshot SCAN') :
      new_text = "Scan - {}".format(this.body_name)
   elif(event=='Screenshot SAVE') :
      new_text = "Save - {}".format(this.body_name)
   elif(event=='Screenshot DEST') :
      new_text = "Destination - {}".format(this.body_name)
   else:
      new_text = event + " - {}".format(this.body_name)

   new_url = this.url_website+"index.php?mode=3d&planet={}&goto={},{}".format(this.body_name, latitude, longitude)
   updateInfoURL(new_text, new_url)

   #if(trspdr_status=="1") :
   #   call(cmdr, 'coords', payload, callback=update_velocity)
   #else:
   call(cmdr, 'coords', payload)

   
   if(event=='Screenshot' or event=='Screenshot SC' or event=='Screenshot NA' or event=='Screenshot L' or event=='Screenshot SAVE' or event=='Screenshot MAT' or event=='Screenshot SCAN'):
      if(trspdr_status=="1") :
         if(this.survey_online):
            if(this.trspdrsound.get()=="1" or this.surveysound.get()=="1") :
               soundfile = 'snd_good.wav'
               this.queue.put(('playsound', soundfile, None))
         else:
            if(this.trspdrsound.get()=="1"):
               soundfile = 'snd_good.wav'
               this.queue.put(('playsound', soundfile, None))
      else:
         soundfile = 'snd_good.wav'
         this.queue.put(('playsound', soundfile, None))

def send_material(cmdr, category, name, count, timestamp):
   url = this.url_website+"send_data"
   #timestamp = time.localtime(timestamp)
   #timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
   #timestamp = time.mktime(time.strptime(timestamp, '%Y-%m-%d %H:%M:%S'))
   payload = {
      'system' : this.system_name,
      'body' : this.body_name,
      'latitude' : '{}'.format(this.nearloc['Latitude']),
      'longitude' : '{}'.format(this.nearloc['Longitude']),
      'altitude' : '{}'.format(this.nearloc['Altitude']),
      'heading' : '{}'.format(this.nearloc['Heading']),
      'category' : category,
      'name' : name,
      'count' : '%d' % count,
      'timestamp' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp)),
      'time' : '%d' % round(timestamp-this.nearloc['Time'])
   }
   call(cmdr, 'materials', payload)

def send_datalink(cmdr, message, timestamp):
   url = this.url_website+"send_data"
   payload = {
      'system' : this.system_name,
      'body' : this.body_name,
      'latitude' : '{}'.format(this.nearloc['Latitude']),
      'longitude' : '{}'.format(this.nearloc['Longitude']),
      'altitude' : '{}'.format(this.nearloc['Altitude']),
      'heading' : '{}'.format(this.nearloc['Heading']),
      'message' : message,
      'timestamp' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp)),
      'time' : '%d' % round(timestamp-this.nearloc['Time'])
   }
   call(cmdr, 'datalink', payload)

def send_datavoucher(cmdr, reward, victim, payee, timestamp):
   url = this.url_website+"send_data"
   payload = {
      'system' : this.system_name,
      'body' : this.body_name,
      'latitude' : '{}'.format(this.nearloc['Latitude']),
      'longitude' : '{}'.format(this.nearloc['Longitude']),
      'altitude' : '{}'.format(this.nearloc['Altitude']),
      'heading' : '{}'.format(this.nearloc['Heading']),
      'reward' : '%d' % reward,
      'victim' : victim,
      'payee' : payee,
      'timestamp' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp)),
      'time' : '%d' % round(timestamp-this.nearloc['Time'])
   }
   call(cmdr, 'datavoucher', payload)

def send_datascan(cmdr, typescan, timestamp):
   url = this.url_website+"send_data"
   payload = {
      'system' : this.system_name,
      'body' : this.body_name,
      'latitude' : '{}'.format(this.nearloc['Latitude']),
      'longitude' : '{}'.format(this.nearloc['Longitude']),
      'altitude' : '{}'.format(this.nearloc['Altitude']),
      'heading' : '{}'.format(this.nearloc['Heading']),
      'typescan' : typescan,
      'timestamp' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp)),
      'time' : '%d' % round(timestamp-this.nearloc['Time'])
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
      'latitude' : '{}'.format(this.nearloc['Latitude']),
      'longitude' : '{}'.format(this.nearloc['Longitude']),
      'altitude' : '{}'.format(this.nearloc['Altitude']),
      'heading' : '{}'.format(this.nearloc['Heading']),
      'name_point' : name_point,
      'timestamp' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp)),
      'time' : '%d' % round(timestamp-this.nearloc['Time'])
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
         (mode, data, callback) = item

      if(mode=='senddata'):

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
                     if ('Latitude_Dest' in reply and 'Longitude_Dest' in reply):
                        this.lat_dest = reply['Latitude_Dest']
                        this.lon_dest = reply['Longitude_Dest']
                     if ('Radius' in reply):
                        this.radius = reply['Radius']
                     #print "lala = {} {} {}".format(this.lat_dest,this.lon_dest,this.radius)
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

def call(cmdr, sendmode, args, callback=None):
   args = dict(args)
   args['cmdr'] = cmdr
   args['mode'] = sendmode
   args['version'] = this.version
   args['apikey'] = this.apikey.get()
   if(this.debug.get()=="1"):
      print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "call : {}".format(sendmode)
   this.queue.put(('senddata', args, callback))

def calc_distance(phi_a, lambda_a, phi_b, lambda_b, radius):

   if radius is None:
      return 0.0
   
   phi_a = phi_a * math.pi / 180.
   lambda_a = lambda_a * math.pi / 180.
   phi_b = phi_b * math.pi / 180.
   lambda_b = lambda_b * math.pi / 180.

   if(phi_a != phi_b or lambda_b != lambda_a):
      d_lambda = lambda_b - lambda_a
      S_ab = math.acos(math.sin(phi_a)*math.sin(phi_b)+math.cos(phi_a)*math.cos(phi_b)*math.cos(d_lambda))
      return S_ab * radius
   else:
      return 0.0

def calc_bearing(phi_a, lambda_a, phi_b, lambda_b, radius):

   if radius is None:
      return 0.0
   
   phi_a = phi_a * math.pi / 180.
   lambda_a = lambda_a * math.pi / 180.
   phi_b = phi_b * math.pi / 180.
   lambda_b = lambda_b * math.pi / 180.

   if(phi_a != phi_b or lambda_b != lambda_a):
      d_lambda = lambda_b - lambda_a
      y = math.sin(d_lambda)*math.cos(phi_b)
      x = math.cos(phi_a)*math.sin(phi_b)-math.sin(phi_a)*math.cos(phi_b)*math.cos(d_lambda)
      brng = math.atan2(y,x)*180./math.pi
      if brng<0:
         brng += 360.
      return brng
   else:
      return 0.0

def update_velocity(args):
   if ('TrspdrDelay' in args) and ('Velocity' in args):
      if(this.debug.get()=="1"):
         print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "TRSPDR : n={} vel={} delay={}".format(this.trspdr_count, args['Velocity'], args['TrspdrDelay']/1000)
      if(this.trspdr_count>1):
         if this.SCmode:
            this.trspdr_delay = max(min(args['TrspdrDelay'],20000),5000)
            if(args['TrspdrDelay'] == 0):
               this.trspdr_delay = 20000
         else:
            this.trspdr_delay = max(min(args['TrspdrDelay'],60000),5000)
            if(args['TrspdrDelay'] == 0):
               this.trspdr_delay = 60000
               if this.survey_online:
                  this.survey_online = False
                  if this.trspdrsound.get()=="1":
                     soundfile = os.path.dirname(this.__file__)+'\\'+'survey_off.wav'
                     this.queue.put(('playsound', soundfile, None))
         #   transponder(False)
   else:
      this.trspdr_delay = 10000

def check_version():
   if this.version[-5:]!="_beta":
      url = this.url_website+"EDMC/version"
   else:
      url = this.url_website+"EDMC/version_beta"
   rsend = this.session.get(url, verify=False)
   if rsend.content[:5] != this.version[:5]:
      this.update_version = rsend.content
      this.update = False
      this.new_version = True
   else:
      if rsend.content != this.version:
         this.update_version = rsend.content
         this.new_version = True

def transponder(status, cmdr = None):
   if (cmdr is None) or (this.body_name is None) or (this.system_name is None) or (this.nearloc['Latitude'] is None) or (this.nearloc['Longitude'] is None):
      status = False
   if(this.debug.get()=="1"):
      print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "TRSPDR status = {}".format(status)
   if status:
      if not this.trspdr_online:
         updateInfo("Transponder activated")
         this.trspdr_online = True
         this.trspdr_delay = 10000
         this.trspdr_count = 0
         if this.trspdrsound.get()=="1":
            soundfile = os.path.dirname(this.__file__)+'\\'+'trspdr_on.wav'
            this.queue.put(('playsound', soundfile, None))
         #transponderStart(cmdr)
   else:
      if this.trspdr_online:
         this.trspdr_online = False
         this.survey_online = False
         updateInfo("Transponder deactivated")
         if this.trspdrsound.get()=="1":
            soundfile = os.path.dirname(this.__file__)+'\\'+'trspdr_off.wav'
            this.queue.put(('playsound', soundfile, None))

def transponderStart(cmdr):
   if (not this.trspdr_online) or (cmdr is None) or (this.body_name is None) or (this.system_name is None) or (this.nearloc['Latitude'] is None) or (this.nearloc['Longitude'] is None):
      transponder(False)
      return
   if EliteInForeground():
      this.trspdr_count += 1
      send_data(cmdr, this.nearloc['Latitude'], this.nearloc['Longitude'], this.nearloc['Altitude'], this.nearloc['Heading'], "Screenshot", this.nearloc['Time'])
      this.label.after(this.trspdr_delay, transponderStart, cmdr)
   else:
      updateInfo("StandBy Mode - Not in Elite Dangerous")
      this.label.after(5000, transponderStart, cmdr)

def deleteScreenshot(filename):
   if this.scdir.get()!="":
      file = this.scdir.get() + '\\'+ filename[13:]
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
