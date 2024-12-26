"""
<plugin key="AWTRIX3" name="AWTRIX3" author="Mark Heinis" version="0.0.5" wikilink="http://www.domoticz.com/wiki/plugins/plugin.html" externallink="https://github.com/galadril/Domoticz-AWTRIX3-Plugin">
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
        self.power_unit = 1  # Device ID for the Power
        self.lux_unit = 2  # Device ID for Lux
        self.temp_unit = 3  # Device ID for Temperature/Humidity
        self.push_button_notify = 4  # Device ID for Push Button 1
        self.push_button_app = 5  # Device ID for Push Button 2
        self.push_button_previous = 6  # Device ID for Send Left
        self.push_button_next = 7  # Device ID for Send Right
        self.push_button_rtttl = 8  # Device ID for RTTTL command
        self.push_button_settings = 9  # Device ID for settings command
        self.debug_level = 0

        # Read username and password for basic auth
        self.username = ""
        self.password = ""
        self.default_icon = ""

    def onStart(self):
        Domoticz.Log("AWTRIX Plugin started.")
        
        # Read parameters
        self.awtrix_ip = Parameters["Address"]
        self.debug_level = int(Parameters["Mode6"])
        self.username = Parameters["Username"]
        self.password = Parameters["Password"]
        self.default_icon = Parameters["Mode1"]

        if self.debug_level > 0:
            Domoticz.Debugging(self.debug_level)
            Domoticz.Debug(f"Debug level set to: {self.debug_level}")
            Domoticz.Debug(f"AWTRIX IP: {self.awtrix_ip}")

        # Create devices if they don't already exist
        self.create_devices()
        
        Domoticz.Heartbeat(30)
        
    def create_devices(self):
        if self.power_unit not in Devices:
            Domoticz.Device(Name="Power", Unit=self.power_unit, TypeName="Switch").Create()
            Domoticz.Log("Power Device created.")
            self.send_notify_message(self.default_icon, "Domoticz")

        if self.lux_unit not in Devices:
            Domoticz.Device(Name="Lux", Unit=self.lux_unit, TypeName="Illumination").Create()
            Domoticz.Log("Lux Device created.")

        if self.temp_unit not in Devices:
            Domoticz.Device(Name="Temperature", Unit=self.temp_unit, TypeName="Temp+Hum").Create()
            Domoticz.Log("Temp+Hum Device created.")

        if self.push_button_notify not in Devices:
            Domoticz.Device(
                Name="Send Notification",
                Unit=self.push_button_notify,
                Type=244, Subtype=73, Switchtype=9,
                Description="Enter notification text here"
            ).Create()
            Domoticz.Log("Notification Push Button created.")

        if self.push_button_app not in Devices:
            Domoticz.Device(
                Name="Send Custom App",
                Unit=self.push_button_app,
                Type=244, Subtype=73, Switchtype=9,
                Description="Enter custom app text here"
            ).Create()
            Domoticz.Log("Custom App Push Button created.")
            
        if self.push_button_previous not in Devices:
            Domoticz.Device(
                Name="Previous App",
                Unit=self.push_button_previous,
                Type=244, Subtype=73, Switchtype=9,
                Description="Trigger the 'previousapp' API command"
            ).Create()
            Domoticz.Log("Send Previous Push Button created.")

        if self.push_button_next not in Devices:
            Domoticz.Device(
                Name="Next App",
                Unit=self.push_button_next,
                Type=244, Subtype=73, Switchtype=9,
                Description="Trigger the 'nextapp' API command"
            ).Create()
            Domoticz.Log("Send Next Push Button created.")

        if self.push_button_rtttl not in Devices:
            Domoticz.Device(
                Name="RTTTL Command",
                Unit=self.push_button_rtttl,
                Type=244, Subtype=73, Switchtype=9,
                Description="The Simpsons:d=4,o=5,b=160:c.6,e6,f#6,8a6,g.6,e6,c6,8a,8f#,8f#,8f#,2g,8p,8p,8f#,8f#,8f#,8g,a#.,8c6,8c6,8c6,c6"
            ).Create()
            Domoticz.Log("RTTTL Command Push Button created.")

        if self.push_button_settings not in Devices:
            Domoticz.Device(
                Name="Send Settings",
                Unit=self.push_button_settings,
                Type=244, Subtype=73, Switchtype=9,
                Description='{"KEY": "Enter JSON formatted settings here"}'
            ).Create()
            Domoticz.Log("Settings Push Button created.")
        
    def onStop(self):
        Domoticz.Log("AWTRIX Plugin stopped.")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log(f"Command received: Unit={Unit}, Command={Command}, Level={Level}, Hue={Hue}")
        
        if Unit == self.push_button_rtttl:
            description = Devices[Unit].Description
            if description:
                try:
                    self.send_api_command_payload("rtttl", description)
                    Domoticz.Log(f"RTTTL command sent successfully: {description}")
                except Exception as e:
                    Domoticz.Error(f"Error sending RTTTL command: {e}")
                    
        elif Unit == self.push_button_previous:
            try:
                self.send_api_command("previousapp")
                Domoticz.Log("Triggered 'previousapp' command successfully.")
            except Exception as e:
                Domoticz.Error(f"Error triggering 'previousapp': {e}")

        elif Unit == self.push_button_next:
            try:
                self.send_api_command("nextapp")
                Domoticz.Log("Triggered 'nextapp' command successfully.")
            except Exception as e:
                Domoticz.Error(f"Error triggering 'nextapp': {e}")

        elif Unit == self.push_button_notify:
            description = Devices[Unit].Description.strip()
            if not description:
                Domoticz.Error("Description field is empty. Cannot send data.")
                return

            try:
                # Case 1: JSON input for Notify
                if description.startswith("{") and description.endswith("}"):
                    self.send_notify_json(description)
                    Domoticz.Log("Sent JSON data to Notify API.")
                    
                # Case 2: JSON input for Notify
                elif description.startswith("[") and description.endswith("]"):
                    self.send_notify_json(description)
                    Domoticz.Log("Sent JSON data to Notify API.")
                
                # Case 3: Icon;Message input for Notify
                elif ";" in description:
                    icon, message = description.split(";", 1)
                    self.send_notify_message(icon.strip(), message.strip())
                    Domoticz.Log(f"Sent Notify with icon: {icon.strip()} | message: {message.strip()}")
                
                # Case 4: Message only for Notify (default icon)
                else:
                    self.send_notify_message(self.default_icon, description)
                    Domoticz.Log(f"Sent Notify with default icon: {self.default_icon} | message: {description}")
            except Exception as e:
                Domoticz.Error(f"Error processing Notify description: {e}")

        elif Unit == self.push_button_app:
            description = Devices[Unit].Description.strip()
            if not description:
                Domoticz.Error("Description field is empty. Cannot send data.")
                return

            try:
                # Case 1: JSON input for Custom App
                if description.startswith("{") and description.endswith("}"):
                    self.send_custom_app_json(description)
                    Domoticz.Log("Sent JSON data to Custom App API.")
                    
                # Case 2: JSON input for Custom App
                elif description.startswith("[") and description.endswith("]"):
                    self.send_custom_app_json(description)
                    Domoticz.Log("Sent JSON data to Custom App API.")
                
                # Case 3: Icon;Message input for Custom App
                elif ";" in description:
                    icon, message = description.split(";", 1)
                    self.send_custom_app_message(icon.strip(), message.strip())
                    Domoticz.Log(f"Sent Custom App data with icon: {icon.strip()} | message: {message.strip()}")
                
                # Case 4: Message only for Custom App (default icon)
                else:
                    self.send_custom_app_message(self.default_icon, description)
                    Domoticz.Log(f"Sent Custom App data with default icon: {self.default_icon} | message: {description}")
            except Exception as e:
                Domoticz.Error(f"Error processing Custom App description: {e}")

        elif Unit == self.power_unit:  # Power Device
            self.send_power_device(Command)

        elif Unit == self.push_button_settings:
            description = Devices[Unit].Description.strip()
            if not description:
                Domoticz.Error("Description field is empty. Cannot send data.")
                return

            try:
                # JSON input for settings
                if description.startswith("{") and description.endswith("}"):
                    self.send_settings_json(description)
                    Domoticz.Log("Sent JSON data to settings API.")
                else:
                    Domoticz.Error(f"Description is not JSON formatted: {description}")
            except Exception as e:
                Domoticz.Error(f"Error processing settings description: {e}")

        else:
            Domoticz.Error("Unknown Unit in onCommand.")

    def send_api_command(self, command):
        url = f"http://{self.awtrix_ip}/api/{command}"
        try:
            response = requests.post(url, auth=HTTPBasicAuth(self.username, self.password) if self.username and self.password else None)
            response.raise_for_status()
            Domoticz.Log(f"API command '{command}' executed successfully.")
        except requests.exceptions.RequestException as e:
            Domoticz.Error(f"Failed to send '{command}' command: {e}")

    def send_api_command_payload(self, endpoint, payload):
        url = f"http://{Parameters['Address']}:{Parameters['Port']}/api/{endpoint}"
        headers = {"Content-Type": "application/json"}
        auth = (Parameters['Username'], Parameters['Password']) if 'Username' in Parameters and 'Password' in Parameters else None
        response = requests.post(url, headers=headers, json=payload, auth=auth)
        response.raise_for_status()

    def send_notify_json(self, json_data):
        url = f"http://{self.awtrix_ip}/api/notify"
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(url, data=json_data, headers=headers, auth=(self.username, self.password))
            response.raise_for_status()
            Domoticz.Log(f"Notify JSON sent successfully: {response.text}")
        except requests.exceptions.RequestException as e:
            Domoticz.Error(f"Failed to send Notify JSON: {e}")

    def send_notify_message(self, icon, message):
        url = f"http://{self.awtrix_ip}/api/notify"
        data = {
            "icon": icon,
            "text": message
        }
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(url, json=data, headers=headers, auth=(self.username, self.password))
            response.raise_for_status()
            Domoticz.Log(f"Notify message sent successfully: {response.text}")
        except requests.exceptions.RequestException as e:
            Domoticz.Error(f"Failed to send Notify message: {e}")

    def send_custom_app_json(self, json_data):
        url = f"http://{self.awtrix_ip}/api/custom"
        headers = {"Content-Type": "application/json"}
        p = {"name": self.custom_app_name}
        try:
            response = requests.post(url, data=json_data, params=p, headers=headers, auth=(self.username, self.password))
            response.raise_for_status()
            Domoticz.Log(f"Custom App JSON sent successfully: {response.text}")
        except requests.exceptions.RequestException as e:
            Domoticz.Error(f"Failed to send Custom App JSON: {e}")

    def send_custom_app_message(self, icon, message):
        url = f"http://{self.awtrix_ip}/api/custom"
        p = {"name": self.custom_app_name}
        data = {
            "icon": icon,
            "text": message
        }
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(url, json=data, params=p, headers=headers, auth=(self.username, self.password))
            response.raise_for_status()
            Domoticz.Log(f"Custom App message sent successfully: {response.text}")
        except requests.exceptions.RequestException as e:
            Domoticz.Error(f"Failed to send Custom App message: {e}")

    def send_settings_json(self, json_data):
        url = f"http://{self.awtrix_ip}/api/settings"
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(url, data=json_data, headers=headers, auth=(self.username, self.password))
            response.raise_for_status()
            Domoticz.Log(f"Settings JSON sent successfully: {response.text}")
        except requests.exceptions.RequestException as e:
            Domoticz.Error(f"Failed to send settings JSON: {e}")

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
