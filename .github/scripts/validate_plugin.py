import xml.etree.ElementTree as ET
import sys

def validate_plugin_structure(plugin_data):
    print("INFO: Starting plugin structure validation.")
    try:
        # Parse the plugin data
        root = ET.fromstring(plugin_data)
        print("INFO: XML parsed successfully.")
        
        # Check for the 'plugin' root element
        print(f"DEBUG: Checking if root element is 'plugin': Found '{root.tag}'")
        assert root.tag == 'plugin', "'plugin' tag not found"

        # Required attributes for the <plugin> tag
        required_attributes = ['key', 'name', 'author', 'version']
        for attr in required_attributes:
            value = root.attrib.get(attr)
            print(f"DEBUG: Checking for attribute '{attr}': Found '{value}'")
            assert value, f"Attribute '{attr}' is missing in 'plugin' tag"

        # Check for <description> tag
        description = root.find('description')
        print(f"DEBUG: Checking for 'description' element: {'Found' if description is not None else 'Not found'}")
        assert description is not None, "'description' tag not found"

        # Check for <params> tag and required child <param> elements
        params = root.find('params')
        print(f"DEBUG: Checking for 'params' element: {'Found' if params is not None else 'Not found'}")
        assert params is not None, "'params' tag not found"

        # List required fields in the <param> tags
        required_fields = ['Address', 'Mode1', 'Mode6']
        for field in required_fields:
            param = params.find(f"./param[@field='{field}']")
            print(f"DEBUG: Checking for 'param' with 'field={field}': {'Found' if param is not None else 'Not found'}")
            assert param is not None, f"'param' with 'field={field}' not found"
        
        print("INFO: Plugin structure is valid.")
        sys.stdout.flush()  # Ensures the outputs are flushed and displayed
        return True

    except AssertionError as e:
        print(f"ERROR: Validation error: {e}")
        sys.stdout.flush()
        return False
    except ET.ParseError as e:
        print(f"ERROR: XML parsing error: {e}")
        sys.stdout.flush()
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error during validation: {e}")
        sys.stdout.flush()
        return False
