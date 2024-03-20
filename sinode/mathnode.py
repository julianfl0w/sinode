from . import sinode
import numpy as np
from io import BytesIO
import base64

def numpy_array_to_base64(numpy_array):
    with BytesIO() as buffer:
        np.save(buffer, numpy_array)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
