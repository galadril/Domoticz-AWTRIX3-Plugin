import xml.etree.ElementTree as ET
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def validate_plugin_structure(plugin_data):
    logging.info("Starting plugin structure validation.")
    try:
        # Parse the plugin data
        root = ET.fromstring(plugin_data)
        logging.info("XML parsed successfully.")
        
        # Check for the 'plugin' root element
        logging.debug(f"Checking if root element is 'plugin': Found '{root.tag}'")
        assert root.tag == 'plugin', "'plugin' tag not found"

        # Required attributes for the <plugin> tag
        required_attributes = ['key', 'name', 'author', 'version']
        for attr in required_attributes:
            value = root.attrib.get(attr)
            logging.debug(f"Checking for attribute '{attr}': Found '{value}'")
            assert value, f"Attribute '{attr}' is missing in 'plugin' tag"

        # Check for <description> tag
        description = root.find('description')
        logging.debug(f"Checking for 'description' element: {'Found' if description is not None else 'Not found'}")
        assert description is not None, "'description' tag not found"

        # Check for <params> tag and required child <param> elements
        params = root.find('params')
        logging.debug(f"Checking for 'params' element: {'Found' if params is not None else 'Not found'}")
        assert params is not None, "'params' tag not found"

        # List required fields in the <param> tags
        required_fields = ['Address', 'Mode1', 'Mode6']
        for field in required_fields:
            param = params.find(f"./param[@field='{field}']")
            logging.debug(f"Checking for 'param' with 'field={field}': {'Found' if param is not None else 'Not found'}")
            assert param is not None, f"'param' with 'field={field}' not found"

        logging.info("Plugin structure is valid.")
        return True

    except AssertionError as e:
        logging.error(f"Validation error: {e}")
        return False
    except ET.ParseError as e:
        logging.error(f"XML parsing error: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error during validation: {e}")
        return False
