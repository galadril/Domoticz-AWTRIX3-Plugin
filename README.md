

The **Awtrix3 Domoticz Plugin** allows you to interact with your **Awtrix3 Smart Pixel Clock** directly from Domoticz.  

Easily send **notifications**, manage **custom apps**, adjust **brightness**, control **effects**, and toggle the clock's power—all without leaving your Domoticz dashboard.


## Features

-   **Send Notifications**: Push messages and icons to the clock via the `/api/notify` endpoint.
-   **Custom Apps**: Create or update app-specific messages using `/api/custom`.
-   **Toggle Power**: Easily turn the clock on or off.


## Getting Started

To get the plugin running, follow these simple steps:

### Prerequisites

-   Domoticz installed on your system.
-   Awtrix3 Smart Pixel Clock connected to your network.

### Installation

1.  Clone the repository:
    
    ```sh
    git clone https://github.com/galadril/Domoticz-AWTRIX3-Plugin.git
    
    ```
    
2.  Copy the plugin to your Domoticz plugin folder:
    
    ```sh
    cp -r Domoticz-AWTRIX3-Plugin /path/to/domoticz/plugins/
    
    ```
    
3.  Restart Domoticz to load the plugin:
    
    ```sh
    sudo service domoticz.sh restart
    
    ```
    
4.  Add the plugin in Domoticz through **Hardware Settings** and configure the IP address and other parameters.


## Usage

The plugin adds text devices for notify (notifications) and app. Both work the same way, but sending data as app message, or as notification.

    Input format: `<icon_id>,<message_text>`  
    Example: `1, Hello World!` sends a notification with icon ID 1 and message `Hello 
    
-   **Power**:  
    Toggle the device on or off


## Updating

To update:
* Go in your Domoticz directory using a command line and open the plugins directory then the Domoticz-AWTRIX3-Plugin directory.
* Run: ```git pull```
* Restart Domoticz.


## Usage

The plugin will automatically discover compatible Quatt devices on your local network and create/update devices in Domoticz. 


## Debugging

You can enable debugging by setting the Debug parameter to a value between 1 and 6 in the Setup > Hardware dialog. More information about the debugging levels can be found in the Domoticz documentation.


## Change log

| Version | Information |
| ----- | ---------- |
| 0.0.1 | Initial version |

----------

## Acknowledgements

-   [Domoticz Plugin Wiki](https://www.domoticz.com/wiki/Plugins)
-   [Awtrix3 Official Documentation](https://awtrixdocs.blueforcer.de)

----------

# Donation

If you like to say thanks, you could always buy me a cup of coffee (/beer)!   
(Thanks!)  
[![PayPal donate button](https://img.shields.io/badge/paypal-donate-yellow.svg)](https://www.paypal.me/markheinis)
    
