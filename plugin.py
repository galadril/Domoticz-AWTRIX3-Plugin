"""
<plugin key="Domoticz-AWTRIX3-Plugin" name="Awtrix3" author="Mark Heinis" version="0.0.1 wikilink="http://www.domoticz.com/wiki/plugins/plugin.html" externallink="https://github.com/galadril/Domoticz-AWTRIX3-Plugin">
    <description>
        Plugin for integrating Awtrix3 Smart Pixel Clock with Domoticz. 
        Send messages as notifications or manage custom apps dynamically.
    </description>
    <params>
        <param field="Address" label="Awtrix IP Address" width="200px" required="true" default="192.168.1.100"/>
        <param field="Username" label="Username" width="200px" required="false" default=""/>
        <param field="Password" label="Password" width="200px" required="false" default="" password="true"/>
        <param field="Mode1" label="Default Icon ID" width="100px" required="true" default="39762"/>
        <param field="Mode6" label="Debug" width="200px">
            <options>
                <option label="None" value="0" default="true"/>
                <option label="Python Only" value="2"/>
                <option label="Basic Debugging" value="62"/>
                <option label="Basic+Messages" value="126"/>
                <option label="Connections Only" value="16"/>
                <option label="Connections+Queue" value="144"/>
                <option label="All" value="-1"/>
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import requests

class BasePlugin:
    def __init__(self):
        self.awtrix_ip = None
        self.custom_app_name = "Domoticz"  # Fixed app name for the custom app
        self.default_icon_id = None
        self.notify_unit = 1  # Device ID for the Notify device
        self.custom_unit = 2  # Device ID for the Custom App device
        self.debug_level = 0

    def onStart(self):
        Domoticz.Log("Awtrix Plugin started.")
        
        # Read parameters
        self.awtrix_ip = Parameters["Address"]
        self.default_icon_id = int(Parameters["Mode1"])
        self.debug_level = int(Parameters["Mode6"])

        if self.debug_level > 0:
            Domoticz.Debugging(self.debug_level)
            Domoticz.Debug(f"Debug level set to: {self.debug_level}")
            Domoticz.Debug(f"Awtrix IP: {self.awtrix_ip}, Default Icon ID: {self.default_icon_id}")

        # Create Notify Device
        if self.notify_unit not in Devices:
            Domoticz.Device(Name="Notify Device", Unit=self.notify_unit, TypeName="Text").Create()
            Domoticz.Log("Notify Device created.")
        
        # Create Custom App Device
        if self.custom_unit not in Devices:
            Domoticz.Device(Name="Custom App Device", Unit=self.custom_unit, TypeName="Text").Create()
            Domoticz.Log("Custom App Device created.")

    def onStop(self):
        Domoticz.Log("Awtrix Plugin stopped.")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log(f"Command received: Unit={Unit}, Command={Command}, Level={Level}, Hue={Hue}")
        
        if Unit == self.notify_unit:  # Notify Device
            self.send_notify_device(Command)
        elif Unit == self.custom_unit:  # Custom App Device
            self.send_custom_app_device(Command)
        else:
            Domoticz.Error("Unknown Unit in onCommand.")

    def send_notify_device(self, Command):
        """
        Sends a notification to the Awtrix API.
        Command format: icon_id,message_text
        """
        try:
            icon_id, message = Command.split(",", 1)
            icon_id = int(icon_id.strip())
            
            # Prepare API payload
            url = f"http://{self.awtrix_ip}/api/notify"
            payload = {
                "icon": icon_id if icon_id > 0 else self.default_icon_id,
                "text": message.strip()
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            Domoticz.Log(f"Notification sent: Icon={icon_id}, Text='{message}'")
        except ValueError:
            Domoticz.Error("Invalid Command format. Expected format: 'icon_id,message_text'")
        except requests.exceptions.RequestException as e:
            Domoticz.Error(f"Failed to send notification: {str(e)}")

    def send_custom_app_device(self, Command):
        """
        Updates the custom app on the Awtrix API.
        Command format: icon_id,message_text
        """
        try:
            icon_id, message = Command.split(",", 1)
            icon_id = int(icon_id.strip())
            
            # Prepare API payload
            url = f"http://{self.awtrix_ip}/api/custom"
            payload = {
                "name": self.custom_app_name,
                "icon": icon_id if icon_id > 0 else self.default_icon_id,
                "text": message.strip()
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            Domoticz.Log(f"Custom app updated: Name='{self.custom_app_name}', Icon={icon_id}, Text='{message}'")
        except ValueError:
            Domoticz.Error("Invalid Command format. Expected format: 'icon_id,message_text'")
        except requests.exceptions.RequestException as e:
            Domoticz.Error(f"Failed to update custom app: {str(e)}")

    def onHeartbeat(self):
        pass

# Instantiate the plugin
global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

