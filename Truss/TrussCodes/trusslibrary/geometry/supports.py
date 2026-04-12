def generatesupports(pinados, joints):
    """
    Parameters
    ----------
    pinados : recebe ID dos nós que serão pinados
    joints: vetor contendo as coordenadas dos pontos na ordem A B C D da primeira para a última seção

    What it does

    Os IDS especificados em pinados serão pinados, e os demais serão livres

    Returns
    -------
    supports: vetor contendo os tipos de suporte para cada nó na mesma ordem de joints
    """
    from slientruss3d.type import SupportType
    supports = len(joints) * [SupportType.NO]
    for i in pinados:
        supports[i] = SupportType.PIN
    return supports