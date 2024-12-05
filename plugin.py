"""
<plugin key="AWTRIX3" name="AWTRIX3" author="Mark Heinis" version="0.0.1" wikilink="http://www.domoticz.com/wiki/plugins/plugin.html" externallink="https://github.com/galadril/Domoticz-AWTRIX3-Plugin">
    <description>
        Plugin for integrating AWTRIX3 Smart Pixel Clock with Domoticz. 
        Send messages as notifications or manage custom apps dynamically.
        
        Please download 39762 as default Domoticz icon on your device: 
        https://developer.lametric.com/icons
        
        More on AWTRIX3:
        https://github.com/Blueforcer/awtrix3
    </description>
    <params>
        <param field="Address" label="IP Address" width="200px" required="true" default="92.168.1.100"/>
        <param field="Username" label="Username" width="200px" required="false" default=""/>
        <param field="Password" label="Password" width="200px" required="false" default="" password="true"/>
        <param field="Mode1" label="Default Icon ID" width="100px" required="true" default="39762"/>
        <param field="Mode6" label="Debug" width="200px">
            <options>
                <option label="None" value="0"  default="true" />
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
from requests.auth import HTTPBasicAuth

class BasePlugin:
    def __init__(self):
        # Initialization of variables
        self.awtrix_ip = None
        self.custom_app_name = "Domoticz"  # Fixed app name for the custom app
        self.notify_unit = 1  # Device ID for the Notify device
        self.custom_unit = 2  # Device ID for the Custom App device
        self.power_unit = 3  # Device ID for the Power
        self.lux_unit = 4  # Device ID for Lux
        self.temp_unit = 6  # Device ID for Temperature/Humidity
        self.push_button_unit_1 = 7  # Device ID for Push Button 1
        self.push_button_unit_2 = 8  # Device ID for Push Button 2
        self.debug_level = 0

        # Read username and password for basic auth
        self.username = ""
        self.password = ""

    def onStart(self):
        Domoticz.Log("AWTRIX Plugin started.")
        
        # Read parameters
        self.awtrix_ip = Parameters["Address"]
        self.debug_level = int(Parameters["Mode6"])
        self.username = Parameters["Username"]
        self.password = Parameters["Password"]

        if self.debug_level > 0:
            Domoticz.Debugging(self.debug_level)
            Domoticz.Debug(f"Debug level set to: {self.debug_level}")
            Domoticz.Debug(f"AWTRIX IP: {self.awtrix_ip}")

        # Create devices if they don't already exist
        self.create_devices()
        
        Domoticz.Heartbeat(30)

    def create_devices(self):
        """ Creates devices if they don't already exist """
        # Create devices only if they don't exist
        if self.notify_unit not in Devices:
            Domoticz.Device(Name="Notify Device", Unit=self.notify_unit, TypeName="Text").Create()
            Domoticz.Log("Notify Device created.")
        
        if self.custom_unit not in Devices:
            Domoticz.Device(Name="Custom App Device", Unit=self.custom_unit, TypeName="Text").Create()
            Domoticz.Log("Custom App Device created.")
            self.send_notify_device("Connected Domoticz")
        
        if self.power_unit not in Devices:
            Domoticz.Device(Name="Power", Unit=self.power_unit, TypeName="Switch").Create()
            Domoticz.Log("Power Device created.")
        
        if self.lux_unit not in Devices:
            Domoticz.Device(Name="Lux", Unit=self.lux_unit, TypeName="Illumination").Create()
            Domoticz.Log("Lux Device created.")
        
        if self.temp_unit not in Devices:
            Domoticz.Device(Name="Temperature", Unit=self.temp_unit, TypeName="Temp+Hum").Create()
            Domoticz.Log("Temp+Hum Device created.")
        
        # Create Push Button devices
        if self.push_button_unit_1 not in Devices:
            Domoticz.Device(Name="Send Notification", Unit=self.push_button_unit_1, Type=244, Subtype=73, Switchtype=9).Create()
        
        if self.push_button_unit_2 not in Devices:
            Domoticz.Device(Name="Send Custom App", Unit=self.push_button_unit_2, Type=244, Subtype=73, Switchtype=9).Create()
        
    def onStop(self):
        Domoticz.Log("AWTRIX Plugin stopped.")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log(f"Command received: Unit={Unit}, Command={Command}, Level={Level}, Hue={Hue}")
        
        if Unit == self.notify_unit:  # Notify Device
            self.send_notify_device(Command)
        elif Unit == self.custom_unit:  # Custom App Device
            self.send_custom_app_device(Command)
        elif Unit == self.power_unit:  # Power Device
            self.send_power_device(Command)
        elif Unit == self.push_button_unit_1:  # Push Button 1
            self.handle_push_button_1()
        elif Unit == self.push_button_unit_2:  # Push Button 2
            self.handle_push_button_2()
        else:
            Domoticz.Error("Unknown Unit in onCommand.")

    def handle_push_button_1(self):
        """ Handle the action for Push Button 1 """
        # Get the text value from the Notify device and send it
        notify_device = Devices[self.notify_unit]
        message = notify_device.sValue
        self.send_notify_device(message)

    def handle_push_button_2(self):
        """ Handle the action for Push Button 2 """
        # Get the text value from the Custom App device and send it
        custom_device = Devices[self.custom_unit]
        message = custom_device.sValue
        self.send_custom_app_device(message)

    def send_notify_device(self, Command):
        """ Sends a notification to the Awtrix API. Command format: icon_id,message_text """
        try:
            if self.is_device_reachable():
                # Use the default icon if no custom icon is provided
                icon_id = Parameters["Mode1"]  # Get default icon ID from plugin parameters
                parts = Command.split(",", 1)
                
                # If there's only one part (message), use the default icon
                if len(parts) == 1:
                    message = parts[0].strip()
                else:
                    message = parts[1].strip()

                # Prepare API payload
                url = f"http://{self.awtrix_ip}/api/notify"
                payload = {"text": message, "icon": icon_id}  # Add icon_id to payload

                # Send the request with Basic Authentication if username/password are provided
                if self.username and self.password:
                    response = requests.post(url, json=payload, auth=HTTPBasicAuth(self.username, self.password))
                else:
                    response = requests.post(url, json=payload)

                response.raise_for_status()

                Domoticz.Log(f"Notification sent: Text='{message}' with Icon ID={icon_id}")
        except requests.exceptions.RequestException as e:
            Domoticz.Log("AWTRIX device is unreachable. Skipping notification.")

    def send_custom_app_device(self, Command):
        """ Updates the custom app on the Awtrix API. Command format: icon_id,message_text """
        try:
            if self.is_device_reachable():
                # Use the default icon if no custom icon is provided
                icon_id = Parameters["Mode1"]  # Get default icon ID from plugin parameters
                parts = Command.split(",", 1)
                
                # If there's only one part (message), use the default icon
                if len(parts) == 1:
                    message = parts[0].strip()
                else:
                    message = parts[1].strip()

                # Prepare API payload
                url = f"http://{self.awtrix_ip}/api/custom"
                payload = {
                    "name": self.custom_app_name,
                    "text": message,
                    "icon": icon_id  # Add icon_id to payload
                }

                # Send the request with Basic Authentication if username/password are provided
                if self.username and self.password:
                    response = requests.post(url, json=payload, auth=HTTPBasicAuth(self.username, self.password))
                else:
                    response = requests.post(url, json=payload)

                response.raise_for_status()

                Domoticz.Log(f"Custom app updated: Name='{self.custom_app_name}', Text='{message}' with Icon ID={icon_id}")
        except requests.exceptions.RequestException as e:
            Domoticz.Log("AWTRIX device is unreachable. Skipping custom app update.")

    def send_power_device(self, Command):
        """ Toggles the power on/off for the AWTRIX device """
        power_state = 1 if Command.upper() == "ON" else 0
        if not self.is_device_reachable():
            # If device is unreachable, set power state to OFF
            Devices[self.power_unit].Update(nValue=0, sValue="OFF")
            return

        url = f"http://{self.awtrix_ip}/api/power"
        payload = {"power": power_state}
        
        try:
            # Send the request with Basic Authentication if username/password are provided
            if self.username and self.password:
                response = requests.post(url, json=payload, auth=HTTPBasicAuth(self.username, self.password))
            else:
                response = requests.post(url, json=payload)
            
            response.raise_for_status()
            Devices[self.power_unit].Update(nValue=power_state, sValue="ON" if power_state else "OFF")
            Domoticz.Log(f"Power toggled {'ON' if power_state else 'OFF'}")
        except requests.exceptions.RequestException as e:
            Domoticz.Log("AWTRIX device is unreachable. Skipping power toggle.")

    def is_device_reachable(self):
        """ Check if the AWTRIX device is reachable via HTTP GET request """
        try:
            url = f"http://{self.awtrix_ip}/api/stats"
            response = requests.get(url, auth=HTTPBasicAuth(self.username, self.password) if self.username and self.password else None)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def fetch_device_stats(self):
        """ Fetches the device stats from the AWTRIX API and updates Domoticz devices """
        if not self.is_device_reachable():
            Domoticz.Log("AWTRIX device is unreachable. Skipping stats fetch.")
            return

        try:
            url = f"http://{self.awtrix_ip}/api/stats"
            response = requests.get(url, auth=HTTPBasicAuth(self.username, self.password) if self.username and self.password else None)
            response.raise_for_status()

            stats = response.json()

            # Extract values from the stats response
            val_temp = "{}".format(stats.get("temp", 0))  # Temperature
            val_hum = "{}".format(stats.get("hum", 0))    # Humidity
            val_bat = stats.get("bat", 0)    # Battery level
            
            # Comfort level logic based on humidity
            val_comfort = "0"
            if float(val_hum) < 40:
                val_comfort = "2"
            elif float(val_hum) <= 70:
                val_comfort = "1"
            elif float(val_hum) > 70:
                val_comfort = "3"
            
            # Update the Temp+Hum device with nValue and sValue
            Devices[self.temp_unit].Update(nValue=0, sValue=f"{val_temp};{val_hum};{val_comfort}", BatteryLevel=val_bat)
            Domoticz.Log(f"Updated Temp+Hum device with nValue=0, sValue={val_temp};{val_hum};{val_comfort}, BatteryLevel={val_bat}%")

            # Update Lux device with nValue and sValue
            Devices[self.lux_unit].Update(nValue=int(stats["lux"]), sValue=f"{stats['lux']} Lux")
            Domoticz.Log(f"Updated Lux device with nValue={int(stats['lux'])}, sValue={stats['lux']} Lux")

            # Set the Power device state based on the "matrix" field from the stats response
            matrix_state = stats.get("matrix", False)
            if matrix_state:
                Devices[self.power_unit].Update(nValue=1, sValue="ON", BatteryLevel=val_bat)
                Domoticz.Log("AWTRIX matrix is ON, Power device set to ON.")
                Domoticz.Log(f"Battery level updated to {val_bat}% on Power device.")
            else:
                Devices[self.power_unit].Update(nValue=0, sValue="OFF", BatteryLevel=val_bat)
                Domoticz.Log("AWTRIX matrix is OFF, Power device set to OFF.")
                Domoticz.Log(f"Battery level updated to {val_bat}% on Power device.")

        except requests.exceptions.RequestException as e:
            Domoticz.Log(f"Failed to fetch AWTRIX stats: {str(e)}. Skipping update.")
            # Set the Power device state to OFF (0) if there's an error fetching stats
            Devices[self.power_unit].Update(nValue=0, sValue="OFF")


    def onHeartbeat(self):
        """ Periodic task to fetch device stats and update the devices """
        self.fetch_device_stats()

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
