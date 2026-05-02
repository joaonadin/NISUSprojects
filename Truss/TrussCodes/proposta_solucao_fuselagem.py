## Código usado com o intuito de simular casos feitos p/ fuselagem e tailboom em 2025 na geometria treliçada
## https://docs.google.com/presentation/d/16rbXcWlJUOXFzzh1A6XDExLiIhwXzigZzNmH9zUp6ng/edit?slide=id.g3d4e5d1ac37_0_20#slide=id.g3d4e5d1ac37_0_20
## autor: joao_nadin

import trusslibrary as tl
import numpy as np
import slientruss3d.truss as sl
import matplotlib.pyplot as plt 

length = 480
#div_len = 120
div_len = 120                                       ## balsa
#d=6                                               ## mm
d = 17                                              ## mm - balsa
area = np.pi*d**2/4
#E = 210000                                         # MPa (N/mm²)
E = 1600                                            # MPa (N/mm²) - balsa
#density = 1.5e-6                                   # kg/mm³
density = 1.5e-7                                    # kg/mm³ - balsa
I = np.pi*d**4/64
#allowablestress = 400                              ## MPa
allowablestress = 14                               ## MPa - balsa            
jointtype = 0                                      ## junta quadrada (nao tem outras implementadas)
trusstype = 3                                      ## 0->warren / 1-> pratt / 2-> howe / 3-> cross 
truss = sl.Truss(dim=3)                                                ## obj Truss de dimensao 3
joints = tl.generatesquarejoints(length, div_len) 
pinned_section = int(length/div_len)    ## last sec
first_pinned = 4*pinned_section
pinned_nodes = [first_pinned, first_pinned+1, first_pinned+2, first_pinned+3]
F_section = int (0.2 * length/div_len)  ## F1 on last sec - count starts on 0
F_node_1 = int(4 * F_section) + 2   ## picking upper nodes for both - arbitrary!
F_node_2 = F_node_1 + 1
F_bin_section = F_section + 1       ## binary set on next node
F_bin_node_1 = int(4*F_bin_section) + 2
F_bin_node_2 = F_bin_node_1 + 1
ind_moment = 110000                 ## 110Nm to be induced
F_bin = ind_moment / div_len        ## force = moment / distance
forces = [(F_node_1, (0,0,-500-F_bin)), (F_node_2, (0,0,1000-F_bin)), (F_bin_node_1, (0,0, F_bin)), (F_bin_node_2, (0,0, F_bin))]
supports = tl.generatesupports(pinned_nodes, joints)
members = tl.warrentruss(joints) 
#members = tl.pratttruss(joints)

memberType= sl.MemberType(area, E, density)                            ## usando recurso do slientruss

trussmembers = tl.settruss(joints, supports, forces, members, truss, memberType)
truss.Solve()
stress = truss.GetInternalStresses()
elementforces = truss.GetInternalForces()


## pos processamento dos dados
(
maxcompressionstress,
maxtensionstress,
maxcompression,
maxtension,
minSFtension,
minSFcompression,
minSFbuckling,
) = tl.safetycoefanls(truss, trussmembers, stress, elementforces, allowablestress, I, E)

print(f"SF compressão: {minSFcompression:.2f}")
print(f"SF tração: {minSFtension:.2f}")
print(f"SF buckling: {minSFbuckling:.2f}")
print(f"Truss weight: {truss.weight*1000:.2f}g")

#tl.plottrussBC(joints, supports, forces, members,view="3d", scale_force=0.1,title=None)   
tl.plottruss(truss, trussmembers, '3d', elementforces, label = 'Forças internas', title='Warren')