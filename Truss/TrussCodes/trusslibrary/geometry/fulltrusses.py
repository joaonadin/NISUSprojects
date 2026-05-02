from .trusses import warrentruss, pratttruss, howetruss, crosstruss
from .landing_gear import setlandinggearmembers
import numpy as np

def split_parts(joints, case = 'geometry'):
    """Parameters
    ----------
    joints: vetor contendo as coordenadas dos pontos na ordem A B C D da primeira para a última seção
    case: se for geometry, faz a escolha considerando geometria, se for forces, faz considerando aplicação de forças
    ps: ambas são distintas pq a geometria considera os nós da seção seguinte p fazer conexão

    Returns
    -------
    nosejoints: vetor contendo as coordenadas dos pontos do nariz
    trussjoints: vetor contendo as coordenadas dos pontos da treliça principal
    tailboomjoints: vetor contendo as coordenadas dos pontos do tailboom
    """
    # Se as joints vierem com seções explícitas, use essas tags em vez de inferir pela geometria.
    if any(isinstance(j, dict) and 'sections' in j for j in joints):
        nosejoints = [j for j in joints if isinstance(j, dict) and 'nose' in j.get('sections', [])]
        trussjoints = [j for j in joints if isinstance(j, dict) and 'truss' in j.get('sections', [])]
        tailboomjoints = [j for j in joints if isinstance(j, dict) and 'tailboom' in j.get('sections', [])]
        landinggearjoints = [j for j in joints if isinstance(j, dict) and 
                     any(s in j.get('sections', []) for s in ['landinggear_tow', 'landinggear_pyr', 'landinggear'])]
    
    if case == 'forces':
        # For forces, we need to assign labels based on sections, prioritizing tailboom > truss > nose > landinggear
        nosejoints = []
        trussjoints = []
        tailboomjoints = []
        landinggearjoints = []
        for joint in joints:
            if isinstance(joint, dict):
                sections = joint.get('sections', [])
                if 'tailboom' in sections:
                    tailboomjoints.append(joint)
                elif 'truss' in sections:
                    trussjoints.append(joint)
                elif 'nose' in sections:
                    nosejoints.append(joint)
                else:
                    landinggearjoints.append(joint)
            else:
                landinggearjoints.append(joint)
    
    return nosejoints, trussjoints, tailboomjoints, landinggearjoints

def setgeom(joints, trussgeom, nosegeom, tailboomgeom):
    nosejoints, trussjoints, tailboomjoints, landinggearjoints = split_parts(joints)

    nosemembers    = warrentruss(nosejoints)    if nosegeom    == 0 else pratttruss(nosejoints)    if nosegeom    == 1 else howetruss(nosejoints)    if nosegeom    == 2 else crosstruss(nosejoints)
    trussmembers   = warrentruss(trussjoints)   if trussgeom   == 0 else pratttruss(trussjoints)   if trussgeom   == 1 else howetruss(trussjoints)   if trussgeom   == 2 else crosstruss(trussjoints)
    tailboommembers= warrentruss(tailboomjoints) if tailboomgeom== 0 else pratttruss(tailboomjoints) if tailboomgeom== 1 else howetruss(tailboomjoints) if tailboomgeom== 2 else crosstruss(tailboomjoints)

    if landinggearjoints:
        landinggearmembers, landinggear_truss_links = setlandinggearmembers(joints, landinggearjoints, trussjoints)
    else:
        landinggearmembers, landinggear_truss_links = [], []

    nose_indices = [idx for idx, j in enumerate(joints) if isinstance(j, dict) and 'nose'     in j.get('sections', [])]
    truss_indices = [idx for idx, j in enumerate(joints) if isinstance(j, dict) and 'truss'    in j.get('sections', [])]
    tailboom_indices = [idx for idx, j in enumerate(joints) if isinstance(j, dict) and 'tailboom' in j.get('sections', [])]
    landinggear_indices = [idx for idx, j in enumerate(joints) if isinstance(j, dict) and      # <-- corrigido
                           any(s in j.get('sections', []) for s in ['landinggear_tow', 'landinggear_pyr', 'landinggear'])]

    nosemembers     = [(nose_indices[i],        nose_indices[j])        for i, j in nosemembers]
    trussmembers    = [(truss_indices[i],        truss_indices[j])       for i, j in trussmembers]
    tailboommembers = [(tailboom_indices[i],     tailboom_indices[j])    for i, j in tailboommembers]
    landinggearmembers      = [(landinggear_indices[i], landinggear_indices[j]) for i, j in landinggearmembers] if landinggearmembers else []
    landinggear_truss_members = [(landinggear_indices[i], truss_indices[j])     for i, j in landinggear_truss_links] if landinggear_truss_links else []

    members = nosemembers + trussmembers + tailboommembers + landinggearmembers + landinggear_truss_members
    members = list({(min(a, b), max(a, b)): (a, b) for a, b in members}.values())
    return members

def get_section_label(j0, j1, joints, member_types_dict=None):
    """
    Retorna a label de seção (ex: 'nose', 'fuselage_1', 'landinggear', etc.)
    para um membro definido pelos joints j0 e j1.
    """
    if not member_types_dict:
        return None

    jnt0 = joints[j0] if isinstance(joints[j0], dict) else {}
    jnt1 = joints[j1] if isinstance(joints[j1], dict) else {}

    s0 = set(jnt0.get('sections', []))
    s1 = set(jnt1.get('sections', []))

    common = s0 & s1

    # ========= PRIORIDADE: INTERSEÇÃO =========
    if 'truss' in common:
        p0 = jnt0.get('part', 1)
        p1 = jnt1.get('part', 1)
        part = min(p0, p1)
        return f'fuselage_{part}'

    if 'landinggear_tow' in common or 'landinggear_pyr' in common:
        return 'landinggear'

    if 'tailboom' in common:
        return 'tailboom'

    if 'nose' in common:
        return 'nose'

    # ========= FALLBACK: UNIÃO =========
    all_sections = s0 | s1

    if 'landinggear_tow' in all_sections or 'landinggear_pyr' in all_sections:
        return 'landinggear'
    
    if 'nose' in all_sections:
        return 'nose'

    if 'truss' in all_sections:
        p0 = jnt0.get('part', 1)
        p1 = jnt1.get('part', 1)
        part = min(p0, p1)
        return f'fuselage_{part}'

    if 'tailboom' in all_sections:
        return 'tailboom'

    return None

def get_member_type(j0, j1, joints, memberType, member_types_dict=None):
    """
    Retorna o memberType correto para um membro (j0, j1),
    usando get_section_label como base.
    """
    label = get_section_label(j0, j1, joints, member_types_dict)
    if label is None or member_types_dict is None:
        return memberType
    return member_types_dict.get(label, memberType)

def settruss(joints, supports, forces, members, truss, memberType, member_types_dict=None):
    for joint, support in zip(joints, supports):
        coord = joint['coords'] if isinstance(joint, dict) else joint
        truss.AddNewJoint(coord, support)
    for jointID, force in forces:
        truss.AddExternalForce(jointID, force)
    for jointID0, jointID1 in members:
        mt = get_member_type(jointID0, jointID1, joints, memberType, member_types_dict)
        truss.AddNewMember(jointID0, jointID1, mt)

    return truss.GetMembers()