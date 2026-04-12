from .trusses import warrentruss, pratttruss, howetruss, crosstruss


def splitnosetrusstailboom(joints, case = 'geometry'):
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
    if case == 'geometry':
        nosejoints = joints[:8]   ## obtendo os pontos do nariz

        nsections = len(joints) // 4

        # Identificar a seção onde começa o tailboom (onde z do ponto A != 0)
        tailboom_section = None
        for i in range(1, nsections):  # começar da seção 1 (após o nariz)
            z_a = joints[4*i][2]  # z do ponto A da seção i
            if z_a != 0:
                tailboom_section = i
                break
        if tailboom_section is not None:
            tailboom_start = 4 * tailboom_section
            tailboomjoints = joints[tailboom_start-4:]
        else:
            tailboom_start = None
            tailboomjoints = []

        trussjoints = joints[4:tailboom_start] if tailboom_start is not None else joints[4:]
    elif case == 'forces':
         nosejoints = joints[:4]   ## obtendo os pontos do nariz

         nsections = len(joints) // 4

         # Identificar a seção onde começa o tailboom (onde z do ponto A != 0)
         tailboom_section = None
         for i in range(1, nsections):  # começar da seção 1 (após o nariz)
             z_a = joints[4*i][2]  # z do ponto A da seção i
             if z_a != 0:
                 tailboom_section = i
                 break
         if tailboom_section is not None:
             tailboom_start = 4 * tailboom_section
             tailboomjoints = joints[tailboom_start:]
         else:
             tailboom_start = None
             tailboomjoints = []

         trussjoints = joints[4:tailboom_start] if tailboom_start is not None else joints[4:]
    

    return nosejoints, trussjoints, tailboomjoints

def setgeom(joints, trussgeom, nosegeom, tailboomgeom):
    """
    Parameters
    ----------
    joints: vetor contendo as coordenadas dos pontos na ordem A B C D da primeira para a última seção
    trussgeom: tipo de geometria da treliça (0->warren / 1-> pratt / 2-> howe / 3-> cross)
    nosegeom: tipo de geometria do nariz
    tailboomgeom: tipo de geometria do tailboom

    What it does

    Cria a geometria da treliça a partir dos pontos gerados e do tipo de treliça escolhido. Insere o nariz e o tailboom caso as dimensões sejam diferentes de zero.
    """
    nosejoints, trussjoints, tailboomjoints = splitnosetrusstailboom(joints)

    nosemembers = warrentruss(nosejoints) if nosegeom == 0 else pratttruss(nosejoints) if nosegeom == 1 else howetruss(nosejoints) if nosegeom == 2 else crosstruss(nosejoints)
    trussmembers = warrentruss(trussjoints) if trussgeom == 0 else pratttruss(trussjoints) if trussgeom == 1 else howetruss(trussjoints) if trussgeom == 2 else crosstruss(trussjoints)
    tailboommembers = warrentruss(tailboomjoints) if tailboomgeom == 0 else pratttruss(tailboomjoints) if tailboomgeom == 1 else howetruss(tailboomjoints) if tailboomgeom == 2 else crosstruss(tailboomjoints)
    
    # Ajustar índices dos members para o sistema global
    trussmembers = [(i+4, j+4) for i, j in trussmembers]
    if tailboomjoints:
        tailboom_start = len(joints) - len(tailboomjoints)
        tailboommembers = [(i+tailboom_start, j+tailboom_start) for i, j in tailboommembers]
    
    members = nosemembers + trussmembers + tailboommembers
    return members