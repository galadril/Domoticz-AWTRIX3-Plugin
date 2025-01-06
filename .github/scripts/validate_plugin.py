import xml.etree.ElementTree as ET
import sys

def extract_plugin_header(file_path):
    """Extract the XML plugin header from a specified file."""
    plugin_header = []
    with open(file_path, "r") as f:
        lines = f.readlines()
        header_started = False
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('"""') and not header_started:
                header_started = True
                # Remove the initial triple quotes, but keep this line as it may contain more content.
                plugin_header.append(stripped_line[3:].lstrip())
            elif stripped_line.endswith('"""') and header_started:
                # Append up to before closing triple quotes.
                plugin_header.append(stripped_line[:-3])
                break
            elif header_started:
                plugin_header.append(line.rstrip())  # Add each line, removing newline characters

    return '\n'.join(plugin_header)

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

if __name__ == "__main__":
    file_path = "plugin.py"
    
    plugin_data = extract_plugin_header(file_path)
    if plugin_data:
        print("INFO: Extracted plugin header:")
        print(plugin_data)
        validate_plugin_structure(plugin_data)
    else:
        print("ERROR: No XML header found in plugin.py")
        sys.stdout.flush()
