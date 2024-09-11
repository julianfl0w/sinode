from . import sinode
import numpy as np
from io import BytesIO
import base64

def numpy_array_to_base64(numpy_array):
    with BytesIO() as buffer:
        np.save(buffer, numpy_array)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')


def base64_to_numpy_array(base64_string):
    decoded_data = base64.b64decode(base64_string)
    with BytesIO(decoded_data) as buffer:
        numpy_array = np.load(buffer)
        return numpy_array
        
def toJsonDict(self):
    if isinstance(self, sinode.Node):
        attributes_dict = {}  # Initialize an empty dictionary
        for attr in dir(self):
            if attr.startswith('__') or callable(getattr(self, attr)):
                continue
            if attr == "apex" or attr == "ancestors":
                continue

            attr_value = getattr(self, attr)  # Retrieve the value of the attribute
            print(f"Attribute: {attr}, Type: {type(attr_value).__name__}")  # Print the attribute name and type
            attributes_dict[attr] = toJsonDict(attr_value)  # Add the attribute and its value to the dictionary
        return attributes_dict
    
    elif isinstance(self, list):
        return [toJsonDict(e) for e in self]

    elif isinstance(self, dict):
        attributes_dict = {}  # Initialize an empty dictionary
        for k, v in self.items():
            attributes_dict[k] = toJsonDict(v)
        return attributes_dict
    
    elif isinstance(self, np.ndarray):
        if attr_value.ndim == 1:
            return numpy_array_to_base64(attr_value)
        elif attr_value.ndim == 2:
            return [numpy_array_to_base64(attr_value[i, :]) for i in range(attr_value.shape[0])]

    return self
