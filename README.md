# Domoticz Plugin homematicIP Thermostats HmIP-eTRV-B, HmIP-eTRV-2, HmIP-WTH-2
Domoticz plugin for the homematicIP Thermostats HmIP-eTRV-B, HmIP-eTRV-2, HmIP-WTH-2.

# Objectives
* To set the temperature setpoint of a thermostat
* To get the actual temperaturemeasured by the thermostat

![domoticz-plugin-hmip-thermostat-o](https://user-images.githubusercontent.com/47274144/105820050-5552a480-5fb9-11eb-9cb0-fe44d65b0231.png)

## Solution
To set a temperature setpoint or measure the actual temperature, following thermostat devices are supported by this plugin: HmIP-eTRV-B, HmIP-eTRV-2, HmIP-WTH-2.
The homematic IP devices are connected to a homematic IP system.
The homematic IP system used is a [RaspberryMatic](https://raspberrymatic.de/) operating system running the Homematic Central-Control-Unit (CCU).
The CCU has the additional software XML-API CCU Addon installed.
Communication between Domoticz and the CCU is via HTTP XML-API requests with HTTP XML response.

In Domoticz, following devices are created for a thermostat:
(Type,SubType) [XML-API Device Datapoint Type])
* Setpoint (Thermostat,Setpoint) [SET_POINT_TEMPERATURE]
* Temperature (Temp,LaCrosse TX3) [ACTUAL_TEMPERATURE]

The device state is updated every 60 seconds (default).

**Be Aware**
This plugin (only) uses the two device attributes SET_POINT_TEMPERATURE and ACTUAL_TEMPERATURE.
Additional attributes can be easily added to the plugin.

## Hardware
* Raspberry Pi 3B+ (RaspberryMatic System)
* homematicIP Thermostats HmIP-eTRV, HmIP-eTRV-2, HmIP-WTH-2
* Note: Hardware subject to change.

## Software
* Raspberry Pi OS ( Raspbian GNU/Linux 10 buster, kernel 5.4.83-v7l+)
* Domoticz 2020.2 (build 12847)
* RaspberryMatic 3.55.5.20201226 [info](https://raspberrymatic.de/)
* XML-API CCU Addon 1.20 [info](https://github.com/jens-maus/XML-API)
* Python 3.7.3
* Python module ElementTree
* Note: Software versions subject to change.

**Note on the Python Module ElementTree**
The Python Module **ElementTree XML API** is used to parse the XML-API response.
This module is part of the standard package and provides limited support for XPath expressions for locating elements in a tree. 

_Hint_
(Optional)
For full XPath support install the module **ElementPath** from the terminal command-line for Python 2.x and 3.x via pip:
``` 
sudo pip install elementpath
sudo pip3 install elementpath
```

## RaspberryMatic Prepare
The RaspberryMatic system has been setup according [these](https://github.com/jens-maus/RaspberryMatic) guidelines.

The XML-API CCU Addon is required and installed via the HomeMatic WebUI > Settings > Control panel > Additional software (download the latest version from previous URL shared).
**IMPORTANT**
Be aware of the security risk, in case the HomeMatic Control Center can be reached via the Internet without special protection (see XML-API Guidelines).

Next description is based on a the thermostat HmIP-eTRV-2, but also applies to HmIP-eTRV-B and HmIP-WTH-2.

### XML-API Scripts
The XML-API provides various tool scripts, i.e. devices state list, device state or set new value and many more.
The scripts are submitted via HTTP XML-API requests.
The plugin makes selective use of scripts with device id and datapoint id's.
The device id is required to get the state of the device datapoints. The datapoint id's are required to get the state/value of device attributes.

#### Device ID (statelist.cgi)
Get Device ID (attribute "ise_id") from list of all devices with channels and current values: http://ccu-ip-address/addons/xmlapi/statelist.cgi.
From the HTTP XML-API response, the Device ID ("ise_id") is selected by searching for the 
* Device Name (i.e. Thermostat MakeLab) or 
* Device Channel (i.e. HmIP-eTRV-2 000A18A9A64DAC:1). 
The data is obtained from the HomeMatic WebUI Home page > Status and control > Devices.
The Device "ise_id" is required for the plugin parameter _Mode1_.
HTTP XML-API response: Device ID = 1541.
```
...
<device name="Thermostat MakeLab" ise_id="1541" unreach="false" config_pending="false">
	<channel...>
</device>
...
```
This script 
* has to be run once from a browser prior installing the plugin to get the device id as required by the plugin parameter Device ID ("mode1") and the next script.
* is not used in the plugin.

#### Channel Datapoint(s) (state.cgi)
Request the Channel Datapoint(s) for a Device ID to get value(s) for selected attribute(s): http://ccu-ip-address/addons/xmlapi/state.cgi?device_id=DEVICE_ISE_ID

The **Device ID 1541** is used as parameter to get the device state from which the attributes can be selected. 
The HTTP XML-API response lists seven Channels from which **Channel HmIP-eTRV-2 000A18A9A64DAC:1** (as previous shown in the HomeMatic WebUI) is used.
The datapoints used:
* type="ACTUAL_TEMPERATURE" with ise_id="1567" to get the actual temperature. The value is from valuetype 4, i.e. float.
* type="SET_POINT_TEMPERATURE" with ise_id="1584" to get/set the thermostat setpoint. The value is from valuetype 4, i.e. float.
```
<device name="Thermostat MakeLab" ise_id="1541" unreach="false" config_pending="false">
<channel name="Thermostat MakeLab:0" ise_id="1542" index="0" visible="true" operate="true">
	<datapoint name="HmIP-RF.000A18A9A64DAC:0.CONFIG_PENDING" type="CONFIG_PENDING" ise_id="1543" value="false" valuetype="2" valueunit="" timestamp="1611569796" operations="5"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:0.DUTY_CYCLE" type="DUTY_CYCLE" ise_id="1547" value="false" valuetype="2" valueunit="" timestamp="1611569796" operations="5"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:0.LOW_BAT" type="LOW_BAT" ise_id="1549" value="false" valuetype="2" valueunit="" timestamp="1611569796" operations="5"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:0.OPERATING_VOLTAGE" type="OPERATING_VOLTAGE" ise_id="1553" value="3.100000" valuetype="4" valueunit="" timestamp="1611569796" operations="5"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:0.OPERATING_VOLTAGE_STATUS" type="OPERATING_VOLTAGE_STATUS" ise_id="1554" value="0" valuetype="16" valueunit="" timestamp="1611569796" operations="5"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:0.RSSI_DEVICE" type="RSSI_DEVICE" ise_id="1555" value="198" valuetype="8" valueunit="" timestamp="1611569796" operations="5"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:0.RSSI_PEER" type="RSSI_PEER" ise_id="1556" value="189" valuetype="8" valueunit="" timestamp="1611508240" operations="5"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:0.UNREACH" type="UNREACH" ise_id="1557" value="false" valuetype="2" valueunit="" timestamp="1611569796" operations="5"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:0.UPDATE_PENDING" type="UPDATE_PENDING" ise_id="1561" value="false" valuetype="2" valueunit="" timestamp="1610918491" operations="5"/>
</channel>
<channel name="HmIP-eTRV-2 000A18A9A64DAC:1" ise_id="1565" index="1" visible="true" operate="true">
	<datapoint name="HmIP-RF.000A18A9A64DAC:1.ACTIVE_PROFILE" type="ACTIVE_PROFILE" ise_id="1566" value="1" valuetype="16" valueunit="" timestamp="1611569796" operations="7"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:1.ACTUAL_TEMPERATURE" type="ACTUAL_TEMPERATURE" ise_id="1567" value="22.600000" valuetype="4" valueunit="" timestamp="1611569796" operations="5"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:1.ACTUAL_TEMPERATURE_STATUS" type="ACTUAL_TEMPERATURE_STATUS" ise_id="1568" value="0" valuetype="16" valueunit="" timestamp="1611569796" operations="5"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:1.BOOST_MODE" type="BOOST_MODE" ise_id="1569" value="false" valuetype="2" valueunit="" timestamp="1611569796" operations="6"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:1.BOOST_TIME" type="BOOST_TIME" ise_id="1570" value="0" valuetype="16" valueunit="" timestamp="1611569796" operations="5"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:1.CONTROL_DIFFERENTIAL_TEMPERATURE" type="CONTROL_DIFFERENTIAL_TEMPERATURE" ise_id="1571" value="" valuetype="4" valueunit="" timestamp="0" operations="2"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:1.CONTROL_MODE" type="CONTROL_MODE" ise_id="1572" value="" valuetype="16" valueunit="" timestamp="0" operations="2"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:1.DURATION_UNIT" type="DURATION_UNIT" ise_id="1573" value="" valuetype="16" valueunit="" timestamp="0" operations="2"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:1.DURATION_VALUE" type="DURATION_VALUE" ise_id="1574" value="" valuetype="16" valueunit="" timestamp="0" operations="2"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:1.FROST_PROTECTION" type="FROST_PROTECTION" ise_id="1575" value="false" valuetype="2" valueunit="" timestamp="1611569796" operations="5"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:1.LEVEL" type="LEVEL" ise_id="1576" value="0.520000" valuetype="4" valueunit="" timestamp="1611569796" operations="7"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:1.LEVEL_STATUS" type="LEVEL_STATUS" ise_id="1577" value="0" valuetype="16" valueunit="" timestamp="1611569796" operations="5"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:1.PARTY_MODE" type="PARTY_MODE" ise_id="1578" value="false" valuetype="2" valueunit="" timestamp="1611569796" operations="5"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:1.PARTY_SET_POINT_TEMPERATURE" type="PARTY_SET_POINT_TEMPERATURE" ise_id="1579" value="0.000000" valuetype="4" valueunit="" timestamp="0" operations="5"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:1.PARTY_TIME_END" type="PARTY_TIME_END" ise_id="1580" value="" valuetype="20" valueunit="" timestamp="0" operations="7"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:1.PARTY_TIME_START" type="PARTY_TIME_START" ise_id="1581" value="" valuetype="20" valueunit="" timestamp="0" operations="7"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:1.QUICK_VETO_TIME" type="QUICK_VETO_TIME" ise_id="1582" value="0" valuetype="16" valueunit="" timestamp="1611569796" operations="5"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:1.SET_POINT_MODE" type="SET_POINT_MODE" ise_id="1583" value="0" valuetype="16" valueunit="" timestamp="1611569796" operations="7"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:1.SET_POINT_TEMPERATURE" type="SET_POINT_TEMPERATURE" ise_id="1584" value="22.000000" valuetype="4" valueunit="°C" timestamp="1611569796" operations="7"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:1.SWITCH_POINT_OCCURED" type="SWITCH_POINT_OCCURED" ise_id="1585" value="false" valuetype="2" valueunit="" timestamp="1611569796" operations="5"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:1.VALVE_ADAPTION" type="VALVE_ADAPTION" ise_id="1586" value="false" valuetype="2" valueunit="" timestamp="0" operations="7"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:1.VALVE_STATE" type="VALVE_STATE" ise_id="1587" value="4" valuetype="16" valueunit="" timestamp="1611569796" operations="5"/>
	<datapoint name="HmIP-RF.000A18A9A64DAC:1.WINDOW_STATE" type="WINDOW_STATE" ise_id="1588" value="0" valuetype="16" valueunit="" timestamp="1611569796" operations="7"/>
</channel>
<channel name="HmIP-eTRV-2 000A18A9A64DAC:2" ise_id="1589" index="2" visible="true" operate="true"/>
<channel name="HmIP-eTRV-2 000A18A9A64DAC:3" ise_id="1590" index="3" visible="true" operate="true"/>
<channel name="HmIP-eTRV-2 000A18A9A64DAC:4" ise_id="1591" index="4" visible="true" operate="true"/>
<channel name="HmIP-eTRV-2 000A18A9A64DAC:5" ise_id="1592" index="5" visible="true" operate="true"/>
<channel name="HmIP-eTRV-2 000A18A9A64DAC:6" ise_id="1593" index="6" visible="true" operate="true"/>
<channel name="HmIP-eTRV-2 000A18A9A64DAC:7" ise_id="1594" index="7" visible="true" operate="true"/>
</device>
```
This script 
* is used in the plugin to get the device datapoint values in regular check intervals.
#### Change Value (statechange.cgi)
Change the State or Value for a Datapoint: http://ccu-ip-address/addons/xmlapi/statechange.cgi?ise_id=DATAPOINT_ISE_ID&new_value=NEW_VALUE

This script is used by the plugin to set the setpoint via the Domoticz Setpoint device.
The parameters 
* ise_id with DATAPOINT_ISE_ID is the previous determined value for the attribute SET_POINT_TEMPERATURE
* new_value is the Domoticz thermostat setpoint value
Example:
```
http://ccu-ip-address/addons/xmlapi/statechange.cgi?ise_id=1584&new_value=20.5
```

#### Summary
The device id "1541" (for the device named "Thermostat MakeLab") is used to 
* get the actual temperature (ACTUAL_TEMPERATURE)
* set the setpoint (SET_SETPOINT_TEMPERATURE) of the channel "HmIP-eTRV-2 000A18A9A64DAC:1". 

## Domoticz Prepare
Open in a browser, four tabs with the Domoticz GUI Tabs: 
* Setup > Hardware = to add / delete the new hardware
* Setup > Devices = to check the devices created by the new hardware (use button Refresh to get the latest values)
* Setup > Log = to check the installation and check interval cycles for errors
* Active Menu depending Domoticz Devices created/used = to check the devices value
Ensure to have the latest Domoticz version installed: Domoticz GUI Tab Setup > Check for Update

### Domoticz Plugin Installation

### Plugin Folder and File
Each plugin requires a dedicated folder which contains the plugin, mandatory named **plugin.py**.
The folder is named according omematic IP device name. 
``` 
mkdir /home/pi/domoticz/plugins/hmip-thermostat
``` 

Copy the file **plugin.py** to the folder.

### Restart Domoticz
``` 
sudo service domoticz.sh restart
``` 

### Domoticz Add Hardware
**IMPORTANT**
Prior adding the hardware, set in Domoticz GUI > Settings the option to allow new hardware.
If this option is not enabled, no new devices are created.
Check the GUI > Setup > Log as error message Python script at the line where the new device is used
(i.e. Domoticz.Debug("Device created: "+Devices[1].Name))

In the GUI > Setup > Hardware add the new hardware **homematicIP Thermostat (HmIP-eTRV,eTRV-2,WTH-2)**.
Define the hardware parameter:
* CCU IP: The IP address of the homematic CCU. Default: 192.168.1.225.
* Device ID: The device datapoint ise_id - taken from the XMLAPI statelist request. Default: 1541.
* Check Interval (sec): How often the state of the device is checked. Default: 60.
* Debug: Set initially to true. If the plugin runs fine, update to false.

### Add Hardware - Check the Domoticz Log
After adding, ensure to check the Domoticz Log (GUI > Setup > Log)
Example - with hardware name TM (just a name for testing instead using german name "Thermostat MakeLab")
```
2021-01-25 11:56:22.411 (TM) Debug logging mask set to: PYTHON PLUGIN QUEUE IMAGE DEVICE CONNECTION MESSAGE ALL
2021-01-25 11:56:22.411 (TM) 'HardwareID':'13'
2021-01-25 11:56:22.411 (TM) 'HomeFolder':'/home/pi/domoticz/plugins/hmip-thermostat/'
2021-01-25 11:56:22.411 (TM) 'StartupFolder':'/home/pi/domoticz/'
2021-01-25 11:56:22.411 (TM) 'UserDataFolder':'/home/pi/domoticz/'
2021-01-25 11:56:22.411 (TM) 'Database':'/home/pi/domoticz/domoticz.db'
2021-01-25 11:56:22.411 (TM) 'Language':'en'
2021-01-25 11:56:22.411 (TM) 'Version':'1.0.1 (Build 20210125)'
2021-01-25 11:56:22.411 (TM) 'Author':'rwbL'
2021-01-25 11:56:22.411 (TM) 'Name':'TM'
2021-01-25 11:56:22.411 (TM) 'Address':'192.168.1.225'
2021-01-25 11:56:22.411 (TM) 'Port':'0'
2021-01-25 11:56:22.412 (TM) 'Key':'HMIP-THERMOSTAT'
2021-01-25 11:56:22.412 (TM) 'Mode1':'1541'
2021-01-25 11:56:22.412 (TM) 'Mode5':'60'
2021-01-25 11:56:22.412 (TM) 'Mode6':'Debug'
2021-01-25 11:56:22.412 (TM) 'DomoticzVersion':'2020.2 (build 12883)'
2021-01-25 11:56:22.412 (TM) 'DomoticzHash':'1a7e11b7d-modified'
2021-01-25 11:56:22.412 (TM) 'DomoticzBuildTime':'2021-01-24 08:48:01'
2021-01-25 11:56:22.412 (TM) Device count: 0
2021-01-25 11:56:22.412 (TM) Devices:0
2021-01-25 11:56:22.412 (TM) Creating new devices ...
2021-01-25 11:56:22.412 (TM) Creating device 'Setpoint'.
2021-01-25 11:56:22.412 (TM) Device created: TM - Setpoint
2021-01-25 11:56:22.412 (TM) Creating device 'Temperature'.
2021-01-25 11:56:22.413 (TM) Device created: TM - Temperature
2021-01-25 11:56:22.413 (TM) Creating new devices: OK
2021-01-25 11:56:22.413 (TM) Heartbeat set: 60
2021-01-25 11:56:22.413 Python Plugin System: (TM) Pushing 'PollIntervalDirective' on to queue
2021-01-25 11:56:22.413 (TM) Processing 'PollIntervalDirective' message
2021-01-25 11:56:22.413 Python Plugin System: (TM) Heartbeat interval set to: 60.
2021-01-25 11:56:22.131 Status: Python Plugin System: (TM) Started.
2021-01-25 11:56:22.410 Status: Python Plugin System: (TM) Entering work loop.
2021-01-25 11:56:22.410 Status: Python Plugin System: (TM) Initialized version 1.0.1 (Build 20210125), author 'rwbL'
```
**NOTE**
Ignore in case following error occur after creating the plugin. This should only apprear once:
```
2021-01-25 11:56:32.644 Error: dzVents: Error: (3.1.3) Discarding device. No last update info found: {["switchTyp ...
```

### Domoticz Log Entry with Debug=False
The plugin runs every 60 seconds (Heartbeat interval).
The thermostat setpoint has been changed on the radiator to 20.5:
```
2021-01-25 12:01:31.060 (TM) HMIP-THERMOSTAT: Setpoint Update=RaspberryMatic:20.5, Domoticz:21.0
```

The thermostat setpoint has been changed by the Domotiocz Setpoint device to 20.5:
```
2021-01-25 12:11:14.627 (TM) HMIP-THERMOSTAT: Setpoint Update=RaspberryMatic:20.0, Domoticz:20.5
```

The plugin has started with initial update:
```
2021-01-25 12:48:14.919 (TF) HMIP-THERMOSTAT: Setpoint Sync: RaspberryMatic 22.5, Domoticz 0
2021-01-25 12:48:14.919 (TF) HMIP-THERMOSTAT: Setpoint Domoticz initial value 0 updated to 22.5
```

## ToDo
See TODO.md
