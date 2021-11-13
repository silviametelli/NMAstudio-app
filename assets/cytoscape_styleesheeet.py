from assets.COLORS import *
from demo_data import get_demo_data
from utils import get_network
from  collections  import OrderedDict


GLOBAL_DATA = get_demo_data()
if "treat1_class" and "treat2_class" in GLOBAL_DATA['net_data'].columns:
    import matplotlib
    from matplotlib import cm
    cmaps = OrderedDict()
    blues = cm.get_cmap('Blues', 128)
    viridis = cm.get_cmap('viridis', 128)
    GLOBAL_DATA['n_class'] = get_network(GLOBAL_DATA['net_data'])[-1]["data"]['n_class']
    cmaps['Sequential'] = [matplotlib.colors.rgb2hex(viridis(i)) for i in range(0, viridis.N, 1)]
    cmaps['Sequential'] = ['purple','green','blue','red','black','yellow','black','orange','pink']
    cmaps_class = cmaps['Sequential'][ :GLOBAL_DATA['n_class'] ]
else:
    cmaps = OrderedDict()
    cmaps_class = None


def get_stylesheet(node_size=False, classes = False, edg_col= False, nd_col=DFLT_ND_CLR, edge_size=False,
                   pie=False, edg_lbl=False, nodes_opacity=1, edges_opacity=0.75):
    default_stylesheet = [
        {"selector": 'node',
         'style': {"opacity": nodes_opacity,
                   'background-color': nd_col,
                   'node-text-rotation': 'autorotate',
                   'line-color':'black',
                   'label': "data(label)",
                   'shape':'circle',
                   'color': "#fff" #"#1b242b"
                   },
         },
        {"selector": 'edge',
         'style': {"curve-style": "bezier",
                   'width': 'data(weight)',
                   #'line-color':edg_col,
                    "opacity": edges_opacity}}]
    if node_size:
        default_stylesheet[0]['style'].update({"width": "data(size)", "height": "data(size)"})
    if classes:
       # default_stylesheet[0]['style'].update({"shape": "triangle"})
       list_classes = [{'selector': '.' + f'{x}',
                        'style': {'background-color': f'{x}',
                                  }} for x in cmaps_class]
       for x in list_classes:
           default_stylesheet.append(x)
    if edge_size:
        default_stylesheet[1]['style'].update({"width": None})
    if edg_lbl:
        default_stylesheet[1]['style'].update({'label': 'data(weight)'})
    if pie:
        default_stylesheet[0]['style'].update({
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