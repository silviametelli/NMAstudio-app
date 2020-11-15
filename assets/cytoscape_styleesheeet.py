
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

download_stylesheet = [
    {"selector": 'node',
     'style': {"opacity": 1,
               'background-color': "#07ABA0",
               'label': "data(label)",
               'color': "#1b242b"}},
    {"selector": 'edge',
     'style': {"curve-style": "bezier",
               'width': 'data(weight)',
               "opacity": 0.75}}]

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