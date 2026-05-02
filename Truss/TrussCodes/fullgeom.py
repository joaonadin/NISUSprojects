## Código de exemplo para gerar uma geometria de treliça com nariz e tailboom
## Faz também o estudo estático dessa geometria e plota resultados com diferenciação de diâmetros

import trusslibrary as tl
import slientruss3d.truss as sl
import numpy as np

# ============ CONFIGURAÇÃO BÁSICA ============
comprimento = 480
divisao = 60

# Diâmetros para cada seção (mm)
d_nose = 2.0
d_truss = 2.5
d_tailboom = 2

# Propriedades do material
E = 210000                                         # MPa (N/mm²)
density = 1.5e-6                                   # kg/mm³
allowablestress = 400                              # MPa

# ============ CRIAR MEMBER TYPES ============
mt_nose, I_nose = tl.set_memberType(d_nose, E, density)
mt_fuselage, I_fuselage = tl.set_memberType(d_truss, E, density)
mt_tailboom, I_tailboom = tl.set_memberType(d_tailboom, E, density)

member_types = {
    'nose': mt_nose,
    'fuselage': mt_fuselage,
    'tailboom': mt_tailboom
}

# ============ GERAR GEOMETRIA ============
truss = sl.Truss(dim=3)
joints = tl.generatesquarejoints(comprimento, divisao, x0=100)
tl.addnosejoints(h=0, b=50, l=30, joints=joints)
tl.addtailboom(h=200, b=35, l=400, joints=joints, cubes=1)

pinados, forces = tl.setstudyfull(joints)
supports = tl.generatesupports(pinados, joints)
members = tl.setgeom(joints, trussgeom=0, nosegeom=1, tailboomgeom=0)

# ============ CRIAR ESTRUTURA COM DIÂMETROS VARIÁVEIS ============
trussmembers = tl.settruss(joints, supports, forces, members, truss, mt_fuselage, member_types)

# ============ RESOLVER E EXTRAIR RESULTADOS ============
truss.Solve()
stress = truss.GetInternalStresses()
elementforces = truss.GetInternalForces()
reactionforces = truss.GetResistances()


# ============ PÓS-PROCESSAMENTO ============
# Modo 1: Análise global (backward compatible - como antes)
(
    maxcompressionstress,
    maxtensionstress,
    maxcompression,
    maxtension,
    minSFtension,
    minSFcompression,
    minSFbuckling,
) = tl.safetycoefanls(truss, trussmembers, stress, elementforces, allowablestress, I_fuselage, E)

# Modo 2: Análise compartimentalizada (novo - separa por seção)
I_dict = {
    'nose': I_nose,
    'fuselage': I_fuselage,
    'tailboom': I_tailboom
}

results_compartmentalized = tl.safetycoefanls(
    truss, trussmembers, stress, elementforces, allowablestress, I_fuselage, E,
    joints=joints, members_list=members, I_dict=I_dict
)

print("\n" + "="*60)
print("ANÁLISE GLOBAL (modo compatível com código antigo)")
print("="*60)
print(f"Min SF Tensão: {minSFtension:.4f}")
print(f"Min SF Compressão: {minSFcompression:.4f}")
print(f"Min SF Buckling: {minSFbuckling:.4f}")

print("\n" + "="*60)
print("ANÁLISE COMPARTIMENTALIZADA (novo modo)")
print("="*60)
for section in ['global', 'nose', 'truss', 'tailboom']:
    if results_compartmentalized[section]:
        print(f"\n{section.upper()}:")
        print(f"  Min SF Tensão: {results_compartmentalized[section]['min_SF_tension']:.4f}")
        print(f"  Min SF Compressão: {results_compartmentalized[section]['min_SF_compression']:.4f}")
        print(f"  Min SF Buckling: {results_compartmentalized[section]['min_SF_buckling']:.4f}")
    else:
        print(f"\n{section.upper()}: Sem dados")

# ============ CRIAR DICTS DE DIÂMETROS PARA PLOTAGEM ============
member_diameters = tl.create_member_diameters_dicts(
    joints, members, d_nose, d_truss, d_tailboom
)

# ============ PLOTAGEM ============
# Plot com forças internas (com cores) - diferenciando diâmetros
#tl.plottruss(
#     truss, trussmembers, '3d', elementforces,
#     label='Forças internas (N)',
#     title='Treliça - Forças Internas e Diâmetros Variáveis',
#     member_diameters=member_diameters,
#     d_scale=2.5
# )

# # Plot com condições de contorno - diferenciando diâmetros
tl.plottrussBC(
    joints, supports, forces, members,
    view="3d",
    scale_force=1.0,
    title='Treliça - Condições de Contorno e Diâmetros Variáveis',
    member_diameters=member_diameters,
    d_scale=1.5
)
