from assets.COLORS import *
from assets.storage import N_CLASSES
from tools.utils import CMAP

def get_stylesheet(node_size=False, classes=False, n_class=N_CLASSES, edg_col= 'grey', nd_col=DFLT_ND_CLR, edge_size=False,
                   pie=False, edg_lbl=False, nodes_opacity=1, edges_opacity=0.77,label_size=False):
    cmaps_class = CMAP[ :n_class] if n_class > 1 else [DFLT_ND_CLR]
    default_stylesheet = [
        {"selector": 'node',
         'style': {"opacity": nodes_opacity,
                   'background-color': nd_col,
                   'node-text-rotation': 'autorotate',
                   'line-color':'black',
                   'label': "data(label)",
                   'shape':'circle',
                   'color': "black", #"#1b242b"
                   'font-size': label_size,
                   'width':50,
                   'height':50
                #    'position':'data(position)'

                   },
         },
        {"selector": 'edge',
         'style': {"curve-style": "bezier",
                   'width': 'data(weight)',
                   'line-color': edg_col,
                    "opacity": edges_opacity}}]
   

    if classes:
       # default_stylesheet[0]['style'].update({"shape": "triangle"})
       list_classes = [{'selector': '.' + f'{x}',
                        'style': {'background-color': f'{x}',
                                  }} for x in cmaps_class]
       for x in list_classes:
           default_stylesheet.append(x)
    # if node_size: default_stylesheet[0]['style'].update({"width": "data(size)", "height": "data(size)"})
    if node_size: default_stylesheet[0]['style'].update({"width": "data(size)", "height": "data(size)"})
    if edge_size: default_stylesheet[1]['style'].update({"width": None})
    # if edg_col:   default_stylesheet[1]['style'].update({'line-color': edg_col})
    if edg_lbl:   default_stylesheet[1]['style'].update({'label': 'data(weight_lab)'})
    if pie:       default_stylesheet[0]['style'].update({
                                               'pie-1-background-color': '#E8747C',
                                               'pie-1-background-size': 'mapData(pie3, 0, 1, 0, 100)',
                                               'pie-2-background-color': '#f8d49d', #'#74CBE8',
                                               'pie-2-background-size': 'mapData(pie2, 0, 1, 0, 100)',
                                               'pie-3-background-color': '#5aa469',
                                               'pie-3-background-size': 'mapData(pie1, 0, 1, 0, 100)',
         })
    return default_stylesheet


download_stylesheet = [
                    {'selector': 'edge',
                        'style': {'opacity': 1, 'width': 'data(weight)',
                        "curve-style": "bezier"}},
                    {'selector': 'node',
                        "style": {'background-color': '#07ABA0',
                            "border-color": "#751225", "border-width": 5, "border-opacity": 1,
                            "opacity": 1,
                            "label": "data(label)",
                            "weight": "data(weight)",
                            'node-text-rotation': 'autorotate',
                            "color": "#1b242b",
                            "text-opacity": 1,
                            'shape': 'ellipse',
                             "font-size": 14,
                            'z-index': 999}}]

stylesheet = [{'selector': 'node',
               'style': {'content': 'data(name)',
                         'font-family': 'helvetica',
                         'font-size': 18,
                         'text-outline-width': 1,
                         'node-text-rotation': 'autorotate',
                         # 'text-outline-color': '#fff',
                         'opacity': 1,
                         'label': "data(label)",
           #              'size': "data(size)",
                         # 'background-color': "#07ABA0",
                         # 'color':'#1b242b',
                          'color': "#fff"
                         }},

              {'selector': 'edge',
               'style': {# 'line-color': "#C5D3E2",
                         'arrow-scale': 2,
                         'width': 'data(weight)',
                         'curve-style': 'bezier'}}
             ]