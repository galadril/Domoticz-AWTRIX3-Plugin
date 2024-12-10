
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

## 🚀 Usage
### Push Button Notifications
The description of the push buttons (`Send Notification` and `Send Custom App`) can be used in three ways:
1. **JSON:**
   - Example: `{ "text": "600 L", "icon": 9766 }`
2. **Icon;Message:**
   - Format: `icon;message`
   - Example: `9766;Check the temperature!`
3. **Message:**
   - Example: `Hello, AWTRIX!`

Check this sample dzVents script to in sequence push device states with icons to the device
[Samples](https://github.com/galadril/Domoticz-AWTRIX3-Plugin/blob/master/samples/dzvents-sample.txt)

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

### Icons
To display icons on the AWTRIX3 device, you need to manually upload them. You can fetch icons from the [LaMetric Developer Site](https://developer.lametric.com/icons).

- **Default Domoticz icon:** 39762

You can find the icon pack under the `/icons` directory in the GitHub repository.

For more details on AWTRIX3 and how to upload/setup icons:
[AWTRIX Icons Setup](https://blueforcer.github.io/awtrix3/#/icons)

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

## 🚀 Updates and Contributions
This project is open-source and contributions are welcome! Visit the GitHub repository for more information: [Domoticz-AWTRIX3-Plugin](https://blueforcer.github.io/awtrix3/#/api?id=custom-apps-and-notifications).

## 🙏 Acknowledgements
- [Domoticz Plugin Wiki](https://www.domoticz.com/wiki/Plugins)
- [Awtrix3 Official Documentation](https://awtrixdocs.blueforcer.de)

# ☕ Donation
If you like to say thanks, you could always buy me a cup of coffee (/beer)!
(Thanks!)
[![PayPal donate button](https://img.shields.io/badge/paypal-donate-yellow.svg)](https://www.paypal.me/markheinis)
