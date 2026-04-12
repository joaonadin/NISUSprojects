import numpy as np
from slientruss3d.type import MemberType

def set_memberType(d, E, density):
    area = np.pi * d**2 / 4
    I = np.pi * d **4 / 64
    mt = MemberType(area, E, density)
    return mt, I