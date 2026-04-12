import numpy as np

def generatesquarejoints(comprimento, divisao, x0=0):                                 ## creating square truss
    """
    Parameters
    ----------
    comprimento : recebe comprimento da treliça
    divisao: recebe o comprimento de uma divisão da treliça

    What it does

    Cria os nós para a treliça, em quadrados de lado divisao e igualmente espaçados por divisao

    Returns
    -------
    joints: vetor contendo as coordenadas dos pontos na ordem A B C D da primeira para a última seção
    """
    joints = []
    nsections = comprimento // divisao + 1                                           ## numero de secoes
    for i in range(nsections):
        A = (x0 + i * divisao, 0, 0)
        B = (x0 + i * divisao, divisao, 0)
        C = (x0 + i * divisao, 0, divisao)
        D = (x0 + i * divisao, divisao, divisao)
        joints.append(A)
        joints.append(B)
        joints.append(C)
        joints.append(D)
    return joints

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
    Afinal = joints[0]   ## obtendo as coordenadas do fim do nariz
    Bfinal = joints[1]
    Cfinal = joints[2]  
    Dfinal = joints[3]

    ladotruss = np.linalg.norm(np.array(joints[0]) - np.array(joints[1]))   ## medindo o lado da treliça para calcular o desvio do tailboom
    desvio = (ladotruss-l)/2                                    
    A0 = np.array(Afinal) + np.array((-b, desvio, desvio+h))   ## coordenada do ponto A0 do nariz
    B0 = np.array(Bfinal) + np.array((-b, -desvio, desvio+h))
    C0 = np.array(Cfinal) + np.array((-b, desvio, -desvio+h))
    D0 = np.array(Dfinal) + np.array((-b, -desvio, -desvio+h))

    joints.insert(0, A0)   ## inserindo os pontos do nariz no vetor de juntas
    joints.insert(1, B0)    
    joints.insert(2, C0)
    joints.insert(3, D0)  ## insert ta errado

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
    nsections = int(l/b)   ## numero de seções do tailboom

    desvio = 0
    if cubes:
        ladotruss = np.linalg.norm(np.array(joints[4]) - np.array(joints[5]))   ## medindo o lado da treliça para calcular o desvio do tailboom
        desvio = (ladotruss-b)/2                                                # queremos que o tailboom tenha lado b, entao medimos o lado da trelica e descontamos a metade da largura do tailboom
    Abase = np.array(joints[-4]) + np.array((0, desvio, desvio))    ## coordenadas base do inicio do tailboom
    Bbase = np.array(joints[-3]) - np.array((0, desvio, -desvio))
    Cbase = np.array(joints[-2]) + np.array((0, desvio, -desvio))
    Dbase = np.array(joints[-1]) - np.array((0, desvio, desvio))

    vec = np.array((int(l/nsections), 0, int(h/nsections)))   ## vetor diretor p deslocamento dos pontos

    for i in range(1,nsections):
        Anew = i*vec + np.array(Abase)   ## coordenada do ponto A0 do nariz
        Bnew = i*vec + np.array(Bbase)
        Cnew = i*vec + np.array(Cbase)
        Dnew = i*vec + np.array(Dbase)

        joints.append(Anew)   ## inserindo os pontos do tailboom no vetor de juntas
        joints.append(Bnew)    
        joints.append(Cnew)
        joints.append(Dnew)