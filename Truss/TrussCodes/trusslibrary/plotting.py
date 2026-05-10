import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import plotly.graph_objects as go
import trusslibrary as tl

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
        if len(v) > 0:
            has_positive = any(val > 0 for val in v)
            has_negative = any(val < 0 for val in v)
            
            if has_positive and has_negative:
                # Tração e compressão: usa colormap completo coolwarm
                norm = colors.Normalize(vmin=min(v), vmax=max(v))
                colormap = plt.colormaps[cmap]
            elif has_positive:
                # Só tração: usa colormap vermelho (fraco para forte)
                v_pos = [val for val in v if val > 0]
                vmin_pos = min(v_pos) * 0.01 if min(v_pos) > 0 else min(v_pos)
                norm = colors.Normalize(vmin=vmin_pos, vmax=max(v_pos))
                colormap = plt.colormaps['Reds']
            elif has_negative:
                # Só compressão: usa colormap azul (fraco para forte)
                v_neg = [val for val in v if val < 0]
                # Ajustar vmax para garantir que o máximo tenha cor visível
                vmax_neg = max(v_neg) * 0.01 if max(v_neg) < 0 else max(v_neg)
                norm = colors.Normalize(vmin=min(v_neg), vmax=vmax_neg)
                colormap = plt.colormaps['Blues_r']  # _r para reverter (azul fraco para forte)
            else:
                # Todos zero: usa azul padrão
                norm = colors.Normalize(vmin=0, vmax=1)
                colormap = plt.colormaps['Blues']
                
            # Configurar barra de cores
            if len(v) > 0:
                # Determinar qual colormap usar para a barra de cores
                if has_positive and has_negative:
                    colorbar_cmap = cmap
                elif has_positive:
                    colorbar_cmap = 'Reds'
                elif has_negative:
                    colorbar_cmap = 'Blues_r'
                else:
                    colorbar_cmap = 'Blues'
                
                sm = cm.ScalarMappable(norm=norm, cmap=colorbar_cmap)
                plt.colorbar(sm, ax=ax, label=label)
        else:
            norm = colors.Normalize(vmin=0, vmax=1)
            colormap = plt.colormaps['Blues']
    else:
        norm = colors.Normalize(vmin=0, vmax=1)
        colormap = plt.colormaps['Blues']

    for memberID, (_, _, member) in trussmembers.items():
        joint0 = member._Member__joint0
        joint1 = member._Member__joint1

        if isinstance(joint0, dict):
            x1, y1, z1 = joint0['coords']
        else:
            x1, y1, z1 = joint0
        if isinstance(joint1, dict):
            x2, y2, z2 = joint1['coords']
        else:
            x2, y2, z2 = joint1

        value = values.get(memberID, 0.0)   ## pega pelo ID, se nao der usa como 0
        color = colormap(norm(value))
        
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

        if isinstance(joints[j0], dict):
            x1, y1, z1 = joints[j0]['coords']
            x2, y2, z2 = joints[j1]['coords']
        else:
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
        
        elif view == "front":  # YZ
            ax.plot([y1, y2], [z1, z2],
                    color='black', linewidth=linewidth)

    for i, joint in enumerate(joints):
        if isinstance(joint, dict):
            x, y, z = joint['coords']
        else:
            x, y, z = joint

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

        if isinstance(joints[jointID], dict):
            x, y, z = joints[jointID]['coords']
        else:
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

def plot_truss_fluid(joints, members):
    """
    Prints truss at a better viewer so that you can easily see and move the camera
    """
    # extrai coordenadas
    coords = [j['coords'] if isinstance(j, dict) else j for j in joints]
    
    # traça os members como linhas
    edge_x, edge_y, edge_z = [], [], []
    for i, j in members:
        x0, y0, z0 = coords[i]
        x1, y1, z1 = coords[j]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
        edge_z += [z0, z1, None]

    edges = go.Scatter3d(x=edge_x, y=edge_y, z=edge_z,
                         mode='lines', line=dict(color='steelblue', width=3))

    # traça os joints como pontos
    nodes = go.Scatter3d(x=[c[0] for c in coords],
                         y=[c[1] for c in coords],
                         z=[c[2] for c in coords],
                         mode='markers', marker=dict(size=4, color='red'))

    fig = go.Figure(data=[edges, nodes])
    fig.update_layout(scene=dict(aspectmode='data'))  # escala real dos eixos
    fig.show()

def truss_deliverable(joints, members, member_types_dict=None, export_html=None, export_csv=None):
    coords = [j['coords'] if isinstance(j, dict) else j for j in joints]

    SECTION_COLORS = {
        'nose':        '#e74c3c',
        'fuselage_1':  '#3498db',
        'fuselage_2':  '#2ecc71',
        'tailboom':    '#f39c12',
        'landinggear': '#9b59b6',
        'encaixe':     '#1abc9c',
        'unknown':     '#95a5a6',
    }

    from collections import defaultdict
    section_members = defaultdict(list)
    for i, j in members:
        label = tl.get_section_label(i, j, joints, member_types_dict) or 'unknown' if member_types_dict else 'unknown'
        section_members[label].append((i, j))

    traces = []
    for label, mlist in section_members.items():
        edge_x, edge_y, edge_z = [], [], []
        for i, j in mlist:
            x0, y0, z0 = coords[i]
            x1, y1, z1 = coords[j]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]
            edge_z += [z0, z1, None]
        color = SECTION_COLORS.get(label, '#95a5a6')
        traces.append(go.Scatter3d(
            x=edge_x, y=edge_y, z=edge_z,
            mode='lines', line=dict(color=color, width=3), name=label
        ))

    traces.append(go.Scatter3d(
        x=[c[0] for c in coords],
        y=[c[1] for c in coords],
        z=[c[2] for c in coords],
        mode='markers', marker=dict(size=4, color='red'), name='joints',
        text=[f'J{idx}: ({c[0]:.1f}, {c[1]:.1f}, {c[2]:.1f})' for idx, c in enumerate(coords)],
        hoverinfo='text'
    ))

    fig = go.Figure(data=traces)
    fig.update_layout(scene=dict(aspectmode='data'), legend=dict(title='Seção'))
    fig.show()

    if export_html:
        fig.write_html(export_html, include_plotlyjs='cdn')
        print(f"HTML exportado: {export_html}")

    if export_csv:
        # calcula larguras de coluna para alinhar
        joint_rows = [[str(idx), f'{c[0]:.2f}', f'{c[1]:.2f}', f'{c[2]:.2f}']
                      for idx, c in enumerate(coords)]

        member_rows = []
        for mid, (i, j) in enumerate(members):
            label = tl.get_section_label(i, j, joints, member_types_dict) or 'unknown' if member_types_dict else 'unknown'
            mt = member_types_dict.get(label) if member_types_dict else None
            d = f'{getattr(mt, "d", 0):.4f}' if mt else ''
            x0, y0, z0 = coords[i]
            x1, y1, z1 = coords[j]
            member_rows.append([
                str(mid), str(i), str(j), label, d,
                f'{x0:.2f}', f'{y0:.2f}', f'{z0:.2f}',
                f'{x1:.2f}', f'{y1:.2f}', f'{z1:.2f}'
            ])

        def format_table(headers, rows):
            widths = [len(h) for h in headers]
            for row in rows:
                for k, val in enumerate(row):
                    widths[k] = max(widths[k], len(val))
            sep = '  '
            lines = []
            lines.append(sep.join(h.ljust(widths[k]) for k, h in enumerate(headers)))
            lines.append(sep.join('-' * widths[k] for k in range(len(headers))))
            for row in rows:
                lines.append(sep.join(val.ljust(widths[k]) for k, val in enumerate(row)))
            return '\n'.join(lines)

        joint_headers  = ['joint_id', 'x', 'y', 'z']
        member_headers = ['member_id', 'j0', 'j1', 'section', 'diameter',
                          'x0', 'y0', 'z0', 'x1', 'y1', 'z1']

        with open(export_csv, 'w') as f:
            f.write('VERTICES\n')
            f.write(format_table(joint_headers, joint_rows))
            f.write('\n\nMEMBROS\n')
            f.write(format_table(member_headers, member_rows))

        print(f"CSV exportado: {export_csv}")

def plottruss_sections(truss, trussmembers, members_list, joints, view, member_types_dict=None, d_scale=2.0, title=None):
    """
    Plota a treliça com cores por seção (nose, fuselage_1, fuselage_2, tailboom, landinggear).
    """

    SECTION_COLORS = {
        'nose':        '#e74c3c',
        'fuselage_1':  '#3498db',
        'fuselage_2':  '#2ecc71',
        'tailboom':    '#f39c12',
        'landinggear': '#9b59b6',
        'unknown':     '#95a5a6',
    }

    fig = plt.figure()
    if view == "3d":
        ax = fig.add_subplot(111, projection="3d")
    else:
        ax = fig.add_subplot(111)

    # monta lookup memberID -> (j0, j1)
    memberid_to_joints = {}
    for idx, (j0, j1) in enumerate(members_list):
        memberid_to_joints[idx] = (j0, j1)

    seen_labels = {}  # para a legenda

    for memberID, (_, _, member) in trussmembers.items():
        joint0 = member._Member__joint0
        joint1 = member._Member__joint1

        if isinstance(joint0, dict):
            x1, y1, z1 = joint0['coords']
        else:
            x1, y1, z1 = joint0
        if isinstance(joint1, dict):
            x2, y2, z2 = joint1['coords']
        else:
            x2, y2, z2 = joint1

        # classifica a seção
        if memberID in memberid_to_joints:
            j0, j1 = memberid_to_joints[memberID]
            label = tl.get_section_label(j0, j1, joints, member_types_dict) or 'unknown'
        else:
            label = 'unknown'

        color = SECTION_COLORS.get(label, '#95a5a6')

        # diâmetro pelo memberType se disponível
        if member_types_dict and label != 'unknown':
            mt = member_types_dict.get(label)
            diameter = getattr(mt, 'diameter', 2.0) if mt else 2.0
        else:
            diameter = 2.0
        linewidth = diameter * d_scale / 2.0

        kwargs = dict(color=color, linewidth=linewidth,
                      label=label if label not in seen_labels else '_nolegend_')
        seen_labels[label] = True

        if view == "3d":
            ax.plot([x1, x2], [y1, y2], [z1, z2], **kwargs)
        elif view == "top":
            ax.plot([x1, x2], [y1, y2], **kwargs)
        elif view == "side":
            ax.plot([x1, x2], [z1, z2], **kwargs)

    ax.legend(loc='best')
    if title:
        ax.set_title(title)
    ax.set_aspect("equal")
    plt.show()