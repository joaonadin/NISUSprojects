import numpy as np

def add_landing_gear_tower(joints, h, div, section=0):
    """
    Parameters
    ----------
    joints: vetor contendo as coordenadas dos pontos na ordem A B C D da primeira para a última seção
    h: altura do landing gear
    div: divisão da treliça (para posicionar o landing gear)
    section: seção onde o landing gear deve ser adicionado (0 para primeira seção, -1 para última seção)

    What it does

    Adiciona um landing gear na geometria, para cobrir vão de altura h, buscando obter comprimento
    otimizado de tubo, que o usuário inputa em div.
    """
    ideal_height = div * 0.866 / 2
    n_triangles = round(h / ideal_height)
    true_height = h / n_triangles
    first_section_joints = 4*section
    second_section_joints = first_section_joints + 4
    A_1 = joints[first_section_joints]['coords'] if isinstance(joints[first_section_joints], dict) else joints[first_section_joints]
    B_1 = joints[first_section_joints + 1]['coords'] if isinstance(joints[first_section_joints + 1], dict) else joints[first_section_joints + 1]
    A_2 = joints[second_section_joints]['coords'] if isinstance(joints[second_section_joints], dict) else joints[second_section_joints]
    B_2 = joints[second_section_joints + 1]['coords'] if isinstance(joints[second_section_joints + 1], dict) else joints[second_section_joints + 1]
    A_mid = (np.array(A_1) + np.array(A_2)) / 2
    B_mid = (np.array(B_1) + np.array(B_2)) / 2
    A_B_1 = (np.array(A_1) + np.array(B_1)) / 2
    A_B_2 = (np.array(A_2) + np.array(B_2)) / 2
    direction_vector = np.array([0, 0, -true_height])
    for i in range(1, n_triangles + 1):
        if i%2 == 1:
            joints.append({'coords': tuple(A_mid + direction_vector * i), 'sections': ['landinggear_tow']})
            joints.append({'coords': tuple(B_mid + direction_vector * i), 'sections': ['landinggear_tow']})
            joints.append({'coords': tuple(A_B_1 + direction_vector * i), 'sections': ['landinggear_tow']})
            joints.append({'coords': tuple(A_B_2 + direction_vector * i), 'sections': ['landinggear_tow']})
        if i%2 == 0:
            joints.append({'coords': tuple(A_1 + direction_vector * i), 'sections': ['landinggear_tow']})
            joints.append({'coords': tuple(B_1 + direction_vector * i), 'sections': ['landinggear_tow']})
            joints.append({'coords': tuple(A_2 + direction_vector * i), 'sections': ['landinggear_tow']})
            joints.append({'coords': tuple(B_2 + direction_vector * i), 'sections': ['landinggear_tow']})

def add_landing_gear_pyramid(joints, h, b, section=0):
    """
    Parameters
    ----------
    joints: vetor contendo as coordenadas dos pontos na ordem A B C D da primeira para a última seção
    h: altura do landing gear
    b: comprimento do quadrado da base
    section: seção onde o landing gear deve ser adicionado (0 para primeira seção, -1 para última seção)

    What it does

    Adiciona um landing gear piramidal na geometria, para cobrir vão de altura h.
    """
    truss_indices = [idx for idx, joint in enumerate(joints) if isinstance(joint, dict) and 'truss' in joint.get('sections', [])]
    front_indices = truss_indices[4*section:4*section+2]
    back_indices = truss_indices[4*(section+1):4*(section+1)+2]
    A, B  = np.array(joints[front_indices[0]]['coords']), np.array(joints[front_indices[1]]['coords'])
    C, D  = np.array(joints[back_indices[0]]['coords']), np.array(joints[back_indices[1]]['coords'])
    center = (A+B+C+D)/4
    side_arr = np.array([0, b/2, 0])
    front_arr = np.array([b/2, 0, 0])
    height = np.array([0, 0, -h])
    A1 = center - side_arr - front_arr + height
    B1 = center + side_arr - front_arr + height
    C1 = center - side_arr + front_arr + height
    D1 = center + side_arr + front_arr + height
    joints.append({'coords': tuple(A1), 'sections': ['landinggear_pyr'], 'section': section}) ## salvando a section de insercao p usar depois
    joints.append({'coords': tuple(B1), 'sections': ['landinggear_pyr'], 'section': section})
    joints.append({'coords': tuple(C1), 'sections': ['landinggear_pyr'], 'section': section})
    joints.append({'coords': tuple(D1), 'sections': ['landinggear_pyr'], 'section': section})

def get_matched_joints_tower(landinggearjoints, trussjoints):
    """
    Returns joints from the truss that are directly connected to the landing gear - tower landing gear
    """
    matched_truss = []
    for j in range(4):
        lg_coord = landinggearjoints[4+j]['coords'] ## compare x and y coordinates of the landing gear joints with the truss joints to find the corresponding indices
        for k, tr_joint in enumerate(trussjoints):
            if tr_joint['coords'][:2] == lg_coord[:2] and tr_joint['coords'][2] == 0:
                matched_truss.append(k)
                break
    return matched_truss

def get_matched_joints_pyramid(joints, landinggearjoints, trussjoints):
    """
    Returns joints from the truss that are directly connected to the landing gear - pyramid landing gear
    """
    section = landinggearjoints[0].get('section', 0)  # <-- pega direto do joint

    truss_indices = [idx for idx, joint in enumerate(joints) if isinstance(joint, dict) and 'truss' in joint.get('sections', [])]
    front_indices = truss_indices[4*section : 4*section+2]
    back_indices  = truss_indices[4*(section+1) : 4*(section+1)+2]

    matched_truss = []
    for idx in front_indices + back_indices:
        for k, tr_joint in enumerate(trussjoints):
            if tr_joint['coords'] == joints[idx]['coords']:
                matched_truss.append(k)
                break
    return matched_truss

def setlandinggearmembers(joints, landinggearjoints, trussjoints):
    if not landinggearjoints:
        return [], []
    landinggear_members = []
    landinggear_truss_links = []
    n_joints = len(landinggearjoints)
    n_sections = n_joints // 4
    first_sections = landinggearjoints[0].get('sections', [])

    if 'landinggear_tow' in first_sections:
        landinggear_members, landinggear_truss_links = set_lg_tower(n_joints, landinggear_members, landinggear_truss_links,
            n_sections, landinggearjoints, trussjoints)
    elif 'landinggear_pyr' in first_sections:
        landinggear_members, landinggear_truss_links = set_lg_pyramid(joints, landinggear_members, landinggear_truss_links,
            landinggearjoints, trussjoints) 
    return landinggear_members, landinggear_truss_links

def set_lg_tower(n_joints, landinggear_members, landinggear_truss_links, n_sections, landinggearjoints, trussjoints):
    for n in range(0, n_sections):
        if n%2 == 0:                          # we invert odd and even cause 0 is 1 here
            i = 4 * n                         # in which section of the landing gear we are
            j = 4 * (n + 1)                   # index of the next section
            A_mid, B_mid, AB_1, AB_2 = i, i + 1, i + 2, i + 3
            if n == 0:
                landinggear_members.extend([(AB_1, AB_2), (A_mid, B_mid)])
            if j < n_joints:
                A_1, B_1, A_2, B_2 = j, j + 1, j + 2, j + 3
                landinggear_members.extend([ 
                    (A_mid, A_1), (A_mid, A_2), (B_mid, B_1), (B_mid, B_2), # diagonal connections
                    (AB_1, A_1), (AB_1, B_1), (AB_2, A_2), (AB_2, B_2),
                    (A_mid, AB_1), (A_mid, AB_2), (B_mid, AB_1), (B_mid, AB_2)  # xy connections - for stability
                ])
        if n%2 == 1:
            i = 4 * n                         # in which section of the landing gear we are
            j = 4 * (n + 1)                   # index of the next section
            k = 4 * (n + 2)                   # index of the section after the next
            A_1, B_1, A_2, B_2 = i, i + 1, i + 2, i + 3
            if j < n_joints:
                A_mid, B_mid, AB_1, AB_2 = j, j + 1, j + 2, j + 3
                landinggear_members.extend([    ## diagonal connections
                    (A_mid, A_1), (A_mid, A_2), (B_mid, B_1), (B_mid, B_2),
                    (AB_1, A_1), (AB_1, B_1), (AB_2, A_2), (AB_2, B_2)
                ])
            if k < n_joints-2:  
                A_1_next, B_1_next, A_2_next, B_2_next = k, k + 1, k + 2, k + 3      # joints da próxima seção par
                landinggear_members.extend([  ## vertical connections
                    (A_1, A_1_next),  (B_1, B_1_next), (A_2, A_2_next), (B_2, B_2_next)
                ])  
    # removing duplications! - 
    landinggear_members = list({(min(a,b), max(a,b)): (a,b) for a,b in landinggear_members}.values())
    matched_truss = get_matched_joints_tower(landinggearjoints, trussjoints)
    A1, B1, A2, B2 = matched_truss[:4]  
    landinggear_truss_links.extend([
        (0, A1), (0, A2), (1, B1), (1, B2), ##zig zag xz
        (2, A1), (2, B1), (3, A2), (3, B2), ##zig zag yz
        (4, A1), (5, B1), (6, A2), (7, B2), ## vertical 
    ])
    return landinggear_members, landinggear_truss_links

def set_lg_pyramid(joints, landinggear_members, landinggear_truss_links, landinggearjoints, trussjoints):
    landinggear_members.extend([(0, 1), (1, 3), (3,2), (2,0)])
    matched_truss = get_matched_joints_pyramid(joints, landinggearjoints, trussjoints)
    A1, B1, A2, B2 = matched_truss[:4]  
    landinggear_truss_links.extend([
        (0, A1), (1, B1), (2, A2), (3, B2)
    ])
    return landinggear_members, landinggear_truss_links