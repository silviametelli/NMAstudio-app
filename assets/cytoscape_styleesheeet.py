
default_stylesheet = [
    {"selector": 'node',
     'style': {"opacity": 1,
               'background-color': "#07ABA0",
               'label': "data(label)",
               'color': "#fff"}},
    {"selector": 'edge',
     'style': {"curve-style": "bezier",
               'width': 'data(weight)',
               "opacity": 0.75}}]

# download_stylesheet = [
#     {"selector": 'node',
#      'style': {"opacity": 1,
#                'background-color': "#07ABA0",
#                'label': "data(label)",
#                'color': "#1b242b"}},
#     {"selector": 'edge',
#      'style': {"curve-style": "bezier",
#                'width': 'data(weight)',
#                "opacity": 0.75}}]

download_stylesheet = [
                    {'selector': 'edge',
                        'style': {'opacity': 1, 'width': 'data(weight)',
                        "curve-style": "bezier"}},
                    {'selector': 'node',
                        "style": {'background-color': '#07ABA0',
                            "border-color": "#751225", "border-width": 5, "border-opacity": 1,
                            "opacity": 1,
                            "label": "data(label)",
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
                         # 'background-color': "#07ABA0",
                         'color': "#fff"
                         }},

              {'selector': 'edge',
               'style': {# 'line-color': "#C5D3E2",
                         'arrow-scale': 2,
                         'width': 'data(weight)',
                         'curve-style': 'bezier'}}
             ]