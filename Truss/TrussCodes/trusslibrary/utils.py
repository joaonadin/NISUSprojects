import json
from .geometry import split_parts
from .geometry.fulltrusses import get_section_label
import trusslibrary as tl
import numpy as np

def save_table(
        filename,
        axis1_values,
        axis2_values,
        results,
        axis1_name="axis1",
        axis2_name="axis2"):
    """
    Salva resultados paramétricos em JSON.

    Parameters
    ----------
    filename : endereço e nome do arquivo json
    axis1_values : vetor com valores do primeiro eixo (ex: geometrias de treliça)
    axis2_values : vetor com valores do segundo eixo (ex: nº divisões)
    results : dict
        deve ser acessado como:
        results[(axis1, axis2)] = {
            'SF_buckling': ...,
            'SF_compression': ...,
            'SF_tension': ...,
            'mass': ...
        }
    axis1_name / axis2_name : nomes descritivos dos eixos
    """

    table = {
        "axes": {
            axis1_name: list(axis1_values),
            axis2_name: list(axis2_values)
        },
        "data": {}
    }

    for a1 in axis1_values:
        table["data"][str(a1)] = {}

        for a2 in axis2_values:
            key = (a1, a2)

            if key in results:
                table["data"][str(a1)][str(a2)] = results[key]

    with open(filename, "w") as f:
        json.dump(table, f, indent=4)

def create_member_diameters_dicts(truss, members, E):

    member_diameters = {}

    for idx, (j0, j1) in enumerate(members):
        member = truss.GetMemberFromConnect((j0, j1))
        if member is None:
            continue

        k = member.k
        L = member.length

        # recupera área real usada pelo solver
        A = k * L / E

        # converte pra diâmetro (seção circular)
        d = np.sqrt(4 * A / np.pi)

        member_diameters[idx] = d

    return member_diameters

def get_member_section(joints, j0, j1):
    s0 = joints[j0].get('sections', []) if isinstance(joints[j0], dict) else []
    s1 = joints[j1].get('sections', []) if isinstance(joints[j1], dict) else []
    all_sections = set(s0 + s1)
    if 'landinggear_tow' in all_sections: return 'landinggear_tow'
    if 'landinggear_pyr' in all_sections: return 'landinggear_pyr'
    if 'tailboom'        in all_sections: return 'tailboom'
    if 'truss'           in all_sections: return 'truss'
    if 'nose'            in all_sections: return 'nose'
    return 'truss'                                        

def get_masses(members_list, joints, truss, density, E, member_types_dict=None):
    """
    Parameters
    ----------
    members_list : lista de tuplas (j0, j1) dos membros
    joints       : mesma lista de joints passada ao settruss
    truss        : objeto treliça do slientruss3d
    density      : densidade
    E            : módulo de Young
    member_types_dict : dict de seções (opcional; se None, retorna só total)

    Returns
    -------
    dict com massas por seção e massa total, em kg
    """
    masses = {}

    for j0, j1 in members_list:
        member = truss.GetMemberFromConnect((j0, j1))
        if member is None:
            continue

        A = member.k * member.length / E
        m = A * member.length * density

        label = get_section_label(j0, j1, joints, member_types_dict) or 'unknown'
        masses[label] = masses.get(label, 0.0) + m

    masses['total'] = sum(v for k, v in masses.items() if k != 'total')
    return masses

def print_global_analysis(truss, trussmembers, stress, elementforces, allowablestress,
                          member_types_dict, joints, members, E):

    I_default = member_types_dict['fuselage_1'].I
    I_dict = {label: mt.I for label, mt in member_types_dict.items()}

    results = tl.safetycoefanls(
        truss, trussmembers, stress, elementforces, allowablestress, I_default, E,
        joints=joints, members_list=members, I_dict=I_dict, member_types_dict=member_types_dict
    )

    print("\n" + "="*60)
    print("ANÁLISE GLOBAL")
    print("="*60)
    g = results['global']
    print(f"Min SF Tensão:      {g['min_SF_tension']:.4f}")
    print(f"Min SF Compressão:  {g['min_SF_compression']:.4f}")
    print(f"Min SF Buckling:    {g['min_SF_buckling']:.4f}")

    print("\n" + "="*60)
    print("ANÁLISE COMPARTIMENTALIZADA")
    print("="*60)
    for section in member_types_dict.keys():
        r = results.get(section)
        if r:
            print(f"\n{section.upper()}:")
            print(f"  Min SF Tensão:     {r['min_SF_tension']:.4f}")
            print(f"  Min SF Compressão: {r['min_SF_compression']:.4f}")
            print(f"  Min SF Buckling:   {r['min_SF_buckling']:.4f}")