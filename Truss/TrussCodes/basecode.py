# Código de exemplo para usar a biblioteca de geometria e análise de treliças. 
# Este código gera uma treliça do tipo Warren, sem nariz e tailboom, e realiza a análise estrutural usando o slientruss3d. 
# Em seguida, os resultados são processados para obter as forças internas e os coeficientes de segurança, e a treliça é plotada em 3D.

import trusslibrary as tl
import numpy as np
import slientruss3d.truss as sl
import matplotlib.pyplot as plt 

comprimento = 480
divisao = 60
d=2.5                                                ## mm
area = np.pi*d**2/4
E = 210000                                         # MPa (N/mm²)
density = 1.5e-6                                   # kg/mm³
I = np.pi*d**4/64
allowablestress = 400                              ## MPa
jointtype = 0                                      ## junta quadrada (nao tem outras implementadas)
trusstype = 3                                      ## 0->warren / 1-> pratt / 2-> howe / 3-> cross 

truss = sl.Truss(dim=3)                                                ## obj Truss de dimensao 3
joints = tl.generatesquarejoints(comprimento, divisao) 
pinados,forces = tl.setstudysquare(joints)
supports = tl.generatesupports(pinados, joints)
members = tl.warrentruss(joints) 

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


print(f"Max compression stress: {maxcompressionstress:.2f} MPa")
print(f"Max tension stress: {maxtensionstress:.2f} MPa")
print(f"Min safety factor (tension): {minSFtension:.2f}")
print(f"Min safety factor (compression): {minSFcompression:.2f}")
print(f"Min safety factor (buckling): {minSFbuckling:.2f}")
print(f"Truss weight: {truss.weight*1000:.3f}g")


tl.plottrussBC(joints, supports, forces, members,view="3d", scale_force=2.0,title=None)   
#tl.plottruss(truss, trussmembers, '3d', elementforces, label = 'Forças internas', title='Warren')
# print(trussmembers)

#print(trussmembers._Member__joint0)
#print(elementforces)