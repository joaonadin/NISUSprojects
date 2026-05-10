import numpy as np
from slientruss3d.type import MemberType

def set_memberType(d, E, density):
    area = np.pi * d**2 / 4
    I = np.pi * d**4 / 64
    mt = MemberType(area, E, density)
    mt.I = I  # anexa direto no objeto
    mt.d = d  # útil para plots de diâmetro também
    mt.E = E
    mt.density = density
    return mt, I