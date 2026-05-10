import numpy as np
from .joints import _get_joint_coords, _add_joint_section

def addnosejoints(h, b, l, joints):
    """
    Parameters
    ----------
    h: distância vertical do nariz
    b: distância horizontal do nariz
    l: comprimento dos lados do nariz
    joints: vetor contendo as coordenadas dos pontos na ordem A B C D da primeira para a última seção

    What it does

    Insere um nariz na geometria, com coordenada central de h
    """
    Afinal = _get_joint_coords(joints[0])   ## obtendo as coordenadas do fim do nariz
    Bfinal = _get_joint_coords(joints[1])
    Cfinal = _get_joint_coords(joints[2])
    Dfinal = _get_joint_coords(joints[3])

    ladotruss = np.linalg.norm(np.array(Afinal) - np.array(Bfinal))   ## medindo o lado da treliça para calcular o desvio do tailboom
    desvio = (ladotruss - l) / 2
    A0 = np.array(Afinal) + np.array((-b, desvio, desvio + h))   ## coordenada do ponto A0 do nariz
    B0 = np.array(Bfinal) + np.array((-b, -desvio, desvio + h))
    C0 = np.array(Cfinal) + np.array((-b, desvio, -desvio + h))
    D0 = np.array(Dfinal) + np.array((-b, -desvio, -desvio + h))

    new_nose = [
        {'coords': tuple(A0), 'sections': ['nose']},
        {'coords': tuple(B0), 'sections': ['nose']},
        {'coords': tuple(C0), 'sections': ['nose']},
        {'coords': tuple(D0), 'sections': ['nose']}
    ]
    joints[0:0] = new_nose

    # Marcar as juntas de conexão como pertencentes também ao nariz
    for i in range(4, 8):
        joints[i] = _add_joint_section(joints[i], 'nose')


def addtailboom(h, l, joints, d_tailboom, optimal_slenderness=18):
    """
    Parameters
    ----------
    h: altura do tailboom
    l: comprimento horizontal do tailboom 
    joints: vetor contendo as coordenadas dos pontos na ordem A B C D
    d_tailboom: diâmetro dos membros do tailboom (para calcular nsections)
    cubes: booleano para seções cúbicas
    optimal_slenderness: razão l/d ótima (default 18)
    """
    # comprimento real da barra inclinada (hipotenusa de l e h)
    l_real = np.sqrt(l**2 + h**2)
    
    # base_unit: comprimento de cada divisão tal que a barra longitudinal fique em l/d ótimo
    base_unit = optimal_slenderness * d_tailboom
    b = base_unit

    # nsections baseado no comprimento real
    nsections = max(1, int(l_real / base_unit))

    desvio = 0
    ladotruss = b
    desvio = (ladotruss - b) / 2

    Abase = np.array(_get_joint_coords(joints[-4])) + np.array((0,  desvio,  desvio))
    Bbase = np.array(_get_joint_coords(joints[-3])) - np.array((0, -desvio,  desvio))
    Cbase = np.array(_get_joint_coords(joints[-2])) + np.array((0,  desvio, -desvio))
    Dbase = np.array(_get_joint_coords(joints[-1])) - np.array((0, -desvio, -desvio))

    boundary_start = len(joints)

    # vetor diretor por seção — divide l e h igualmente entre nsections
    vec = np.array((l / nsections, 0, h / nsections))

    for i in range(1, nsections):
        Anew = i * vec + Abase
        Bnew = i * vec + Bbase
        Cnew = i * vec + Cbase
        Dnew = i * vec + Dbase

        joints.append({'coords': tuple(Anew), 'sections': ['tailboom']})
        joints.append({'coords': tuple(Bnew), 'sections': ['tailboom']})
        joints.append({'coords': tuple(Cnew), 'sections': ['tailboom']})
        joints.append({'coords': tuple(Dnew), 'sections': ['tailboom']})

    for i in range(boundary_start - 4, boundary_start):
        if 0 <= i < len(joints):
            joints[i] = _add_joint_section(joints[i], 'tailboom')

def addtailboom(h, l, joints, d_tailboom, optimal_slenderness=18, b=0):

    P_start = [np.array(_get_joint_coords(joints[-4])),
               np.array(_get_joint_coords(joints[-3])),
               np.array(_get_joint_coords(joints[-2])),
               np.array(_get_joint_coords(joints[-1]))]
    centro = sum(P_start) / 4

    centro_end = centro + np.array([l, 0, h])
    if b == 0:
        b = optimal_slenderness * d_tailboom
    half = b / 2
    offsets = [
        np.array([0, -half, -half]),  # A
        np.array([0, +half, -half]),  # B
        np.array([0, -half, +half]),  # C
        np.array([0, +half, +half]),  # D
    ]

    l_real = np.sqrt(l**2 + h**2)
    base_unit = optimal_slenderness * d_tailboom
    nsections = max(1, int(l_real / base_unit))

    boundary_start = len(joints) - 4
    for i in range(boundary_start, boundary_start + 4):
        joints[i] = _add_joint_section(joints[i], 'tailboom')

    # seções 1..nsections: offset fixo do tailboom, centro interpolado
    for i in range(1, nsections + 1):
        t = i / nsections
        centro_i = (1 - t) * centro + t * centro_end
        for off in offsets:
            P_new = centro_i + off
            joints.append({'coords': tuple(P_new), 'sections': ['tailboom']})

def addtailboom_straight(h, l, joints, d_tailboom, optimal_slenderness=18):
    
    # pontos de partida: últimos 4 joints da fuselagem
    P_start = [np.array(_get_joint_coords(joints[-4])),
               np.array(_get_joint_coords(joints[-3])),
               np.array(_get_joint_coords(joints[-2])),
               np.array(_get_joint_coords(joints[-1]))]

    # centro da seção final da fuselagem
    centro = sum(P_start) / 4

    # ponto central de chegada do tailboom
    centro_end = centro + np.array([l, 0, h])

    b = optimal_slenderness * d_tailboom
    # 4 cantos da seção final — deslocamentos relativos ao centro, mesma ordem A B C D
    half = b / 2
    offsets = [
        np.array([0, -half, -half]),  # A
        np.array([0, +half, -half]),  # B
        np.array([0, -half, +half]),  # C
        np.array([0, +half, +half]),  # D
    ]
    P_end = [centro_end + off for off in offsets]

    # nsections baseado no comprimento real da barra e l/d ótimo
    l_real = np.sqrt(l**2 + h**2)
    base_unit = optimal_slenderness * d_tailboom
    nsections = max(1, int(l_real / base_unit))

    # marcar joints de fronteira
    boundary_start = len(joints) - 4
    for i in range(boundary_start, boundary_start + 4):
        joints[i] = _add_joint_section(joints[i], 'tailboom')

    # interpolar linearmente entre P_start e P_end
    for i in range(1, nsections):
        t = i / nsections
        for P_s, P_e in zip(P_start, P_end):
            P_new = (1 - t) * P_s + t * P_e
            joints.append({'coords': tuple(P_new), 'sections': ['tailboom']})


def add_tailboom_encaixe(joints, L, b, section='encaixe'):
    """Adiciona uma seção de encaixe após o tailboom.

    Usa os últimos 4 nós do tailboom como A, B, C, D, adiciona E, F, G, H
    deslocados em y por d e duplica os 4 pontos superiores em x por b.
    Vista frontal dos nós:

    H  D  C  G
    F  B  A  E

    L é o comprimento total do encaixe, ou seja, a distância em y entre E e F.
    Calcula d = (L - AB) / 2, onde AB é a distância em y entre A e B.

    Retorna os índices dos nós gerados e os pares de conexões extras.
    """
    # Encontrar todos os índices de joints com seção 'tailboom'
    tailboom_indices = [idx for idx, j in enumerate(joints) 
                        if isinstance(j, dict) and 'tailboom' in j.get('sections', [])]
    
    if len(tailboom_indices) < 8:
        raise ValueError(f'Tailboom deve ter pelo menos 8 joints (duas seções). Encontrado: {len(tailboom_indices)}')
    
    # Últimos 4 nós do tailboom
    A_idx = tailboom_indices[-4]
    B_idx = tailboom_indices[-3]
    C_idx = tailboom_indices[-2]
    D_idx = tailboom_indices[-1]

    # Penúltima seção: 4 joints antes dos últimos 4
    A0_idx = tailboom_indices[-8]
    B0_idx = tailboom_indices[-7]
    C0_idx = tailboom_indices[-6]
    D0_idx = tailboom_indices[-5]

    A = np.array(_get_joint_coords(joints[A_idx]))
    B = np.array(_get_joint_coords(joints[B_idx]))
    C = np.array(_get_joint_coords(joints[C_idx]))
    D = np.array(_get_joint_coords(joints[D_idx]))

    # Calcular AB = |A_y - B_y|
    dist_AB = abs(A[1] - B[1])
    # 2d = L - AB
    d = (L - dist_AB) / 2

    E = A + np.array((0, -d, 0))
    F = B + np.array((0, d, 0))
    G = C + np.array((0, -d, 0))
    H = D + np.array((0, d, 0))

    added_indices = []
    for P in (E, F, G, H):
        joints.append({'coords': tuple(P), 'sections': [section]})
        added_indices.append(len(joints) - 1)

    duplicated_indices = []
    for P in (C, D, G, H):
        joints.append({'coords': tuple(P + np.array((b, 0, 0))), 'sections': [section]})
        duplicated_indices.append(len(joints) - 1)

    connector_members = [
        (A_idx, duplicated_indices[0]),  # A -> C2
        (A_idx, added_indices[0]),  # A -> E
        (A_idx, added_indices[2]),  # A -> G
        (A_idx, D_idx),  # A -> D
        (D_idx, added_indices[1]),  # D -> F
        (B_idx, duplicated_indices[1]),  # B -> D2
        (added_indices[0], duplicated_indices[2]),  # E -> G2
        (added_indices[1], duplicated_indices[3]),   # F -> H2
        (added_indices[2], duplicated_indices[2]),   # G -> G2
        (C_idx, duplicated_indices[0]),   # C -> C2
        (D_idx, duplicated_indices[1]),   # D -> D2
        (added_indices[3], duplicated_indices[3]),   # H -> H2
        (C_idx, added_indices[2]),   # C -> G
        (D_idx, added_indices[3]),   # D -> H
        (duplicated_indices[0], duplicated_indices[2]),   # C2 -> G2
        (D_idx, duplicated_indices[3]),   # D -> H2
        (B_idx, added_indices[1]),   # B -> F
        (added_indices[1], added_indices[3]),   # F -> H
        (added_indices[2], added_indices[0]),   # G -> E
        (added_indices[0], duplicated_indices[0]),  # E -> C2
        (B_idx, duplicated_indices[0]),  # B -> C2
        (B_idx, duplicated_indices[3]),   # B -> H2
        (duplicated_indices[0], duplicated_indices[1]),  # C2 -> D2
        (duplicated_indices[3], duplicated_indices[1]),  # H2 -> D2
        (A0_idx, added_indices[0]),  # A0 -> E
        (B0_idx, added_indices[1]),  # B0 -> F
        (C0_idx, added_indices[2]),  # C0 -> G
        (D0_idx, added_indices[3])   # D0 -> H
    ]

    return {
        'new_joint_indices': added_indices + duplicated_indices,
        'connector_members': connector_members,
    }