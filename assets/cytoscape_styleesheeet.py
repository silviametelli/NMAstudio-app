
def get_stylesheet(node_size=False, nd_col='#07ABA0', edge_size=False, pie=False, nodes_opacity=1, edges_opacity=0.75):
    default_stylesheet = [
        {"selector": 'node',
         'style': {"opacity": nodes_opacity,
                   'background-color': nd_col,
                   'line-color':'black',
                   'label': "data(label)",
                   'shape':'circle',
                   'color': "#fff"
                   },
         },
        {"selector": 'edge',
         'style': {"curve-style": "bezier",
                   #'width': 'data(weight)',
                   "opacity": edges_opacity}}]
    if node_size:
        default_stylesheet[0]['style'].update({"width": "data(size)", "height": "data(size)"})
    if edge_size:
        default_stylesheet[1]['style'].update({"width": "data(weight)"})
    if pie:
        default_stylesheet[0]['style'].update({'pie-1-background-color': '#E8747C',
                                               'pie-1-background-size': 'mapData(pie1, 0, 10, 0, 100)',
                                               'pie-2-background-color': '#74CBE8',
                                               'pie-2-background-size': 'mapData(pie2, 0, 10, 0, 100)',
                                               'pie-3-background-color': '#74E883',
                                               'pie-3-background-size': 'mapData(pie3, 0, 10, 0, 100)',})
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
                             "color": "#1b242b",
                            "text-opacity": 1,
                            'shape': 'ellipse',
                            # "font-size": 12,
                            'z-index': 9999}}]

stylesheet = [{'selector': 'node',
               'style': {'content': 'data(name)',
                         'font-family': 'helvetica',
                         'font-size': 18,
                         'text-outline-width': 1,
                         # 'text-outline-color': '#fff',
                         'opacity': 1,
                         'label': "data(label)",
           #              'size': "data(size)",
                         # 'background-color': "#07ABA0",
                         'color': "#fff"
                         }},

              {'selector': 'edge',
               'style': {# 'line-color': "#C5D3E2",
                         'arrow-scale': 2,
                         'width': 'data(weight)',
                         'curve-style': 'bezier'}}
             ]