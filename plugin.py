"""
<plugin key="AWTRIX3" name="AWTRIX3" author="Mark Heinis" version="0.0.9" wikilink="http://www.domoticz.com/wiki/plugins/plugin.html" externallink="https://github.com/galadril/Domoticz-AWTRIX3-Plugin">
    <description>
        <p>
        Plugin for integrating AWTRIX3 Smart Pixel Clock with Domoticz. 
        Send messages as notifications or manage custom apps dynamically.
        </p><p>
        Please download icon 39762 as default Domoticz icon on your device: <a href="https://developer.lametric.com/icons">https://developer.lametric.com/icons</a>.
        </p><p>
        More on AWTRIX3 is available on its github project page: <a href="https://github.com/Blueforcer/awtrix3">https://github.com/Blueforcer/awtrix3</a>.
        A list of shared AWTRIX 3 automation flows is available on the <a href="https://flows.blueforcer.de/search?provider=domoticz">AWTRIX Flows website</a>.
        </p>
    </description>
    <params>
        <param field="Address" label="IP Address" width="200px" required="true" default="192.168.1.100"/>
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
import json
import json.decoder
import re

class BasePlugin:
    def __init__(self):
        # Initialization of variables
        self.awtrix_ip = None
        self.custom_app_name = "Domoticz"  # Fixed app name for the custom app
        self.awtrix3_icon_name = "AWTRIX3"  # Fixed icon id
        self.power_unit = 1  # Device ID for the Power
        self.lux_unit = 2  # Device ID for Lux
        self.temp_unit = 3  # Device ID for Temperature/Humidity
        self.push_button_notify = 4  # Device ID for Push Button 1
        self.push_button_app = 5  # Device ID for Push Button 2
        self.push_button_previous = 6  # Device ID for Send Left
        self.push_button_next = 7  # Device ID for Send Right
        self.push_button_rtttl = 8  # Device ID for RTTTL command
        self.push_button_settings = 9  # Device ID for settings command
        self.selector_transition_effect = 10  # Device ID for selector of transition effect
        self.selector_overlay = 11  # Device ID for selector of overlay
        self.color_text = 12  # Device ID for the global text color
        self.brightness_unit = 13  # Device ID for the brightness slider
        self.sleep_button = 14  # New Device ID for the Sleep Button
        
        self.debug_level = 0

        # Read username and password for basic auth
        self.username = ""
        self.password = ""
        self.default_icon = ""

        # The last selected text color
        self.color_white = { "r": 255, "g": 255, "b": 255 }
        self.selected_text_color = self.color_white.copy()

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

        # Load custom icons
        self.load_icons(Images)

        # Create devices if they don't already exist
        self.create_devices()
        
        Domoticz.Heartbeat(30)

    def load_icons(self, Images):
        """Load the custom AWTRIX3 icon."""
        if self.awtrix3_icon_name in Images:
            Domoticz.Debug(f"Icon ID found: {Images[self.awtrix3_icon_name].ID}")
        else:
            Domoticz.Image("AWTRIX3-Icons.zip").Create()
            Domoticz.Log("Icons added from AWTRIX3-Icons.zip")
        
    def create_devices(self):
        if self.power_unit not in Devices:
            Domoticz.Device(Name="Power", Unit=self.power_unit, TypeName="Switch", Image=Images[self.awtrix3_icon_name].ID).Create()
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
        
        if self.selector_transition_effect not in Devices:
            Options = {
                "LevelActions": "|| ||",
                "LevelNames": "Off|Random|Slide|Dim|Zoom|Rotate|Pixelate|Curtain|Ripple|Blink|Reload|Fade",
                "LevelOffHidden": "true",
                "SelectorStyle": "1"
                }
            Domoticz.Device(
                Name="Transition effect",
                Unit=self.selector_transition_effect,
                TypeName="Selector Switch",
                Options=Options
            ).Create()
            Domoticz.Log("Transition effect selector created.")

        if self.selector_overlay not in Devices:
            Options = {
                "LevelActions": "|| ||",
                "LevelNames": "Off|Snow|Rain|Drizzle|Storm|Thunder|Frost", # Off = Clear
                "LevelOffHidden": "false",
                "SelectorStyle": "1"
                }
            Domoticz.Device(
                Name="Overlay",
                Unit=self.selector_overlay,
                TypeName="Selector Switch",
                Options=Options
            ).Create()
            Domoticz.Log("Overlay selector created.")

        if self.color_text not in Devices:
            Domoticz.Device(
                Name="Text color",
                Unit=self.color_text,
                TypeName="RGB"
            ).Create()
            Domoticz.Log("Text color device created.")

        if self.brightness_unit not in Devices:
            Domoticz.Device(
                Name="Brightness",
                Unit=self.brightness_unit,
                TypeName="Dimmer"
            ).Create()
            Domoticz.Log("Brightness slider device created.")
            
        if self.sleep_button not in Devices:
            Domoticz.Device(
                Name="Sleep Mode",
                Unit=self.sleep_button,
                Type=244, Subtype=73, Switchtype=9,
                Description="Send the device into sleep mode for X seconds (input X in the description)"
            ).Create()
            Domoticz.Log("Sleep Mode Push Button created.")
        
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
                        
        elif Unit == self.sleep_button:
            try:
                self.send_api_command("sleep")
                Domoticz.Log(f"Sent sleep command successfully for {sleep_seconds} seconds.")
            except Exception as e:
                Domoticz.Error(f"Error sending sleep command: {e}")
                
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

        elif Unit == self.selector_transition_effect:
            transitionValue = (Level / 10) - 1
            settings = f'{{"TEFF": {transitionValue}}}'
            try:
                self.send_settings_json(settings)
                # Also set the value in the selector again, to confirm that it was set
                Devices[self.selector_transition_effect].Update(nValue=Level, sValue=f"{Level}")
            except Exception as e:
                Domoticz.Error(f"Error sending the transition effect: {e}")
        elif Unit == self.selector_overlay:
            overlayMap = { 0: "clear", 10: "snow", 20: "rain", 30: "drizzle", 40: "storm", 50: "thunder", 60: "frost" }
            overlayName = overlayMap.get(Level, "clear")
            settings = f'{{"OVERLAY": "{overlayName}"}}'
            try:
                self.send_settings_json(settings)
                # Also set the value in the selector again, to confirm that it was set
                Devices[self.selector_overlay].Update(nValue=Level, sValue=f"{Level}")
            except Exception as e:
                Domoticz.Error(f"Error sending the overlay: {e}")

        elif Unit == self.color_text:
            # By default text color will be white
            newColor = self.color_white.copy()
            dimmer_state = 0
            dimmer_level = Level
            if Command == "Off":
                # We will switch back to white
                dimmer_level = 0
            elif Command == "Set Level":
                # Only the level is changed
                # Set the same color as previously
                dimmer_state = 1
                newColor = self.selected_text_color
            else:
                dimmer_state = 1
                if Hue:
                    colorInfo = json.loads(Hue)
                    newColor = { key: colorInfo.get(key, self.color_white[key]) for key in ['r', 'g', 'b'] }
            try:
                settings = f'{{ "TCOL": [{newColor["r"]},{newColor["g"]},{newColor["b"]}] }}'
                self.send_settings_json(settings)
                # Also set the color in the domoticz control, to confirm that it was set
                color = { "ColorMode": 3 }
                color.update(newColor)
                Devices[self.color_text].Update(nValue=dimmer_state, sValue=str(dimmer_level), Color=str(color))
                if dimmer_state:
                    self.selected_text_color.update(newColor)
            except Exception as e:
                Domoticz.Error(f"Error sending the global text color: {e}")

        elif Unit == self.brightness_unit:
            bri = Level
            auto_bri = False
            if Command == "Off":
                bri = 0
                auto_bri = True
            bri = max(0, min(bri, 100))
            settings = f'{{ "ABRI": {int(auto_bri)}, "BRI": {bri} }}'
            try:
                self.send_settings_json(settings)
                Devices[self.brightness_unit].Update(nValue=int(not auto_bri), sValue=str(bri))
            except Exception as e:
                Domoticz.Error(f"Error sending the brightness: {e}")

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

    def _determine_custom_app_name(self, json_data):
        appname = self.custom_app_name
        try:
            jd = json.loads(json_data)
            json_list = jd if isinstance(jd, list) else [jd]
            for app in json_list:
                appname = app.get("appname", "")
                # Only keep valid characters as it will be passed on an URL
                sanitized_appname = re.sub(r'[^a-zA-Z0-9_]', '', appname)
                if sanitized_appname:
                    if sanitized_appname != appname:
                        Domoticz.Error(f"appname: '{appname}' was sanitized to: '{sanitized_appname}'")
                    return sanitized_appname
        except json.decoder.JSONDecodeError as e:
            Domoticz.Error(f"Invalid JSON data passed: {json_data}")

        return self.custom_app_name

    def send_custom_app_json(self, json_data):
        url = f"http://{self.awtrix_ip}/api/custom"
        headers = {"Content-Type": "application/json"}
        p = {"name": self._determine_custom_app_name(json_data) }
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

        try:
            url = f"http://{self.awtrix_ip}/api/settings"
            response = requests.get(url, auth=HTTPBasicAuth(self.username, self.password) if self.username and self.password else None)
            response.raise_for_status()

            settings = response.json()

            # Extract values from the stats response
            val_teff = int(settings.get("TEFF", 1))  # Slide is the default
            selector_value = (val_teff + 1) * 10

            # Update the transition effect device
            Devices[self.selector_transition_effect].Update(nValue=selector_value, sValue=f"{selector_value}")
            Domoticz.Log(f'Updated transition effect device with nValue={selector_value}, sValue="{selector_value}".')

            overlayMap = {"clear": 0, "snow": 10, "rain": 20, "drizzle": 30, "storm": 40, "thunder": 50, "frost": 60 }
            overlay_value = overlayMap.get(settings.get("OVERLAY", "clear"), 0)
            Devices[self.selector_overlay].Update(nValue=overlay_value, sValue=f"{overlay_value}")
            Domoticz.Log(f'Updated overlay device with nValue={overlay_value}, sValue="{overlay_value}".')

            text_color = settings.get("TCOL", None)
            if text_color:
                # Set the color in the domoticz control, to confirm that it was set
                color = { "ColorMode": 3 }
                color["r"] = (text_color >> 16) & 0xFF
                color["g"] = (text_color >> 8) & 0xFF
                color["b"] = text_color & 0xFF
                dimmer_state = 1
                dimmer_level = 50
                if text_color == (256 ** 3) - 1:
                    # The text color is full white, so the custom text color is off
                    dimmer_state = 0
                    dimmer_level = 0
                Devices[self.color_text].Update(nValue=dimmer_state, sValue=str(dimmer_level), Color=str(color))
                Domoticz.Log(f'Updated text color device with nValue={dimmer_state}, sValue="{dimmer_level}", Color={str(color)}.')

            auto_bri = settings.get("ABRI", False)
            bri = int(settings.get("BRI", 50))
            bri = max(1, min(bri, 100))
            Devices[self.brightness_unit].Update(nValue=int(not auto_bri), sValue=str(bri))
            Domoticz.Log(f'Update brightness device with nValue={int(not auto_bri)}, sValue="{bri}"')
        except requests.exceptions.RequestException as e:
            Domoticz.Log(f"Failed to fetch AWTRIX settings: {str(e)}. Skipping update.")
            # Set the transition effect device to 'OFF'
            Devices[self.selector_transition_effect].Update(nValue=20, sValue="0")
            Devices[self.selector_overlay].Update(nValue=0, sValue="0")

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
