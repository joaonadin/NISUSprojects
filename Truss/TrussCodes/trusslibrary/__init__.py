import seaborn as sns
sns.set()
from slientruss3d.truss import Truss
from slientruss3d.type  import SupportType, MemberType
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import json
np.bool8 = np.bool_

from .constants import TRUSS_DIMENSION
from .geometry import generatesquarejoints, generatesupports, crosstruss, warrentruss, pratttruss, howetruss, addnosejoints, addtailboom, setgeom, splitnosetrusstailboom, set_memberType  
from .study import setstudysquare, setstudyfull
from .analysis import safetycoefanls, settruss, analyzetruss
from .plotting import plottruss, plottrussBC
from .utils import save_table, create_member_diameters_dicts