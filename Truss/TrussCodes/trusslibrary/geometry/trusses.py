def crosstruss(joints):
    """
    Parameters
    ----------
    joints: vetor contendo as coordenadas dos pontos na ordem A B C D da primeira para a última seção

    What it does

    Cria uma geometria de treliça com base no modelo crosstruss

    Returns
    -------
    members: vetor contendo os IDs dos pontos que cada uma das barras liga, ex: barra de ID i liga a tupla i de pontos
    """
    nsections = len(joints) // 4
    members = []
    for i in range(nsections):
        Aid = 4 * i
        Bid = Aid + 1
        Cid = Aid + 2
        Did = Aid + 3
        members.append((Aid, Bid))
        members.append((Bid, Did))
        members.append((Did, Cid))
        members.append((Cid, Aid))
        if i < (nsections - 1):
            Anextid = 4 * (i + 1)
            Bnextid = Anextid + 1
            Cnextid = Anextid + 2
            Dnextid = Anextid + 3
            if i % 2 == 0:
                members.append((Aid, Cnextid))                                        ## zigzag plano xz
                members.append((Bid, Dnextid))
                members.append((Cid, Anextid))
                members.append((Did, Bnextid))
                members.append((Aid, Bnextid))                                        ## zigzag plano xy
                members.append((Did, Cnextid))
                members.append((Bid, Anextid))
                members.append((Cid, Dnextid))
            if i % 2 == 1:
                members.append((Cid, Anextid))                                        ## zigzag plano xz
                members.append((Did, Bnextid))
                members.append((Aid, Cnextid))
                members.append((Bid, Dnextid))
                members.append((Bid, Anextid))                                        ## zigzag plano xy
                members.append((Cid, Dnextid))
                members.append((Aid, Bnextid))
                members.append((Did, Cnextid))
    return members

def warrentruss(joints):
    """
    Parameters
    ----------
    joints: vetor contendo as coordenadas dos pontos na ordem A B C D da primeira para a última seção

    What it does

    Cria uma geometria de treliça com base no modelo warren

    Returns
    -------
    members: vetor contendo os IDs dos pontos que cada uma das barras liga, ex: barra de ID i liga a tupla i de pontos
    """
    nsections = len(joints) // 4
    members = []
    for i in range(nsections):
        Aid = 4 * i
        Bid = Aid + 1
        Cid = Aid + 2
        Did = Aid + 3
        members.append((Aid, Bid))
        members.append((Bid, Did))
        members.append((Did, Cid))
        members.append((Cid, Aid))
        if i < (nsections - 1):
            Anextid = 4 * (i + 1)
            Bnextid = Anextid + 1
            Cnextid = Anextid + 2
            Dnextid = Anextid + 3
            members.append((Aid, Anextid))
            members.append((Bid, Bnextid))
            members.append((Cid, Cnextid))
            members.append((Did, Dnextid))
            if i % 2 == 0:
                members.append((Aid, Cnextid))                                        ## zigzag plano xz
                members.append((Bid, Dnextid))
                members.append((Aid, Bnextid))                                        ## zigzag plano xy
                members.append((Did, Cnextid))
            if i % 2 == 1:
                members.append((Cid, Anextid))                                        ## zigzag plano xz
                members.append((Did, Bnextid))
                members.append((Bid, Anextid))                                        ## zigzag plano xy
                members.append((Cid, Dnextid))
    return members

def pratttruss(joints):
    """
    Parameters
    ----------
    joints: vetor contendo as coordenadas dos pontos na ordem A B C D da primeira para a última seção

    What it does

    Cria uma geometria de treliça com base no modelo pratt

    Returns
    -------
    members: vetor contendo os IDs dos pontos que cada uma das barras liga, ex: barra de ID i liga a tupla i de pontos
    """
    nsections = len(joints) // 4
    members = []
    for i in range(nsections):
        Aid = 4 * i
        Bid = Aid + 1
        Cid = Aid + 2
        Did = Aid + 3
        members.append((Aid, Bid))
        members.append((Bid, Did))
        members.append((Did, Cid))
        members.append((Cid, Aid))
        if i < (nsections - 1):
            Anextid = 4 * (i + 1)
            Bnextid = Anextid + 1
            Cnextid = Anextid + 2
            Dnextid = Anextid + 3
            members.append((Aid, Anextid))
            members.append((Bid, Bnextid))
            members.append((Cid, Cnextid))
            members.append((Did, Dnextid))
            if i < (nsections // 2):
                members.append((Cid, Anextid))    ## plano xz
                members.append((Did, Bnextid))
                members.append((Aid, Bnextid))    ## zigzag plano xy
                members.append((Did, Cnextid))
                if (nsections % 2 == 0) and (i + 1 == nsections // 2):
                    members.append((Aid, Cnextid))    ## se for par tem q fazer x no meio
                    members.append((Did, Bnextid))
            if i >= (nsections // 2):                                             ## forma um x no meio se for impar
                members.append((Aid, Cnextid))    ## plano xz
                members.append((Bid, Dnextid))
                members.append((Aid, Bnextid))    ## zigzag plano xy
                members.append((Did, Cnextid))
    return members

def howetruss(joints):
    """
    Parameters
    ----------
    joints: vetor contendo as coordenadas dos pontos na ordem A B C D da primeira para a última seção

    What it does

    Cria uma geometria de treliça com base no modelo howe

    Returns
    -------
    members: vetor contendo os IDs dos pontos que cada uma das barras liga, ex: barra de ID i liga a tupla i de pontos
    """
    nsections = len(joints) // 4
    members = []
    for i in range(nsections):
        Aid = 4 * i
        Bid = Aid + 1
        Cid = Aid + 2
        Did = Aid + 3
        members.append((Aid, Bid))
        members.append((Bid, Did))
        members.append((Did, Cid))
        members.append((Cid, Aid))
        if i < (nsections - 1):
            Anextid = 4 * (i + 1)
            Bnextid = Anextid + 1
            Cnextid = Anextid + 2
            Dnextid = Anextid + 3
            members.append((Aid, Anextid))
            members.append((Bid, Bnextid))
            members.append((Cid, Cnextid))
            members.append((Did, Dnextid))
            if i < (nsections // 2):
                members.append((Aid, Cnextid))    ## plano xz
                members.append((Bid, Dnextid))
                members.append((Aid, Bnextid))    ## zigzag plano xy
                members.append((Did, Cnextid))
                if (nsections % 2 == 0) and (i + 1 == nsections // 2):
                    members.append((Cid, Anextid))    ## se for par tem q fazer x no meio
                    members.append((Bid, Dnextid))
            if i >= (nsections // 2):                                             ## forma um x no meio se for impar
                members.append((Cid, Anextid))    ## plano xz
                members.append((Did, Bnextid))
                members.append((Aid, Bnextid))    ## zigzag plano xy
                members.append((Did, Cnextid))
    return members

