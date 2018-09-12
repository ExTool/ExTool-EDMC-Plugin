# -*- encoding: utf-8 -*-

import sys
import datetime
import time
import requests
import os
from os.path import isfile
import key
import math
import urllib2
from winsound import *
#from PriorityQueue import Queue
import Queue as Q
from threading import Thread

import Tkinter as tk
import myNotebook as nb
from ttkHyperlinkLabel import HyperlinkLabel

from config import config
import plug
import overlay
from overlay import display

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

this.StartJump = False
this.SCmode = False
this.SRVmode = False
this.landed = False
this.droped = []

this.system_name = None
this.body_name = None
this.body_drop = None
this.coordinates = None
this.lat_dest = None
this.lon_dest = None
this.x_dest = None
this.y_dest = None
this.z_dest = None
this.planet_dest = None
this.radius = None
this.landingpad = None

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
this.version = "1.1.1"
this.update = True
this.disable = False
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
this.chksysToggle = "#ExTool CHKSYS"
this.commentToggle = "#ExTool COMMENT"

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
if(config.get("ExTool_MatSound")==None):
   config.set("ExTool_MatSound", "0")
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

   this.matsound = tk.StringVar(value=config.get("ExTool_MatSound"))
   this.destsound = tk.StringVar(value=config.get("ExTool_DestSound"))

   this.debug = tk.StringVar(value=config.get("ExTool_Debug"))
   #this.extool_on = tk.StringVar(value=config.get("ExTool_On"))
   #this.extool_off = tk.StringVar(value=config.get("ExTool_Off"))
   #this.delsc_toggle = tk.StringVar(value=config.get("ExTool_DelSC"))

   this.thread = Thread(target = worker, name = 'ExTool worker')
   this.thread.daemon = True
   this.thread.start()
   
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
   
   matsound_checkbox = nb.Checkbutton(frame, text="Play sound when scanning or collecting materials", variable=this.matsound)
   matsound_checkbox.grid(columnspan=2, padx = BUTTONX, pady = PADY, sticky=tk.W)
   
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
   config.set("ExTool_SurveySound", this.surveysound.get())
   
   config.set("ExTool_SCDIR", this.scdir.get())
   #config.set("ExTool_DeleteAutoScreen", this.deleteautoscreen.get())
   config.set("ExTool_DeleteScreen", this.deletescreen.get())

   config.set("ExTool_MatSound", this.matsound.get())
   config.set("ExTool_DestSound", this.destsound.get())

   config.set("ExTool_Debug", this.debug.get())

def plugin_app(parent):
   this.parent = parent
   this.frame = tk.Frame(parent)
   this.frame.columnconfigure(2, weight=1)
   this.label = tk.Label(this.frame, text="ExTool:   ")
   
   #this.status1 = tk.Label(this.frame, anchor=tk.W, text="")
   this.status = HyperlinkLabel(this.frame, anchor=tk.W, text="", popup_copy = True)
   this.infobody_status = HyperlinkLabel(this.frame, anchor=tk.W, text="", popup_copy = True)
   this.bearing_status = tk.Label(this.frame, anchor=tk.W, text="")

   this.label.grid(row = 0, column = 0, sticky=tk.W)
   this.status.grid(row = 0, column = 1, sticky=tk.W)
   this.infobody_status.grid(row = 1, column = 0, columnspan=2, sticky=tk.W)
   this.bearing_status.grid(row = 2, column = 0, columnspan=2, sticky=tk.W)

   this.infobody = False
   this.infobody_status.grid_remove()
   
   this.bearing = False
   this.bearing_status.grid_remove()

   check_version()
   
   if this.disable:
      updateInfo("ExTool temporary disabled", False)
   else:
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

   this.bearing_status["text"] = "   DEST ({},{}) : BEARING {} / DIST {} km".format(latitude, longitude, bearing, distance)
   display(this.bearing_status["text"], 250,730, "yellow", "normal")    
   
   if(this.debug.get()=="1"):
      print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "updateBearing = {} / {}".format(bearing, distance)

def updateSysBearing(x, y, z, planet):
   #this.status["text"] = ""
   #this.status.grid_remove()
   #this.status = tk.Label(this.frame, anchor=tk.W)

   if(this.coordinates is not None):
      distance = round(math.sqrt((this.coordinates[0]-x)**2+(this.coordinates[1]-y)**2+(this.coordinates[2]-z)**2),2)
      
      if not this.bearing:
         this.bearing = True
         this.bearing_status.grid()

      if(distance==0):
         this.bearing_status["text"] = "   DEST System({},{},{}) : Planet {}".format(round(x,1), round(y,1), round(z,1), planet)
      else:
         this.bearing_status["text"] = "   DEST System({},{},{}) : DIST {} ly".format(round(x,1), round(y,1), round(z,1), round(distance,2))

      display(this.bearing_status["text"], 250,730, "yellow", "normal")    
      
      if(this.debug.get()=="1"):
         print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "updateSysBearing = {},{},{} / {}".format(x,y,z, distance)
   else:
      if this.bearing:
         this.bearing = False
         this.bearing_status.grid_remove()

def updateInfoBody(txt, url):
   #this.status["text"] = ""
   #this.status.grid_remove()
   #this.status = tk.Label(this.frame, anchor=tk.W)
   if not this.infobody:
      this.infobody = True
      this.infobody_status.grid()

   this.infobody_status["text"] = "   " + txt
   this.infobody_status["url"] = url
   
   if(this.debug.get()=="1"):
      print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "updateInfoBody = {} / {}".format(txt, url)

def dashboard_entry(cmdr, is_beta, entry):
   if this.infobody is None:
      this.infobody = False
      this.infobody_status.grid_remove()
      
   if this.update and not this.disable:
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

         if(this.nearloc['Altitude']<=500):
            if this.autotrspdr.get()=="1":
               if not this.trspdr_online:
                  transponder(True, cmdr)
                  #print "Survey = {}".format(this.survey_online)
            else:
               if this.survey_online:
                  if not this.trspdr_online:
                     transponder(True, cmdr)
         else:
            transponder(False)
            
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
         
         if (this.lat_dest is not None) and (this.lon_dest is not None) and (this.body_name is not None):
            dist = calc_distance(this.nearloc['Latitude'], this.nearloc['Longitude'], float(this.lat_dest), float(this.lon_dest), this.radius)
            brng = calc_bearing(this.nearloc['Latitude'], this.nearloc['Longitude'], float(this.lat_dest), float(this.lon_dest), this.radius)
            updateBearing(this.lat_dest, this.lon_dest, round(brng,2), round(dist,3))
         else:
            if (this.x_dest is None) or (this.y_dest is None) or (this.z_dest is None) or (this.planet_dest is None):
               if this.bearing:
                  this.bearing = False
                  this.bearing_status.grid_remove()
            else:
               updateSysBearing(this.x_dest, this.y_dest, this.z_dest, this.planet_dest)
         
      else:
         this.body_name = None
         update_nearloc(None, None, None, None, None)
         transponder(False)
         this.lat_dest = None
         this.lon_dest = None
         if (this.x_dest is None) or (this.y_dest is None) or (this.z_dest is None) or (this.planet_dest is None):
            if this.bearing:
               this.bearing = False
               this.bearing_status.grid_remove()
         else:
            updateSysBearing(this.x_dest, this.y_dest, this.z_dest, this.planet_dest)
         if this.infobody:
            this.infobody = False
            this.infobody_status.grid_remove()
      #print "landed = {}".format(this.landed)

def journal_entry(cmdr, is_beta, system, station, entry, state):
   if is_beta:
      updateInfo("v"+this.version+" - This version is only working on ED v3.0", False)
      time.sleep(0.01)
      return
   
   if this.update and not this.disable:
      if entry['event'] == 'Location':
         transponder(False)
         this.landingpad = None
         if ('StarSystem' in entry):
            this.system_name = entry['StarSystem']
            #print "SystemAddress = {}".format(entry['SystemAddress'])
            #print "BodyID = {}".format(entry['BodyID'])
         if ('Body' in entry):
            this.body_name = entry['Body']
            this.body_drop = entry['Body']
         if ('Latitude' in entry) and ('Longitude' in entry):
            this.landed = True
            timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
            send_data(cmdr, entry['Latitude'], entry['Longitude'], None, None, entry['event'], timestamp)
         if ('StarPos' in entry):
            this.coordinates = entry['StarPos']
            timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
            send_coordinates(cmdr, this.coordinates, timestamp)
            if (this.x_dest is not None) and (this.y_dest is not None) and (this.z_dest is not None) and (this.planet_dest is not None):
               updateSysBearing(this.x_dest, this.y_dest, this.z_dest, this.planet_dest)
         updateInfo("v"+this.version+" - Ready", False)

      if entry['event'] == 'StartUp':
         update_nearloc(None, None, None, None, None)
         transponder(False)
         if ('StarSystem' in entry):
            this.system_name = entry['StarSystem']
         if ('Body' in entry):
            this.body_name = entry['Body']
            this.body_drop = entry['Body']
         this.droped = []
         updateInfo("v"+this.version+" - Ready", False)

      if entry['event'] == 'ShutDown':
         this.system_name = None
         this.body_name = None
         this.body_drop = None
         update_nearloc(None, None, None, None, None)
         transponder(False)
         this.lat_dest = None
         this.lon_dest = None
         this.x_dest = None
         this.y_dest = None
         this.z_dest = None
         this.planet_dest = None
         this.landingpad = None
         if this.bearing:
            this.bearing = False
            this.bearing_status.grid_remove()
         if this.infobody:
            this.infobody = False
            this.infobody_status.grid_remove()
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
               if this.autotrspdr.get()=="0":
                  transponder(False)
               if this.surveysound.get()=="1":
                  soundfile = os.path.dirname(this.__file__)+'\\'+'survey_off.wav'
                  this.queue.put(('playsound', soundfile, None))
            else:
               this.survey_online = True
               if this.surveysound.get()=="1":
                  soundfile = os.path.dirname(this.__file__)+'\\'+'survey_on.wav'
                  this.queue.put(('playsound', soundfile, None))
                  
         if entry['Message'].lower() == this.trspdrToggle.lower():
            if this.autotrspdr.get()=="1":
               this.autotrspdr = tk.StringVar(value="0")
               if this.survey_online:
                  this.survey_online = False
                  if this.surveysound.get()=="1":
                     soundfile = os.path.dirname(this.__file__)+'\\'+'survey_off.wav'
                     this.queue.put(('playsound', soundfile, None))
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
            unset_dest = False
            try:
               #print "body = {}".format(this.body_name)
               if(this.nearloc['Latitude'] is not None and this.nearloc['Longitude'] is not None and this.body_name is not None):
                  coord_dest = entry['Message'][len(this.setdestToggle)+1:].strip("()").split(",")
                  this.lat_dest = coord_dest[0]
                  this.lon_dest = coord_dest[1]
                  if this.destsound.get()=="1":
                     soundfile = os.path.dirname(this.__file__)+'\\'+'new_destination.wav'
                     this.queue.put(('playsound', soundfile, None))
                  updateInfo("Set destination to ({},{})".format(this.lat_dest, this.lon_dest))
                  timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
                  send_destination(cmdr, 1, this.lat_dest, this.lon_dest)                  
                  send_data(cmdr, this.nearloc['Latitude'], this.nearloc['Longitude'], this.nearloc['Altitude'], this.nearloc['Heading'], "Screenshot DEST", this.nearloc['Time'])
                  dist = calc_distance(this.nearloc['Latitude'], this.nearloc['Longitude'], float(this.lat_dest), float(this.lon_dest), this.radius)
                  brng = calc_bearing(this.nearloc['Latitude'], this.nearloc['Longitude'], float(this.lat_dest), float(this.lon_dest), this.radius)
                  updateBearing(this.lat_dest, this.lon_dest, round(brng,2), round(dist,3))
               else:
                  plug.show_error(_('Error: #ExTool DEST need to have lat lon'))
                  unset_dest = True
                  if(this.debug.get()=="1"):
                     print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "Error: #ExTool DEST need to have lat lon"
            except:
               unset_dest = True
            finally:
               if(unset_dest):
                  updateInfo("Unset destination")
                  this.lat_dest = None
                  this.lon_dest = None
                  this.x_dest = None
                  this.y_dest = None
                  this.z_dest = None
                  this.planet_dest = None
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

         if entry['Message'][:len(this.chksysToggle)].lower() == this.chksysToggle.lower():
            timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
            comment = entry['Message'][len(this.chksysToggle)+len((entry['Message'][len(this.chksysToggle)+1:].split(" "))[0])+2:]
            send_chksys(cmdr, (entry['Message'][len(this.chksysToggle)+1:].split(" "))[0], comment, timestamp)

         if entry['Message'][:len(this.commentToggle)].lower() == this.commentToggle.lower():
            timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
            comment = entry['Message'][len(this.commentToggle)+1:]
            send_comment(cmdr, comment, timestamp)
            
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

      if entry['event'] == 'DockingGranted':
         this.landingpad = entry['LandingPad']

      if entry['event'] == 'Docked':
         if entry['StationType'] == 'SurfaceStation':
            this.landed = True
            timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
            send_data(cmdr, this.nearloc['Latitude'], this.nearloc['Longitude'], None, None, 'Touchdown', timestamp)
            send_surfacestation(cmdr, entry['StationName'], entry['MarketID'], timestamp)
         else:
            timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
            send_spacestation(cmdr, entry['StationName'], entry['MarketID'], timestamp)
      if entry['event'] == 'Undocked':
         this.landingpad = None
         if entry['StationType'] == 'SurfaceStation':
            this.landed = False
            this.droped = []
            timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
            send_data(cmdr, this.nearloc['Latitude'], this.nearloc['Longitude'], None, None, 'Liftoff', timestamp)
            send_surfacestation(cmdr, entry['StationName'], entry['MarketID'], timestamp)

      if entry['event'] == 'StartJump':
         this.SCmode = True
         this.StartJump = True
         if entry['JumpType'] == 'Hyperspace':
            transponder(False)
            this.system_name = entry['StarSystem']
            this.body_name = None
            this.body_drop = None
            this.droped = []
            if this.infobody:
               this.infobody = False
               this.infobody_status.grid_remove()
      
      if entry['event'] == 'FSDJump':
         this.SCmode = True
         this.StartJump = False
         if ('StarPos' in entry):
            this.coordinates = entry['StarPos']
            timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
            send_coordinates(cmdr, this.coordinates, timestamp)
            if (this.x_dest is not None) and (this.y_dest is not None) and (this.z_dest is not None) and (this.planet_dest is not None):
               updateSysBearing(this.x_dest, this.y_dest, this.z_dest, this.planet_dest)
      
      if entry['event'] == 'SupercruiseEntry':
         this.SCmode = True
         this.StartJump = False
         this.system_name = entry['StarSystem']
         this.body_drop = None
         this.droped = []
      if entry['event'] == 'SupercruiseExit':
         this.SCmode = False
         this.system_name = entry['StarSystem']
         if ('Body' in entry):
            this.body_name = entry['Body']
            this.body_drop = entry['Body']
      
      if entry['event'] == 'LaunchSRV':
         this.SRVmode = True
      if entry['event'] == 'DockSRV':
         this.SRVmode = False

      if entry['event'] == 'ApproachBody':
         this.system_name = entry['StarSystem']
         this.body_name = entry['Body']
      if entry['event'] == 'LeaveBody':
         #transponder(False)
         this.system_name = entry['StarSystem']
         #this.body_name = None

      if entry['event'] == 'ApproachSettlement':
         if(this.body_name is not None):
            timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
            send_settlement(cmdr, entry['Name'], entry['MarketID'], this.StartJump, timestamp)
         
      if entry['event'] == 'CollectCargo':
         if entry['Type'] in this.droped:
            this.droped.remove(entry['Type'])
         else:
            if this.landed:
               timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
               send_data(cmdr, this.nearloc['Latitude'], this.nearloc['Longitude'], this.nearloc['Altitude'], this.nearloc['Heading'], "Screenshot MAT", this.nearloc['Time'])
               send_material(cmdr, "Cargo", entry['Type'], 1, timestamp)
            else:
               timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
               send_spacematerial(cmdr, "Cargo", entry['Type'], 1, timestamp)
      if entry['event'] == 'EjectCargo':
         for x in range(0, entry['Count']):
            this.droped.append(entry['Type'])
      if entry['event'] == 'MaterialCollected':
         if this.landed:
            timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
            send_data(cmdr, this.nearloc['Latitude'], this.nearloc['Longitude'], this.nearloc['Altitude'], this.nearloc['Heading'], "Screenshot MAT", this.nearloc['Time'])
            send_material(cmdr, entry['Category'], entry['Name'], entry['Count'], timestamp)
         else:
            timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
            send_spacematerial(cmdr, entry['Category'], entry['Name'], entry['Count'], timestamp)
      if entry['event'] == 'DatalinkScan':
         if this.landed:
            timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
            send_data(cmdr, this.nearloc['Latitude'], this.nearloc['Longitude'], this.nearloc['Altitude'], this.nearloc['Heading'], "Screenshot SCAN", this.nearloc['Time'])
            send_datalink(cmdr, entry['Message'], timestamp)
         else:
            timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
            send_spacedatalink(cmdr, entry['Message'], timestamp)
      if entry['event'] == 'DatalinkVoucher':
         if this.landed:
            timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
            send_data(cmdr, this.nearloc['Latitude'], this.nearloc['Longitude'], this.nearloc['Altitude'], this.nearloc['Heading'], "Screenshot SCAN", this.nearloc['Time'])
            send_datavoucher(cmdr, entry['Reward'], entry['VictimFaction'], entry['PayeeFaction'], timestamp)
         else:
            timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
            send_spacedatavoucher(cmdr, entry['Reward'], entry['VictimFaction'], entry['PayeeFaction'], timestamp)
      if entry['event'] == 'DataScanned':
         if this.landed:
            timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
            send_data(cmdr, this.nearloc['Latitude'], this.nearloc['Longitude'], this.nearloc['Altitude'], this.nearloc['Heading'], "Screenshot SCAN", this.nearloc['Time'])
            send_datascan(cmdr, entry['Type'], timestamp)
         else:
            timestamp = time.mktime(time.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
            send_spacedatascan(cmdr, entry['Type'], timestamp)

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

   new_url = this.url_website + 'index.php?mode=3d&planet=%s&goto=%f,%f' % (urllib2.quote(this.body_name), latitude, longitude)
   updateInfoURL(new_text, new_url)

   #if(trspdr_status=="1") :
   #   call(cmdr, 'coords', payload, callback=update_velocity)
   #else:
   call(cmdr, 'coords', payload)

   if(isfile(os.path.dirname(this.__file__)+'\\'+'snd_good.wav')):
      soundfile = os.path.dirname(this.__file__)+'\\'+'snd_good.wav'
   else:
      soundfile = 'snd_good.wav'
   
   if(event=='Screenshot' or event=='Screenshot SC' or event=='Screenshot NA' or event=='Screenshot L'):
      if(trspdr_status=="1") :
         if(this.survey_online):
            if(this.trspdrsound.get()=="1" or this.surveysound.get()=="1") :
               this.queue.put(('playsound', soundfile, None))
         else:
            if(this.trspdrsound.get()=="1"):
               this.queue.put(('playsound', soundfile, None))
      else:
         this.queue.put(('playsound', soundfile, None))
   elif(event=='Screenshot MAT' or event=='Screenshot SCAN'):
      if(this.matsound.get()=="1"):
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

def send_spacematerial(cmdr, category, name, count, timestamp):
   url = this.url_website+"send_data"
   payload = {
      'system' : this.system_name,
      'bodydrop' : this.body_drop,
      'category' : category,
      'name' : name,
      'count' : '%d' % count,
      'timestamp' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
   }
   call(cmdr, 'spacematerial', payload)

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

def send_spacedatalink(cmdr, message, timestamp):
   url = this.url_website+"send_data"
   payload = {
      'system' : this.system_name,
      'bodydrop' : this.body_drop,
      'message' : message,
      'timestamp' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
   }
   call(cmdr, 'spacedatalink', payload)

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

def send_spacedatavoucher(cmdr, reward, victim, payee, timestamp):
   url = this.url_website+"send_data"
   payload = {
      'system' : this.system_name,
      'bodydrop' : this.body_drop,
      'reward' : '%d' % reward,
      'victim' : victim,
      'payee' : payee,
      'timestamp' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))   }
   call(cmdr, 'spacedatavoucher', payload)

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

def send_spacedatascan(cmdr, typescan, timestamp):
   url = this.url_website+"send_data"
   payload = {
      'system' : this.system_name,
      'bodydrop' : this.body_drop,
      'typescan' : typescan,
      'timestamp' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
   }
   call(cmdr, 'spacedatascan', payload)

def send_chksys(cmdr, chksys, comment, timestamp):
   url = this.url_website+"send_data"
   payload = {
      'system' : this.system_name,
      'chksys' : chksys,
      'comment' : comment,
      'timestamp' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
   }
   call(cmdr, 'chksys', payload)

def send_comment(cmdr, comment, timestamp):
   url = this.url_website+"send_data"
   payload = {
      'system' : this.system_name,
      'bodydrop' : this.body_drop,
      'comment' : comment,
      'timestamp' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
   }
   call(cmdr, 'comment', payload)

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

def send_surfacestation(cmdr, name_settlement, marketID, timestamp):
   url = this.url_website+"send_data"
   if this.landingpad is None:
      pad = ""
   else:
      pad = this.landingpad
   payload = {
      'system' : this.system_name,
      'body' : this.body_name,
      'latitude' : '{}'.format(this.nearloc['Latitude']),
      'longitude' : '{}'.format(this.nearloc['Longitude']),
      'name_settlement' : name_settlement,
      'marketID' : '{}'.format(marketID),
      'landingpad' : '{}'.format(pad),
      'timestamp' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp)),
      'time' : '%d' % round(timestamp-this.nearloc['Time'])
   }
   call(cmdr, 'surfacestation', payload)

def send_spacestation(cmdr, name_settlement, marketID, timestamp):
   url = this.url_website+"send_data"
   if this.landingpad is None:
      pad = ""
   else:
      pad = this.landingpad
   payload = {
      'system' : this.system_name,
      'name_settlement' : name_settlement,
      'marketID' : '{}'.format(marketID),
      'landingpad' : '{}'.format(pad),
      'timestamp' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
   }
   call(cmdr, 'spacestation', payload)

def send_settlement(cmdr, name_settlement, marketID, startJump, timestamp):
   url = this.url_website+"send_data"
   payload = {
      'system' : this.system_name,
      'body' : this.body_name,
      'latitude' : '{}'.format(this.nearloc['Latitude']),
      'longitude' : '{}'.format(this.nearloc['Longitude']),
      'altitude' : '{}'.format(this.nearloc['Altitude']),
      'heading' : '{}'.format(this.nearloc['Heading']),
      'name_settlement' : name_settlement,
      'marketID' : '{}'.format(marketID),
      'startJump' : '{}'.format(startJump),
      'timestamp' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp)),
      'time' : '%d' % round(timestamp-this.nearloc['Time'])
   }
   call(cmdr, 'settlement', payload)

def send_coordinates(cmdr, coordinates, timestamp):
   url = this.url_website+"send_data"
   #timestamp = time.localtime(timestamp)
   #timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
   #timestamp = time.mktime(time.strptime(timestamp, '%Y-%m-%d %H:%M:%S'))
   payload = {
      'system' : this.system_name,
      'syscoords' : '{}'.format(coordinates),
      'timestamp' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
   }
   call(cmdr, 'coordinates', payload)

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
                  #print(reply)
                  if ('X_Dest' in reply and 'Y_Dest' in reply and 'Z_Dest' in reply):
                     this.x_dest = reply['X_Dest']
                     this.y_dest = reply['Y_Dest']
                     this.z_dest = reply['Z_Dest']
                     this.planet_dest = reply['Planet_Dest']
                  else:
                     this.x_dest = None
                     this.y_dest = None
                     this.z_dest = None
                     this.planet_dest = None
                     
                  if ('Latitude_Dest' in reply and 'Longitude_Dest' in reply):
                     this.lat_dest = reply['Latitude_Dest']
                     this.lon_dest = reply['Longitude_Dest']
                  else:
                     this.lat_dest = None
                     this.lon_dest = None

                  if('Radius' in reply):
                     this.radius = reply['Radius']
                     
                  if('InfoBody' in reply and 'InfoBodyURL' in reply):
                     updateInfoBody( reply['InfoBody'], reply['InfoBodyURL'] )
                  else:
                     this.infobody = None
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

   if(this.debug.get()=="1"):
      print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "calc_distance"
      print datetime.datetime.now().strftime("%H:%M:%S") + " - " + "{} {} {} {} {}".format(phi_a, lambda_a, phi_b, lambda_b, radius)
      
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
   rsend = this.session.get(url, verify=False, timeout=_TIMEOUT)
   #print(url)
   
   if rsend.status_code == requests.codes.ok:
      if rsend.content[:5] != this.version[:5]:
         if this.version[0]<rsend.content[0] or (this.version[0]==rsend.content[0] and this.version[2]<rsend.content[2]) or (this.version[0]==rsend.content[0] and this.version[2]==rsend.content[2] and this.version[4]<rsend.content[4]):
            this.update_version = rsend.content
            this.update = False
            this.new_version = True
      else:
         if rsend.content != this.version:
            this.update_version = rsend.content
            this.new_version = True
   else:
      this.disable = True

   if this.disable:
      print('ExTool : retry in 60sec')
      this.frame.after(60000,check_version)

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
         #this.survey_online = True
         #if this.surveysound.get()=="1":
         #   soundfile = os.path.dirname(this.__file__)+'\\'+'survey_on.wav'
         #   this.queue.put(('playsound', soundfile, None))
         #transponderStart(cmdr)
   else:
      if this.trspdr_online:
         this.trspdr_online = False
         updateInfo("Transponder deactivated")
         if this.trspdrsound.get()=="1":
            soundfile = os.path.dirname(this.__file__)+'\\'+'trspdr_off.wav'
            this.queue.put(('playsound', soundfile, None))
         if this.survey_online:
            this.survey_online = False
            if this.surveysound.get()=="1":
               soundfile = os.path.dirname(this.__file__)+'\\'+'survey_off.wav'
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
