import  trusslibrary as tl
import numpy as np
import slientruss3d.truss as sl
import os

d = 3

E = 210000                                         # MPa (N/mm²)
density = 1.5e-6                                   # kg/mm³
allowablestress = 400                              ## MPa

mt, I = tl.set_memberType(d, E, density)


member_types = {
    'fuselage_1':     mt
}

joints = tl.generatesquarejoints(divisao=54, n1=2, divisao2=54, n2=0)

# ============ GERAR GEOMETRIA ============
truss = sl.Truss(dim=3)
members = tl.setgeom(joints, trussgeom=0, nosegeom=0, tailboomgeom=0)

m= 50
F = m * 9.81
pinados = [0, 1, 2, 3]
forces = [(8, (F//4, 0, 0)), (9, (F//4, 0, 0)), (10, (F//4, 0, 0)), (11, (F//4, 0, 0)) ]
supports = [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0] ## 2 roller em x, 1 pinado completo, 0 livre

# # ============ CRIAR ESTRUTURA COM DIÂMETROS VARIÁVEIS ============
trussmembers = tl.settruss(joints, supports, forces, members, truss, mt, member_types)

# # ============ RESOLVER E EXTRAIR RESULTADOS ============
truss.Solve()
stress = truss.GetInternalStresses()
elementforces = truss.GetInternalForces()
reactionforces = truss.GetResistances()

member_diameters = tl.create_member_diameters_dicts(truss, members, E)

tl.print_global_analysis(truss, trussmembers, stress, elementforces, allowablestress,
                          member_types, joints, members, E)


masses = tl.get_masses(members, joints, truss, density, E, member_types_dict=member_types)
print(masses)
print(truss.weight)


###### PLOT FUNCTIONS 

tl.plottruss(truss, trussmembers, '3d', elementforces, label='Forças internas', title='Treliça Completa')

# tl.plottrussBC(joints, supports, forces, members,view="3d", scale_force=2.0,title='Condições de Contorno - Treliça Completa'
#               , member_diameters=member_diameters)

#tl.plot_truss_fluid(joints, members)

#tl.plottruss_sections(truss, trussmembers, members, joints,'side', member_types, 2.0)

