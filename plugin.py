# Domoticz Home Automation - Python Plugin homematicIP Thermostat (HmIP-eTRV,eTRV-2,WTH-2)
# For the homematicIP Thermostats HmIP-eTRV, HmIP-eTRV-2, HmIP-WTH-2:
#   * set the setpoint
#   * get the actual temperature
# Dependencies:
# RaspberryMatic XML-API CCU Addon (https://github.com/hobbyquaker/XML-API)
# Library ElementTree (https://docs.python.org/3/library/xml.etree.elementtree.html#)
# Notes:
# 1. After every change: delete the hardware using the plugin homematicIP Thermostat
# 2. After every change: restart domoticz by running from terminal the command: sudo service domoticz.sh restart
# 3. Domoticz Python Plugin Development Documentation (https://www.domoticz.com/wiki/Developing_a_Python_plugin)
# 4. Only two adevice attributes are used. The plugin is flexible to add more attributes as required (examples WTH-2: HUMIDITY, eTRV-2: LEVEL)
#
# Author: Robert W.B. Linn
# Version: See plugin xml definition

"""
<plugin key="HMIP-THERMOSTAT" name="homematicIP Thermostat (HmIP-eTRV,eTRV-2,WTH-2)" author="rwbL" version="1.0.1 (Build 20210125)">
    <description>
        <h2>homematicIP Thermostat (HmIP-eTRV,eTRV-2,WTH-2) v1.0.1</h2>
        <ul style="list-style-type:square">
            <li>Set the setpoint (degrees C)</li>
            <li>Get the actual temperature (degrees C)</li>
            <li>Supported are the devices HmIP-eTRV,eTRV-2,WTH-2</li>
        </ul>
        <h3>Domoticz Devices (Type,SubType) [XML-API Device Datapoint Type]</h3>
        <ul style="list-style-type:square">
            <li>Setpoint (Thermostat,Setpoint) [SET_POINT_TEMPERATURE]</li>
            <li>Temperature (Temp,LaCrosse TX3) [ACTUAL_TEMPERATURE]</li>
        </ul>
        <h3>Hardware Configuration</h3>
        <ul style="list-style-type:square">
            <li>CCU IP Address (default: 192.168.1.225)</li>
            <li>Device ID (default: 1541, get via XML-API script http://ccu-ip-address/addons/xmlapi/statelist.cgi)</li>
            <li>Notes</li>
            <ul style="list-style-type:square">
                <li>The setpoint ID is set after the first check interval.</li>
                <li>After a configuration update, the setpoint is 0. Click the setpoint to set the value or wait for first check interval update.</li>
            </ul>
        </ul>
    </description>
    <params>
        <param field="Address" label="CCU IP" width="200px" required="true" default="192.168.1.225"/>
        <param field="Mode1" label="Device ID" width="75px" required="true" default="1541"/>
        <param field="Mode5" label="Check Interval (sec)" width="75px" required="true" default="60"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug" default="true"/>
                <option label="False" value="Normal"/>
            </options>
        </param>
    </params>
</plugin>
"""

# Set the plugin version
PLUGINVERSION = "v1.0.1"
PLUGINSHORTDESCRIPTON = "HMIP-THERMOSTAT"

## Imports
import Domoticz
import urllib
import urllib.request
from datetime import datetime
import json
import xml.etree.ElementTree as etree

## Domoticz device units used for creating & updating devices
## And the XMLAPI type used to get the value attribute
## Each of the devices have a self variable defined in function init
UNIT_SET_POINT_TEMPERATURE = 1 # TypeName: N/A; Type ID:242 (Name:Thermostat); Subtype ID:1 (Name:Setpoint); Create device use Type=242, Subtype=1
TYPE_SET_POINT_TEMPERATURE = "SET_POINT_TEMPERATURE"

UNIT_ACTUAL_TEMPERATURE = 2   # TypeName: Temperature
TYPE_ACTUAL_TEMPERATURE = "ACTUAL_TEMPERATURE"

# Tasks to perform
## Change the setpoint
TASKSETPOINTTEMPERATURE = 1 
## Get values from the datapoint ACTUAL_TEMPERATURE
TASKGETDATAPOINTS = 2

class BasePlugin:

    def __init__(self):
        # HTTP Connection
        self.httpConn = None
        self.httpConnected = 0
        
        # Task to complete - default is get the datapoints
        self.Task = TASKGETDATAPOINTS

        # Thermostat Datapoints, i.e. Setpoint, LowBat, Temperature
        self.SetPoint = 0       # setpoint in C 
        self.SetPointID = 0     # setpoint datapoint ise_id required to set the setpoint 
        self.Temperature = 0    # actual temperature
               
        # The Domoticz heartbeat is set to every 60 seconds. Do not use a higher value as Domoticz message "Error: hardware (N) thread seems to have ended unexpectedly"
        # The plugin heartbeat is set in Parameter.Mode5 (seconds). This is determined by using a hearbeatcounter which is triggered by:
        # (self.HeartbeatCounter * self.HeartbeatInterval) % int(Parameter.Mode5) = 0
        self.HeartbeatInterval = 60
        self.HeartbeatCounter = 0
        return

    def onStart(self):
        Domoticz.Debug(PLUGINSHORTDESCRIPTON + " " + PLUGINVERSION)
        Domoticz.Debug("onStart called")

        Domoticz.Debug("Debug Mode:" + Parameters["Mode6"])
        if Parameters["Mode6"] == "Debug":
            self.debug = True
            Domoticz.Debugging(1)
            DumpConfigToLog()

        # if there no devices, create these
        Domoticz.Debug("Devices:" + str(len(Devices)) )
        if (len(Devices) == 0):
            try:
                Domoticz.Debug("Creating new devices ...")
                
                ## 1 - SET_POINT_TEMPERATURE - TypeName: Thermostat (Type=242, Subtype=1)
                Domoticz.Device(Name="Setpoint", Unit=UNIT_SET_POINT_TEMPERATURE, Type=242, Subtype=1, Used=1).Create()
                Domoticz.Debug("Device created: "+Devices[UNIT_SET_POINT_TEMPERATURE].Name)

                ## 2 - ACTUAL_TEMPERATURE - TypeName: Temperature (Type=80, Subtype=5)
                Domoticz.Device(Name="Temperature", Unit=UNIT_ACTUAL_TEMPERATURE, Type=80, Subtype=5, Used=1).Create()
                Domoticz.Debug("Device created: "+Devices[UNIT_ACTUAL_TEMPERATURE].Name)

                Domoticz.Debug("Creating new devices: OK")
            except:
                Domoticz.Error("Creating new devices: Failed. Check settings if new hardware allowed")
        else:
            # NOT USED - if there are devices, go for sure and update options. Exampe selector switch
            # Options = { "LevelActions": "", "LevelNames": Parameters["Mode3"], "LevelOffHidden": "false", "SelectorStyle": "0" }
            Domoticz.Debug("Devices already created.")

        # Heartbeat
        Domoticz.Debug("Heartbeat set: "+Parameters["Mode5"])
        Domoticz.Heartbeat(self.HeartbeatInterval)

        return

    def onStop(self):
        Domoticz.Debug("Plugin is stopping.")

    # Send the url parameter (GET request)
    # If task = actualtemperature then to obtain device state information in xml format
    # If task = setpoint then set the setpoint usig switch using the self.switchstate
    # The http response is parsed in onMessage()
    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")
        if (Status == 0):
            Domoticz.Debug("CCU connected successfully.")
            self.httpConnected = 1

            # request all datapoints for the device id to get the actual data for the defined datapoints
            if self.Task == TASKGETDATAPOINTS:
                ## url example = 'http://192.168.1.225/addons/xmlapi/state.cgi?device_id=' .. ID_DEVICE;
                url = '/addons/xmlapi/state.cgi?device_id=' + Parameters["Mode1"]
                
            # set the new setpoint
            if self.Task == TASKSETPOINTTEMPERATURE:
                ## url example = 'http://192.168.1.225/addons/xmlapi/statechange.cgi?ise_id=1584&new_value=
                if self.SetPointID > 0:
                    url = '/addons/xmlapi/statechange.cgi?ise_id=' + str(self.SetPointID) + '&new_value=' + str(self.SetPoint)
                    Domoticz.Log(PLUGINSHORTDESCRIPTON + ": Setpoint changed to " + str(self.SetPoint))
                else:
                    Domoticz.Error("Can not set the setpoint because the Datapoint ID is 0. Wait for the next heartbeat cycle to update.")
                    return
                    
            Domoticz.Debug(url)
            # define the senddata parameters (JSON)
            sendData = { 'Verb' : 'GET',
                         'URL'  : url,
                         'Headers' : { 'Content-Type': 'text/xml; charset=utf-8', \
                                       'Connection': 'keep-alive', \
                                       'Accept': 'Content-Type: text/html; charset=UTF-8', \
                                       'Host': Parameters["Address"], \
                                       'User-Agent':'Domoticz/1.0' }
                       }
            
            # Send the data and disconnect
            self.httpConn.Send(sendData)
            self.httpConn.Disconnect
            return
        else:
            self.httpConnected = 0
            Domoticz.Error("HTTP connection to CCU failed ("+str(Status)+") to: "+Parameters["Address"]+":"+Parameters["Port"]+" with error: "+Description)
            return

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")

        # If not conected, then leave
        if self.httpConnected == 0:
            return

        # Parse the JSON Data Object with keys Status (Number) and Data (ByteArray)
        ## 200 is OK
        responseStatus = int(Data["Status"])
        Domoticz.Debug("STATUS=responseStatus:" + str(responseStatus) + " ;Data[Status]="+Data["Status"])

        ## decode the data using the encoding as given in the xml response string
        responseData = Data["Data"].decode('ISO-8859-1')
        ## Domoticz.Debug("DATA=" + responseData)

        if (responseStatus != 200):
            Domoticz.Error("XML-API response faillure: " + str(responseStatus) + ";" + resonseData)
            return

        # Parse the xml string 
        # Get the xml tree - requires several conversions
        tree = etree.fromstring(bytes(responseData, encoding='utf-8'))
        
        # Handle the respective task to update the domoticz devices
        if self.Task == TASKGETDATAPOINTS:
            Domoticz.Debug("TASKGETDATAPOINTS")
            # init helper vars
            atv = 0.0       #actualtemperaturevalue
            spvrm = 0.0     #setpointvalueraspberrymatic
            spvdom = 0.0    #setpointvaluedomoticz
                        
            # ACTUAL_TEMPERATURE
            ## <datapoint name="HmIP-RF.000A18A9A64DAC:1.ACTUAL_TEMPERATURE" type="ACTUAL_TEMPERATURE" ise_id="1567" value="23.000000" valuetype="4" valueunit="" timestamp="1610965660"/>
            ## Get the value for datapoint actual_temperature & update the device and log
            actualtemperaturevalue = tree.find(".//datapoint[@type='" + TYPE_ACTUAL_TEMPERATURE + "']").attrib['value']
            ## convert the raspberrymatic value to float
            atv = float(actualtemperaturevalue)
            ## update the device if raspmatic value not equal domoticz value
            if atv != self.Temperature:
                self.Temperature = atv
                Devices[UNIT_ACTUAL_TEMPERATURE].Update( nValue=0, sValue=str(round(atv,2)) )
                Domoticz.Debug("T Update=" + Devices[UNIT_ACTUAL_TEMPERATURE].sValue)

            # SETPOINT_TEMPERATURE
            ## <datapoint name="HmIP-RF.000A18A9A64DAC:1.SET_POINT_TEMPERATURE" type="SET_POINT_TEMPERATURE" ise_id="1584" value="20.000000" valuetype="4" valueunit="°C" timestamp="1611476084"/>
            ## Get the setpointid ise_id if 0 (initial state). the setpointid is reuired to set the setpoint via xmlapi request
            if self.SetPointID == 0:
                spid = tree.find(".//datapoint[@type='" + TYPE_SET_POINT_TEMPERATURE + "']").attrib['ise_id']
                self.SetPointID = int(spid)
                Domoticz.Debug("SetpointID set=" + str(self.SetPointID))
            # Get the value for datapoint set_point_temperature & update the device and log
            setpointtemperaturevalue = tree.find(".//datapoint[@type='" + TYPE_SET_POINT_TEMPERATURE + "']").attrib['value']
            ## setpoint value raspberrymatic
            spvrm = float(setpointtemperaturevalue)
            ## Update the setpoint if changed by homematic or manual and not equal domoticz setpoint
            if spvrm != self.SetPoint:
                Devices[UNIT_SET_POINT_TEMPERATURE].Update( nValue=1, sValue= str(spvrm) )    
                Domoticz.Log(PLUGINSHORTDESCRIPTON + ": Setpoint Sync RaspberryMatic " + str(spvrm) + ", Domoticz " + str(self.SetPoint))
                if self.SetPoint == 0:
                    Domoticz.Log(PLUGINSHORTDESCRIPTON + ": Setpoint Domoticz initial value " + str(self.SetPoint) + " updated to " + str(spvrm))
                # Domoticz.Debug(PLUGINSHORTDESCRIPTON + ":Setpoint Update=RM:" + str(spvrm) + ", DOM:" + str(self.SetPoint))
            self.SetPoint = spvrm
            
        if self.Task == TASKSETPOINTTEMPERATURE:
            Domoticz.Debug("TASKSETPOINTTEMPERATURE")
            # Update the thermostat
            Devices[UNIT_SET_POINT_TEMPERATURE].Update( nValue=1, sValue= str(self.SetPoint) )    
            # NOT REQUIRED = Devices[UNIT_SET_POINT_TEMPERATURE].Refresh()    
        return

    # Handle oncomand for:
    # Set the setpoint - Create http connection, the setpoint is set in onConnect
    def onCommand(self, Unit, Command, Level, Hue):
        # Unit 1 - UNIT_SET_POINT_TEMPERATURE: Parameter: 'Set Level', Level: 18.5
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        if (Unit == UNIT_SET_POINT_TEMPERATURE):
            ## Set the new setpoint temperature
            self.SetPoint = Level
            Domoticz.Debug("T Setpoint=" + str(self.SetPoint))
            # Create IP connection and connect - see further onConnect where the parameters are send
            self.httpConn = Domoticz.Connection(Name="CCU-"+Parameters["Address"], Transport="TCP/IP", Protocol="HTTP", Address=Parameters["Address"], Port="80")
            self.httpConn.Connect()
            self.httpConnected = 0
            self.Task = TASKSETPOINTTEMPERATURE
        return

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")

    def onHeartbeat(self):
        self.HeartbeatCounter = self.HeartbeatCounter + 1
        Domoticz.Debug("onHeartbeat called. Counter=" + str(self.HeartbeatCounter * self.HeartbeatInterval) + " (Heartbeat=" + Parameters["Mode5"] + ")")
        # check the heartbeatcounter against the heartbeatinterval
        if (self.HeartbeatCounter * self.HeartbeatInterval) % int(Parameters["Mode5"]) == 0:
            try:
                # Create IP connection
                self.httpConn = Domoticz.Connection(Name="CCU-"+Parameters["Address"], Transport="TCP/IP", Protocol="HTTP", Address=Parameters["Address"], Port="80")
                self.httpConn.Connect()
                self.httpConnected = 0
                self.Task = TASKGETDATAPOINTS
                return
            except:
                Domoticz.Error("IP connection failed. Check settings and restart Domoticz.")
                return

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

#
## Generic helper functions
#

def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

"""
# <TODO>
## Sync the setpoint value in case the thermostat has been changed manual.
def syncSetpoint(self,setpoint):
        Domoticz.Debug("syncSetpoint " + str(setpoint) )

        ## Set the new setpoint temperature based on the selector switch level
        ## Convert the level 0,10,20 ... to temperature 0,19,20,12 ...
        self.SetPointLevel = Level
        ## Get the setpoint index 0,1,2 from the level to get the setpoint from the setpointlist
        setpointIndex = Level
        if setpointIndex > 0:
            setpointIndex = int(round(Level/10))
        ## Get the setpoint temperature from the setpointlist
        self.SetPoint = self.SetPointList[setpointIndex]
        Domoticz.Debug("T Setpoint=" + self.SetPoint)
        return
"""
