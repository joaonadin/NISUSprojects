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

def generatesquarejoints(divisao, n1, divisao2=None, n2=0, x0=0):
    """
    Parameters
    ----------
    divisao  : tamanho da célula da parte 1
    n1       : número de células da parte 1
    divisao2 : tamanho da célula da parte 2 (None = igual à parte 1)
    n2       : número de células da parte 2
    x0       : posição inicial em x
    """
    if divisao2 is None:
        divisao2 = divisao

    cy = max(divisao, divisao2) / 2
    cz = max(divisao, divisao2) / 2

    joints = []
    x = x0

    for part, d, n in [(1, divisao, n1), (2, divisao2, n2)]:
        if n == 0:
            continue
        half = d / 2
        nsections = n + 1 if part == 1 else n  # parte 1 inclui o anel inicial, parte 2 continua

        for _ in range(nsections):
            for coord in [
                (x, cy - half, cz - half),
                (x, cy + half, cz - half),
                (x, cy - half, cz + half),
                (x, cy + half, cz + half),
            ]:
                joints.append({'coords': coord, 'sections': ['truss'], 'part': part})
            x += d

    return joints
