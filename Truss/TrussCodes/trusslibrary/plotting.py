import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors

def plottruss(truss, trussmembers, view, values, label=None, title=None, cmap='coolwarm', member_diameters=None, d_scale=2.0):
    """
    Parameters
    ----------
    truss : objeto truss
    trussmembers : dict com os membros da trelica
    view : lateral, superior ou 3d
    values : dict contendo qual deve ser a informacao pro colormap da trelica
    label: label para inserir no plot
    cmap: mapa de cor usado, o coolwarm é interessante pq mostra tração em vermelho e compressão em azul
    label: opcional , label para o colorbar
    title: opcional, título para o gráfico
    member_diameters: dict opcional com diâmetros dos membros {memberID: diâmetro}
    d_scale: fator de escala para converter diâmetro em largura da linha (padrão: 2.0)

    What it does

    Plota a treliça de acordo com as configurações solicitadas pelo usuário
    Se member_diameters for fornecido, diferencia a largura das linhas por diâmetro
    """
    fig = plt.figure()
    if view == "3d":
        ax = fig.add_subplot(111, projection="3d")
    else:
        ax = fig.add_subplot(111)

    # normalização do mapa de cores
    if values is not None:
        v = list(values.values())
        norm = colors.Normalize(vmin=min(v), vmax=max(v))
        colormap = plt.colormaps[cmap]
    else:
        colormap = None

    for memberID, (_, _, member) in trussmembers.items():
        joint0 = member._Member__joint0
        joint1 = member._Member__joint1

        x1, y1, z1 = joint0
        x2, y2, z2 = joint1

        if colormap is not None:
            value = values.get(memberID, 0.0)   ## pega pelo ID, se nao der usa como 0

        if colormap is not None:
            color = colormap(norm(value))
        else:
            color = 'blue'
        
        # Determinar largura da linha baseado no diâmetro se fornecido
        if member_diameters is not None:
            diameter = member_diameters.get(memberID, 2.0)  # memberID é equivalente ao índice
            linewidth = diameter * d_scale / 2.0
        else:
            linewidth = 2

        if view == "3d":
            ax.plot([x1, x2],
                    [y1, y2],
                    [z1, z2],
                    color=color,
                    linewidth=linewidth)

        elif view == "top":     # XY
            ax.plot([x1, x2],
                    [y1, y2],
                    color=color,
                    linewidth=linewidth)

        elif view == "side":    # XZ
            ax.plot([x1, x2],
                    [z1, z2],
                    color=color,
                    linewidth=linewidth)

    if title is not None:
        ax.set_title(title)

    if colormap is not None:
        sm = cm.ScalarMappable(norm=norm, cmap=cmap)
        plt.colorbar(sm, ax=ax, label=label)

    ax.set_aspect("equal")
    plt.show()

def plottrussBC(joints, supports, forces, members,
                view="3d", scale_force=1.0,
                title=None, member_diameters=None, d_scale=2.0):
    """
    Parameters
    ----------
    joints : recebe joints, que armazena as coordenadas dos pontos.
    supports : vetor contendo os tipos de suporte para cada nó na mesma ordem de joints
    forces : ID das forças e vetor de força
    members: vetor contendo os IDs dos pontos que cada uma das barras liga, ex: barra de ID i liga a tupla i de pontos
    view: 3d, side ou top
    scale_force: permite reescalar a força
    title: título, opcional
    member_diameters: dict opcional com diâmetros dos membros {(j0, j1): diâmetro}
    d_scale: fator de escala para converter diâmetro em largura da linha (padrão: 2.0)

    What it does

    Plota a treliça e condicões de contorno: forças em verde, nós livres em azul e nós pinados em vermelho
    Se member_diameters for fornecido, diferencia a largura das linhas por diâmetro
    """
    fig = plt.figure()

    if view == "3d":
        ax = fig.add_subplot(111, projection="3d")
    else:
        ax = fig.add_subplot(111)

    for member_idx, (j0, j1) in enumerate(members):

        x1, y1, z1 = joints[j0]
        x2, y2, z2 = joints[j1]
        
        # Determinar largura da linha baseado no diâmetro se fornecido
        if member_diameters is not None:
            diameter = member_diameters.get(member_idx, 2.0)  # Usa índice unificado
            linewidth = diameter * d_scale / 2.0
        else:
            linewidth = 1.5

        if view == "3d":
            ax.plot([x1, x2], [y1, y2], [z1, z2],
                    color='black', linewidth=linewidth)

        elif view == "top":   # XY
            ax.plot([x1, x2], [y1, y2],
                    color='black', linewidth=linewidth)

        elif view == "side":  # XZ
            ax.plot([x1, x2], [z1, z2],
                    color='black', linewidth=linewidth)

    for i, (x, y, z) in enumerate(joints):

        support = supports[i]

        # nó livre
        marker = 'o'
        color = 'blue'

        # nó fixo
        if support == 1:
            marker = '^'
            color = 'red'

        if view == "3d":
            ax.scatter(x, y, z,
                       marker=marker,
                       color=color,
                       s=40)

        elif view == "top":
            ax.scatter(x, y,
                       marker=marker,
                       color=color,
                       s=40)

        elif view == "side":
            ax.scatter(x, z,
                       marker=marker,
                       color=color,
                       s=40)

    for jointID, force in forces:

        x, y, z = joints[jointID]
        fx, fy, fz = force

        fx *= scale_force
        fy *= scale_force
        fz *= scale_force

        if view == "3d":
            ax.quiver(x, y, z, fx, fy, fz,
                      color='green')

        elif view == "top":
            ax.quiver(x, y, fx, fy,
                      color='green')

        elif view == "side":
            ax.quiver(x, z, fx, fz,
                      color='green')

    ax.set_aspect("equal")

    if title:
        ax.set_title(title)

    plt.show()