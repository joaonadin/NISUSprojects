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
from .geometry import generatesquarejoints, generatesupports, crosstruss, warrentruss, pratttruss, howetruss, addnosejoints, addtailboom, add_landing_gear_tower, setgeom, split_parts, set_memberType, get_matched_joints_tower, addtailboom_straight, add_tailboom_encaixe 
from .geometry import add_landing_gear_pyramid, settruss, get_section_label
from .study import setstudysquare, setstudyfull, set_study_tailboom, set_study_landinggear
from .analysis import safetycoefanls, analyzetruss
from .plotting import plottruss, plottrussBC, plot_truss_fluid, plottruss_sections, truss_deliverable
from .utils import save_table, create_member_diameters_dicts, get_masses, print_global_analysis
from .utils import export_apdl, print_material_lengths, export_spaceclaim