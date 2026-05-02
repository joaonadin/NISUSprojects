## Código usado com o intuito de simular casos feitos p/ fuselagem e tailboom em 2025 na geometria treliçada
## https://docs.google.com/presentation/d/16rbXcWlJUOXFzzh1A6XDExLiIhwXzigZzNmH9zUp6ng/edit?slide=id.g3d4e5d1ac37_0_20#slide=id.g3d4e5d1ac37_0_20
## autor: joao_nadin

import trusslibrary as tl
import numpy as np
import slientruss3d.truss as sl
import matplotlib.pyplot as plt 

length = 560
div_len = 40
d=2                                               ## mm
area = np.pi*d**2/4
E = 210000                                         # MPa (N/mm²)
density = 1.5e-6                                   # kg/mm³
I = np.pi*d**4/64
allowablestress = 400                              ## MPa
jointtype = 0                                      ## junta quadrada (nao tem outras implementadas)
trusstype = 3                                      ## 0->warren / 1-> pratt / 2-> howe / 3-> cross 
truss = sl.Truss(dim=3)                                                ## obj Truss de dimensao 3
joints = tl.generatesquarejoints(length, div_len) 
pinned_section = int(0.15*length/div_len)
first_pinned = 4*pinned_section
pinned_nodes = [first_pinned, first_pinned+1, first_pinned+2, first_pinned+3]
F1_section = length/div_len - 1  ## F1 on last sec - count starts on 0
F2_section = F1_section - 1  ## F2 on last but one sec - for binary insertion
F1_node_1 = int(4 * F1_section)   ## picking lower nodes for both - arbitrary!
F1_node_2 = F1_node_1 + 1
F2_node_1 = int(4 * F2_section)
F2_node_2 = F2_node_1 + 1
F = 70                       ## force
F1 = 1500 / div_len          ## F1 must induce 1500 Nmm on last node

forces = [(F1_node_1, (0,0,-F/2-F1/2)), (F1_node_2, (0,0,-F/2-F1/2)), (F2_node_1, (0,0,F1/2)), (F2_node_2, (0,0,F1/2)) ]
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
print(f"Truss weight: {truss.weight*1000:.3f}g")

tl.plottrussBC(joints, supports, forces, members,view="3d", scale_force=2.0,title=None)   
#tl.plottruss(truss, trussmembers, '3d', elementforces, label = 'Forças internas', title='Warren')