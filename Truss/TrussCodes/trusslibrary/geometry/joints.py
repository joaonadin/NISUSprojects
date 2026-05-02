import numpy as np


def _get_joint_coords(joint):
    """
    Retorna as coordenadas da junta - inserir joint[12] para coords da junta 12
    """
    return joint['coords'] if isinstance(joint, dict) else joint

def _ensure_joint_dict(joint, default_sections=None):
    """
    Garante que joint estará no formato adequado, com coords e sections
    """
    if isinstance(joint, dict):
        if 'coords' not in joint:
            joint = {'coords': _get_joint_coords(joint), 'sections': joint.get('sections', list(default_sections or []))}
        if 'sections' not in joint:
            joint['sections'] = list(default_sections or [])
        return joint
    return {'coords': _get_joint_coords(joint), 'sections': list(default_sections or [])}

def _add_joint_section(joint, section):
    """
    Adiciona section na junta
    """
    joint = _ensure_joint_dict(joint, default_sections=['truss'])
    if section not in joint['sections']:
        joint['sections'].append(section)
    return joint

def _joint_sections(joint):
    """
    Retorna as sections da junta
    """
    if isinstance(joint, dict):
        return joint.get('sections', [])
    return []

def generatesquarejoints(comprimento, divisao, divisao2=None, transicao=0.5, x0=0):
    if divisao2 is None:
        divisao2 = divisao

    nsections = comprimento // divisao + 1
    transicao_idx = int(nsections * transicao)

    # centro fixo — metade da maior divisao
    cy = max(divisao, divisao2) / 2
    cz = max(divisao, divisao2) / 2

    joints = []
    x = x0
    for i in range(nsections):
        part = 1 if i < transicao_idx else 2
        d = divisao if part == 1 else divisao2
        half = d / 2

        for coord in [
            (x, cy - half, cz - half),  # A
            (x, cy + half, cz - half),  # B
            (x, cy - half, cz + half),  # C
            (x, cy + half, cz + half),  # D
        ]:
            joints.append({'coords': coord, 'sections': ['truss'], 'part': part})

        x += d

    return joints

