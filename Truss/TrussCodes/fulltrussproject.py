import  trusslibrary as tl
import numpy as np
import slientruss3d.truss as sl
import os

## ORIGINAL
d_fuselage_1 = 2
d_fuselage_2 = 2
d_nose = 2
d_tailboom = 2
d_landing_gear = 2

## REDUZIDO 
# d_fuselage_1 = 3
# d_fuselage_2 = 2
# d_nose = 1.5
# d_tailboom = 1.5
# d_landing_gear = 2


optimal_slenderness_ratio = 18

base_unit_fuselage_1 = 90
base_unit_fuselage_2 = int( optimal_slenderness_ratio * d_fuselage_2 )

# x = 0.4             ## transicao
# l1 = x*575
# l2 = 575-l1
# n1 = int(l1 / (18*d_fuselage_1))
# n2 = int(l2 / (18*d_fuselage_2))

# len_fuselage = n1 * base_unit_fuselage_1 + n2 * base_unit_fuselage_2   ## approx. 50

# print(f"Fuselage length: {len_fuselage:.2f}")

E = 210000                                         # MPa (N/mm²)
density = 1.5e-6                                   # kg/mm³
allowablestress = 400                              ## MPa

mt_fuselage_1, I_fuselage_1 = tl.set_memberType(d_fuselage_1, E, density)
mt_fuselage_2, I_fuselage_2 = tl.set_memberType(d_fuselage_2, E, density)
mt_tailboom,   I_tailboom   = tl.set_memberType(d_tailboom, E, density)
mt_landing_gear, I_landing_gear = tl.set_memberType(d_landing_gear, E, density)
mt_nose,       I_nose       = tl.set_memberType(d_nose, E, density)

member_types = {
    'nose':         mt_nose,
    'fuselage_1':   mt_fuselage_1,      # parte dianteira (part=1)
    'fuselage_2':   mt_fuselage_2,      # parte traseira  (part=2)
    'tailboom':     mt_tailboom,
    'landinggear':  mt_landing_gear,
}

optimal_div_2 = optimal_slenderness_ratio * d_fuselage_2
joints = tl.generatesquarejoints(divisao=90, n1=1, divisao2=90, n2=5)
tl.addnosejoints(h=0, b=50, l=30, joints=joints)
#tl.addtailboom_straight(h=328, l=740, joints=joints, d_tailboom=d_tailboom)
tl.addtailboom(h=301, l=765, joints=joints, d_tailboom=d_tailboom, b = 50)
tl.add_landing_gear_pyramid(h=100, b = 10, joints=joints, section=0)

# ============ GERAR GEOMETRIA ============
truss = sl.Truss(dim=3)
members = tl.setgeom(joints, trussgeom=0, nosegeom=0, tailboomgeom=0, 
                     tailboom_encaixe_params={'L': 120, 'b': optimal_slenderness_ratio*d_tailboom})

#pinados, forces = tl.set_study_landinggear(joints, force=(0, 0, 500))
pinados, forces = tl.set_study_tailboom(joints, force=-30, moment=-1.5)
#pinados, forces = tl.setstudysquare(joints, 'concentrated', 100)

supports = tl.generatesupports(pinados, joints)

# # ============ CRIAR ESTRUTURA COM DIÂMETROS VARIÁVEIS ============
trussmembers = tl.settruss(joints, supports, forces, members, truss, mt_fuselage_1, member_types)

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

#tl.plottruss(truss, trussmembers, '3d', elementforces, label='Forças internas', title='Treliça Completa')

# tl.plottrussBC(joints, supports, forces, members,view="3d", scale_force=2.0,title='Condições de Contorno - Treliça Completa'
#               , member_diameters=member_diameters)

tl.plot_truss_fluid(joints, members)

#tl.plottruss_sections(truss, trussmembers, members, joints,'side', member_types, 2.0)


send_to = os.path.join(os.path.expanduser('~'), 'Desktop', 'NISUS\Truss\PRELIMINAR\B')
os.makedirs(send_to, exist_ok=True)

tl.truss_deliverable(
    joints, members,
    member_types_dict=member_types,
    export_html=os.path.join(send_to, 'truss.html'),
    export_csv=os.path.join(send_to, 'truss_data.csv')
)

# send_to = os.path.join('C:\\Users\\joaon\\Desktop\\NISUS\\Truss\\datfiles', 'truss_original.dat')
# tl.export_apdl(joints, members, member_types, filepath=send_to)

# desktop = os.path.join(os.path.expanduser('~'), 'Desktop', 'NISUS\Truss\TrussExport')
# tl.export_spaceclaim(joints, members, member_types, 
#                   filepath=os.path.join(desktop, 'truss_spaceclaim.py'))