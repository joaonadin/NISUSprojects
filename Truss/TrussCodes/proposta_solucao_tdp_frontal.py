
import trusslibrary as tl
import numpy as np
import slientruss3d.truss as sl
import matplotlib.pyplot as plt 
from trusslibrary.geometry.members import set_memberType

def get_lg_joints(lado, altura):                                 ## creating square truss
    """
    Recebe lado e altura do trem de pouso e retorna as coordenadas dos pontos A B C D E, onde E é o ponto da roda.
    """
    joints = []
    A = (0, 0,  0)
    B = (0, lado, 0)
    C = (lado, 0, 0)
    D = (lado, lado, 0)
    E = (lado/2, lado/2, -altura)
    joints.append(A)
    joints.append(B)
    joints.append(C)
    joints.append(D)
    joints.append(E)
    return joints

def get_lg_members():
    members = []
    members.append((0, 1))
    members.append((0, 2))
    members.append((1, 3))
    members.append((2, 3))
    members.append((0, 4))
    members.append((1, 4))
    members.append((2, 4))
    members.append((3, 4))
    return members

def get_lg_supports(pinados):
    supports = len(joints) * [sl.SupportType.NO]
    for node_id in pinados:
        supports[node_id] = sl.SupportType.PIN
    return supports

truss = sl.Truss(dim=3)                                               
joints = get_lg_joints(100, 150)
jointids = np.arange(0, len(joints), 1)   # getting joint ids
pinados = jointids[-4:]                 ## last 4 nodes pinned
lower_node_id = jointids[-1]           ## node E is the one with the payload
forces = [(lower_node_id, (0, 0, 500))]
pinados = [0, 1, 2, 3]   ## nodes A, B, C, D are pinned
supports = get_lg_supports(pinados)
members = get_lg_members()

d = 3                                            ## mm
E = 210000                                         # MPa (N/mm²)
density = 1.5e-6                                   # kg/mm³
allowablestress = 400                              ## MPa
memberType, I = set_memberType(d, E, density)  ## usando recurso do slientruss

trussmembers = tl.settruss(joints, supports, forces, members, truss, memberType)
truss.Solve()
stress = truss.GetInternalStresses()
elementforces = truss.GetInternalForces()
displacements = truss.GetDisplacements(isProtect=True)


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
print(f"SF flambagem: {minSFbuckling:.2f}") 
print(f"Truss weight: {truss.weight*1000:.3f}g")

print(displacements)
# tl.plottrussBC(joints, supports, forces, members,view="3d", scale_force=2.0,title=None)   
tl.plottruss(truss, trussmembers, '3d', elementforces, label = 'Forças internas', title='Warren')
# print(trussmembers)
