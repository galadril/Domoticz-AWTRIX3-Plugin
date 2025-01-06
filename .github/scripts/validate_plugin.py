import xml.etree.ElementTree as ET

def validate_plugin_structure(plugin_data):
    try:
        # Parse the plugin data
        root = ET.fromstring(plugin_data)
        # Check for required elements and attributes
        assert root.tag == 'plugin', "'plugin' tag not found"
        
        # Required attributes for the <plugin> tag
        required_attributes = ['key', 'name', 'author', 'version']
        for attr in required_attributes:
            assert root.attrib.get(attr), f"Attribute '{attr}' is missing in 'plugin' tag"

        # Check for <description> tag
        description = root.find('description')
        assert description is not None, "'description' tag not found"

        # Check for <params> tag and required child <param> elements
        params = root.find('params')
        assert params is not None, "'params' tag not found"
        
        required_fields = ['Address', 'Mode1', 'Mode6']
        for field in required_fields:
            param = params.find(f"./param[@field='{field}']")
            assert param is not None, f"'param' with 'field={field}' not found"

        print("Plugin structure is valid.")
        return True
    
    except Exception as e:
        print(f"Validation error: {e}")
        return False
