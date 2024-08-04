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