
# Domoticz AWTRIX3 Plugin 🎉

**Plugin for Integrating AWTRIX3 Smart Pixel Clock with Domoticz**

![AWTRIX3 Domoticz](https://github.com/galadril/Domoticz-AWTRIX3-Plugin/blob/master/images/awtrix_domoticz.gif?raw=true)

## 🌟 Overview
Dive into the world of smart home technology by integrating your AWTRIX3 Smart Pixel Clock with Domoticz! This plugin lets you send messages as notifications, manage custom apps dynamically, control power, fetch and display temperature, humidity, and illumination stats, and utilize push buttons for notifications or custom app text.

## ⚡ Features
- **Send Messages as Notifications:** Use the Domoticz interface to send notification messages to your AWTRIX3 device.
- **Manage Custom Apps:** Dynamically send custom applications to your AWTRIX3 device.
- **Power Control:** Toggle the power state of the AWTRIX3 display.
- **Temperature, Humidity, and Illumination:** Fetch and display temperature, humidity, and illumination stats.
- **Push Button Notifications:** Use virtual devices to trigger notifications or custom applications based on button input.
- **Send RTTTL Sounds:** Use virtual devices to play RTTTL sounds on the device.
- **Send Settings:** Use virtual devices to change settings on the device.
- **Debugging Options:** Multiple levels of debugging to help you get precise information about the plugin activities.

## 🛠 Installation
1. **Download the Plugin:**
   - Clone the plugin repository: `git clone https://github.com/galadril/Domoticz-AWTRIX3-Plugin`
   - Navigate to the plugin directory: `cd Domoticz-AWTRIX3-Plugin`
2. **Install Dependencies:**
   - Ensure you have `requests` module installed: `pip install requests`
3. **Add to Domoticz:**
   - Open the Domoticz interface and go to `Setup -> Hardware`.
   - Select `AWTRIX3` from the list of hardware types.
   - Fill in the required fields such as IP Address, Username and Password (if applicable), and Debug level.

## ⚙️ Configuration
### Parameters
- **IP Address:** The IP address of your AWTRIX3 device.
- **Username:** The username for basic authentication (optional).
- **Password:** The password for basic authentication (optional).
- **Default Icon ID:** Default icon ID to be used in notifications.
- **Debug Level:** Choose the level of debug information you want to receive.

### Devices
- **Power Device:** Toggles the power state of the AWTRIX3 device.
- **Lux Device:** Displays the illumination levels.
- **Temp+Hum Device:** Displays temperature and humidity levels with comfort index.
- **Send Notification:** Virtual device to send notifications via the AWTRIX3 API.
- **Send Custom App:** Virtual device to send custom applications data via the AWTRIX3 API.
- **Send Settings:** Virtual device to send settings via the AWTRIX3 API.
- **Next App:** Navigate to the next app via the AWTRIX3 API.
- **Previous App:** Navigate to the previous app via the AWTRIX3 API.
- **RTTTL:** Start a RTTTL Melodie on the device.
- **Transition effect:** A selector to specify the transition between the applications.
- **Overlay:** A selector to specify a 'weather' overlay to be shown on the AWTRIX3.
- **Text color:** A RGB color selector to change the global color text color. 
- **Brightness:** Allows to control the (auto) brightness of the AWTRIX3.

## 🚀 Usage
### Push Button Notifications
The description of the push buttons (`Send Notification` and `Send Custom App`) can be used in three ways:
1. **JSON:**
   - Example: `{ "text": "600 L", "icon": 9766 }`
   - Multi page example `[{ "text": "600 L", "icon": 9766 }, { "text": "364 W", "icon": 95 }]`
2. **Icon;Message:**
   - Format: `icon;message`
   - Example: `9766;Check the temperature!`
3. **Message:**
   - Example: `Hello, AWTRIX!`

See flows for Domoticz here:
https://flows.blueforcer.de/search?provider=domoticz

Check this sample dzVents script to in sequence push device states with icons to the device
[Samples](https://github.com/galadril/Domoticz-AWTRIX3-Plugin/blob/master/samples/dzvents-sample.txt)

Or this script to adjust the overlay based on the weather
[Samples](https://github.com/galadril/Domoticz-AWTRIX3-Plugin/blob/master/samples/dzvents-weather-overlay-sample.txt)

If you like to use dzVents to set the description of the notification and custom app switches, you need to allow 127.0.0.* as trusted network under Settings/Security


### Example JSONs
**Simple Notification JSON:**
```json
{
  "text": "21 C",
  "icon": 9766
}
```
For more details on all JSON options:
[Custom Apps and Notifications](https://blueforcer.github.io/awtrix3/#/api?id=custom-apps-and-notifications)

If multiple dzVents scripts are used to send different 'Custom Apps' to the AWTRIX3
using the 'Send Custom App' button, it is best to also include an "appname" key and an appropriate
value in the JSON data, as otherwise the 'Custom Apps' of the other dzVents scripts will be overwritten.
 
### Icons
To display icons on the AWTRIX3 device, you need to manually upload them. You can fetch icons from the [LaMetric Developer Site](https://developer.lametric.com/icons).

- **Default Domoticz icon:** 39762

You can find the icon pack under the `/icons` directory in the GitHub repository.

For more details on AWTRIX3 and how to upload/setup icons:
[AWTRIX Icons Setup](https://blueforcer.github.io/awtrix3/#/icons)

### Settings
The description of the push button (`Send settings`) should be set to a JSON object, using the keys and values as defined by the [AWTRIX3 API](https://blueforcer.github.io/awtrix3/#/api?id=change-settings).

#### Example JSONs for changing the global settings
| Example                                       | JSON                                              |
|-----------------------------------------------|---------------------------------------------------|
| Disable battery, humidity and temperature     | `{ "BAT": false, "HUM": false, "TEMP": false }`   |
| Enable weekday display, and use a green color | `{ "WD": true, "WDCA": [0, 255, 0] }`             |
| Show every app for 10 seconds with 2 s change | `{ "ATIME": 10, "TSPEED": 2000 }`                 |

## 🌈 Samples
![Samples1](https://github.com/galadril/Domoticz-AWTRIX3-Plugin/blob/master/images/awtrix_door.gif?raw=true)
![Samples2](https://github.com/galadril/Domoticz-AWTRIX3-Plugin/blob/master/images/awtrix_fan.gif?raw=true)
![Samples3](https://github.com/galadril/Domoticz-AWTRIX3-Plugin/blob/master/images/awtrix_power.gif?raw=true)
![Samples4](https://github.com/galadril/Domoticz-AWTRIX3-Plugin/blob/master/images/awtrix_water.gif?raw=true)

## 📅 Change log
| Version | Information |
| ------- | ----------- |
|   0.0.1 | Initial version |
|   0.0.2 | Fixed issue with Power Device |
|   0.0.3 | Fixes on first use of hardware |
|   0.0.4 | Added buttons for next and previous app navigation |
|   0.0.5 | Added RTTTL Sounds |
|   0.0.6 | Added devices to change settings |
|   0.0.8 | Set custom app names + custom app icon |
|   0.0.9 | Added sleep button |

## 🚀 Updates and Contributions
This project is open-source and contributions are welcome! Visit the GitHub repository for more information: [Domoticz-AWTRIX3-Plugin](https://blueforcer.github.io/awtrix3/#/api?id=custom-apps-and-notifications).

## 🙏 Acknowledgements
- [Domoticz Plugin Wiki](https://www.domoticz.com/wiki/Plugins)
- [Awtrix3 Official Documentation](https://blueforcer.github.io/awtrix3/#/README)


## 🧩 Using the Template Repository

If you're interested in creating a new Domoticz plugin, you can use our [template repository](https://github.com/galadril/Domoticz-Python-Plugin-Template). 
This can serve as a foundation for developing similar projects, making it easier and faster to get started.

# ☕ Donation
If you like to say thanks, you could always buy me a cup of coffee (/beer)!
(Thanks!)
[![PayPal donate button](https://img.shields.io/badge/paypal-donate-yellow.svg)](https://www.paypal.me/markheinis)
