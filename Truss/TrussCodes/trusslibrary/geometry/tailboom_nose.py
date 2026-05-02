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

def addtailboom(h, b, l, joints, cubes=False):

    """
    Parameters
    ----------
    h: altura do tailboom
    b: largura da seção do tailboom
    l: comprimento horizontal do tailboom 
    joints: vetor contendo as coordenadas dos pontos na ordem A B C D da primeira para a última seção
    cubes: booleano para escolher se as juntas do tailboom serão cúbicas (reduzindo Asec) ou mantém Asec (ficam como paralelepípedos)
    What it does

    Insere um tailboom na geometria, com coordenada central de h
    """
    nsections = int(l/(0.8*b))   ## numero de seções do tailboom

    desvio = 0
    if cubes:
        ladotruss = np.linalg.norm(np.array(_get_joint_coords(joints[4])) - np.array(_get_joint_coords(joints[5])))   ## medindo o lado da treliça para calcular o desvio do tailboom
        desvio = (ladotruss-b)/2                                                # queremos que o tailboom tenha lado b, entao medimos o lado da trelica e descontamos a metade da largura do tailboom
    Abase = np.array(_get_joint_coords(joints[-4])) + np.array((0, desvio, desvio))    ## coordenadas base do inicio do tailboom
    Bbase = np.array(_get_joint_coords(joints[-3])) - np.array((0, desvio, -desvio))
    Cbase = np.array(_get_joint_coords(joints[-2])) + np.array((0, desvio, -desvio))
    Dbase = np.array(_get_joint_coords(joints[-1])) - np.array((0, desvio, desvio))

    boundary_start = len(joints)
    vec = np.array((int(l/nsections), 0, int(h/nsections)))   ## vetor diretor p deslocamento dos pontos

    for i in range(1,nsections):
        Anew = i*vec + Abase   ## coordenada do ponto A0 do nariz
        Bnew = i*vec + Bbase
        Cnew = i*vec + Cbase
        Dnew = i*vec + Dbase

        joints.append({'coords': tuple(Anew), 'sections': ['tailboom']})   ## inserindo os pontos do tailboom no vetor de juntas
        joints.append({'coords': tuple(Bnew), 'sections': ['tailboom']})    
        joints.append({'coords': tuple(Cnew), 'sections': ['tailboom']})
        joints.append({'coords': tuple(Dnew), 'sections': ['tailboom']})

    # Marcar as juntas de conexão como pertencentes também ao tailboom
    for i in range(boundary_start - 4, boundary_start):
        if 0 <= i < len(joints):
            joints[i] = _add_joint_section(joints[i], 'tailboom')

def addtailboom(h, b, l, joints, d_tailboom, cubes=False, optimal_slenderness=18):
    """
    Parameters
    ----------
    h: altura do tailboom
    b: largura da seção do tailboom
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
    
    # nsections baseado no comprimento real
    nsections = max(1, int(l_real / base_unit))

    desvio = 0
    if cubes:
        ladotruss = np.linalg.norm(np.array(_get_joint_coords(joints[4])) - np.array(_get_joint_coords(joints[5])))
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

def addtailboom_straight(h, b, l, joints, d_tailboom, optimal_slenderness=18):
    
    # pontos de partida: últimos 4 joints da fuselagem
    P_start = [np.array(_get_joint_coords(joints[-4])),
               np.array(_get_joint_coords(joints[-3])),
               np.array(_get_joint_coords(joints[-2])),
               np.array(_get_joint_coords(joints[-1]))]

    # centro da seção final da fuselagem
    centro = sum(P_start) / 4

    # ponto central de chegada do tailboom
    centro_end = centro + np.array([l, 0, h])

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