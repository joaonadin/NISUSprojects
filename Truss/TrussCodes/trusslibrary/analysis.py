import numpy as np
from slientruss3d.truss import Truss
from slientruss3d.type import MemberType
from .geometry import split_parts
from trusslibrary import get_section_label

def get_member_I(member_idx, members_list, joints, I_dict, I_default, member_types_dict=None):
    """
    Obtém momento de inércia do objeto
    """
    if I_dict is None or members_list is None or joints is None:
        return I_default
    j0, j1 = members_list[member_idx]
    label = get_section_label(j0, j1, joints, member_types_dict)
    if label is None:
        return I_default
    return I_dict.get(label, I_default)

def calc_buckling_sf(member_idx, P, I_member, members, truss, E):
    """
    Retorna SF de buckling do membro
    """
    connect = members[member_idx]
    member = truss.GetMemberFromConnect(connect)
    L = member.length
    if L < 1e-10:
        return np.inf
    Pcr = np.pi**2 * E * I_member / L**2
    return -Pcr / P if P < 0 else np.inf


def calc_section_results(member_indices, stress, elementforces, allowablestress,
                         members, truss, E, members_list, joints, I_dict, I_default,
                         member_types_dict=None):
    """
    Coeficientes baseados em cada section 
    """
    s_stress = [stress[i] for i in member_indices if i in stress]
    s_forces = [elementforces[i] for i in member_indices if i in elementforces]
    if not s_stress or not s_forces:
        return None

    max_comp_stress = abs(min(s_stress)) if min(s_stress) < 0 else 0
    max_tens_stress = max(s_stress) if max(s_stress) > 0 else 0
    min_SF_tens = allowablestress / max_tens_stress if max_tens_stress > 0 else np.inf
    min_SF_comp = allowablestress / max_comp_stress if max_comp_stress > 0 else np.inf

    bsf = [calc_buckling_sf(i, elementforces[i], 
            get_member_I(i, members_list, joints, I_dict, I_default, member_types_dict),
            members, truss, E)
        for i in member_indices if i in elementforces and elementforces[i] < 0]
    min_SF_buck = min(bsf) if bsf else np.inf

    return {
        'max_compression_stress': max_comp_stress,
        'max_tension_stress':     max_tens_stress,
        'max_compression_force':  abs(min(s_forces)) if min(s_forces) < 0 else 0,
        'max_tension_force':      max(s_forces) if max(s_forces) > 0 else 0,
        'min_SF_tension':         min_SF_tens,
        'min_SF_compression':     min_SF_comp,
        'min_SF_buckling':        min_SF_buck,
    }


def classify_members_by_section(members, members_list, joints, member_types_dict=None):
    """
    Retorna dict {label: [member_ids]} usando get_section_label.
    """
    by_section = {}
    for mid in members.keys():
        j0, j1 = members_list[mid]
        label = get_section_label(j0, j1, joints, member_types_dict) or 'unknown'
        by_section.setdefault(label, []).append(mid)
    return by_section

    
    def get_mt(j0, j1):
        if not member_types_dict:
            return memberType

        jnt0 = joints[j0] if isinstance(joints[j0], dict) else {}
        jnt1 = joints[j1] if isinstance(joints[j1], dict) else {}

        s0 = set(jnt0.get('sections', []))
        s1 = set(jnt1.get('sections', []))

        common = s0 & s1  

        # ========= PRIORIDADE: INTERSEÇÃO =========
        if 'truss' in common:
            p0 = jnt0.get('part', 1)
            p1 = jnt1.get('part', 1)
            part = max(p0, p1)
            return member_types_dict.get(f'fuselage_{part}', memberType)
        
        if 'landinggear_tow' in common or 'landinggear_pyr' in common:
            return member_types_dict.get('landinggear', memberType)

        if 'tailboom' in common:
            return member_types_dict.get('tailboom', memberType)

        if 'nose' in common:
            return member_types_dict.get('nose', memberType)

        # ========= FALLBACK: NÃO HÁ INTERSEÇÃO =========

        all_sections = s0 | s1

        if 'nose' in all_sections:
            return member_types_dict.get('nose', memberType)
        
        if 'landinggear_tow' in all_sections or 'landinggear_pyr' in all_sections:
            return member_types_dict.get('landinggear', memberType)
        
        if 'truss' in all_sections:
            p0 = jnt0.get('part', 1)
            p1 = jnt1.get('part', 1)
            part = max(p0, p1)
            return member_types_dict.get(f'fuselage_{part}', memberType)

        if 'tailboom' in all_sections:
            return member_types_dict.get('tailboom', memberType)

        
        return memberType

    for joint, support in zip(joints, supports):
        coord = joint['coords'] if isinstance(joint, dict) else joint
        truss.AddNewJoint(coord, support)
    for jointID, force in forces:
        truss.AddExternalForce(jointID, force)
    for jointID0, jointID1 in members:
        truss.AddNewMember(jointID0, jointID1, get_mt(jointID0, jointID1))
    
    return truss.GetMembers()

def safetycoefanls(truss, members, stress, elementforces, allowablestress, I, E,
                   joints=None, members_list=None, I_dict=None, member_types_dict=None):
    """
    Análise de coeficientes de segurança
    """

    all_member_ids = list(members.keys())

    global_results = calc_section_results(all_member_ids, stress, elementforces, allowablestress,
    members, truss, E, members_list, joints, I_dict, I,member_types_dict)

    # backward compatibility
    if I_dict is None or joints is None or members_list is None:
        return (
            global_results['max_compression_stress'],
            global_results['max_tension_stress'],
            global_results['max_compression_force'],
            global_results['max_tension_force'],
            global_results['min_SF_tension'],
            global_results['min_SF_compression'],
            global_results['min_SF_buckling'],
        )

    by_section = classify_members_by_section(members, members_list, joints, member_types_dict)

    results = {'global': global_results}
    for label, member_ids in by_section.items():
        results[label] = calc_section_results(
            member_ids, stress, elementforces, allowablestress,
            members, truss, E, members_list, joints, I_dict, I,
            member_types_dict
        )

    return results

def analyzetruss(comprimento, divisao, d, E, density, allowablestress, jointtype, trusstype):
    """
    Parameters

    comprimento = comprimento da trelica
    divisao = comprimento de uma unidade fundamental
    d = diametro das barras [mm]
    E = Módulo de Young do material das barras [MPa]
    density = densidade do material das barras [kg/mm³] - eu sei, confia nas unidadas
    allowablestress = tensão máxima elástica do material [MPa]
    jointtype = tipo de junta a ser usada, 0 -> squarejoint
    trusstype = tipo de trelica a ser usada, 0 -> warrentruss / 1-> pratttruss / 2-> howetruss / 3-> crosstruss
    study = tipo de estudo, funcao que vai retornar os nos que serao pinados e as forcas no modelo id,(vetor)

    What it does

    Cria e analisa uma geometria de treliça com base no modelo escolhido e considerando o caso proposto para
    estudo. Retorna resultados da análise para o modelo escolhido

    Returns
    -------
    """
    from .geometry import generatesquarejoints, generatesupports, warrentruss, pratttruss, howetruss, crosstruss
    from .study import setstudysquare
    from .constants import TRUSS_DIMENSION

    ## basic setup

    truss = Truss(dim=TRUSS_DIMENSION)
    joints = generatesquarejoints(comprimento, divisao)
    pinados, forces = setstudysquare(joints)                                        ## forca aplicada no ponto
    supports = generatesupports(pinados, joints)                             ## quais suportes queremos pinar
    if trusstype == 0:
        members = warrentruss(joints)                                          ## barras ligando os pontos
    if trusstype == 1:
        members = pratttruss(joints)
    if trusstype == 2:
        members = howetruss(joints)
    if trusstype == 3:
        members = crosstruss(joints)

    ## geometry
    area = np.pi * d**2 / 4
    I = np.pi * d**4 / 64
    memberType = MemberType(area, E, density)

    ## setando a treliça a partir da biblioteca slientruss3d

    trussmembers = settruss(joints, supports, forces, members, truss, memberType)

    ## resolvendo e obtendo resultados via slientruss3d
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
    ) = safetycoefanls(truss, trussmembers, stress, elementforces, allowablestress, I, E)

    return (
    maxcompressionstress,
    maxtensionstress,
    maxcompression,
    maxtension,
    minSFtension,
    minSFcompression,
    minSFbuckling,
    truss.weight
    )