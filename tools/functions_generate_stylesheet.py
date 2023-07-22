import dash
from assets.COLORS import *
from assets.cytoscape_styleesheeet import get_stylesheet

def __generate_stylesheet(node, slct_nodesdata, elements, slct_edgedata,
                        dd_nclr, dd_eclr, custom_nd_clr, custom_edg_clr, label_size,treat_name,dd_nds, dd_egs,
                        dwld_button, net_download_activation):

    nodes_color = (custom_nd_clr or DFLT_ND_CLR) if dd_nclr != 'Default' else DFLT_ND_CLR
    edges_color = (custom_edg_clr or None) if dd_eclr != 'Default' else None
    label_size=(label_size or None) if dd_eclr != 'Default' else None
    treat_name=(treat_name or None) if dd_eclr != 'Default' else None

    node_size = dd_nds or 'Default'
    node_size = node_size == 'Tot randomized'
    edge_size = dd_egs or 'Number of studies'
    edge_size = edge_size == 'No size'
    pie = dd_nclr == 'Risk of Bias'
    cls = dd_nclr == 'By class'
    edg_lbl = dd_eclr == 'Add label'
    FOLLOWER_COLOR, FOLLOWING_COLOR = DFLT_ND_CLR, DFLT_ND_CLR

    n_cls = elements[-1]["data"]['n_class'] if "n_class" in elements[-1]["data"] and cls else 1
    stylesheet = get_stylesheet(pie=pie, classes=cls, n_class=n_cls, edg_lbl=edg_lbl, edg_col=edges_color,
                                nd_col=nodes_color, node_size=node_size, edge_size=edge_size,label_size=label_size)
    edgedata = [el['data'] for el in elements if 'target' in el['data'].keys()]
    all_nodes_id = [el['data']['id'] for el in elements if 'target' not in el['data'].keys()]

    if treat_name is not None:
        stylesheet = get_stylesheet(pie=pie,  classes=cls,  n_class=n_cls, edg_lbl=edg_lbl, edg_col=edges_color,
                                    nd_col=nodes_color, node_size=node_size,
                                    nodes_opacity=0.2, edges_opacity=0.1,label_size=label_size) + [
                         {"selector": 'node[label = "{}"]'.format(treat_name),
                          "style": {'color':'red',"opacity": 1,'background-color':'#78131c'}}]+ [
                         {"selector": 'node[id = "{}"]'.format(id),
                          "style": {"opacity": 1}}
                         for id in all_nodes_id if id  not in treat_name]+[
                           {"selector": 'edge',
                          "style": {"opacity": 1}}  
                         ]


    if slct_nodesdata:
        selected_nodes_id = [d['id'] for d in slct_nodesdata]
        all_slct_src_trgt = list({e['source'] for e in edgedata if e['source'] in selected_nodes_id
                                  or e['target'] in selected_nodes_id}
                                 | {e['target'] for e in edgedata if e['source'] in selected_nodes_id
                                    or e['target'] in selected_nodes_id})

        stylesheet = get_stylesheet(pie=pie,  classes=cls,  n_class=n_cls, edg_lbl=edg_lbl, edg_col=edges_color,
                                    nd_col=nodes_color, node_size=node_size,
                                    nodes_opacity=0.2, edges_opacity=0.1,label_size=label_size) + [
                         {"selector": 'node[id = "{}"]'.format(id),
                          "style": {"border-color": "#751225", "border-width": 5, "border-opacity": 1,
                                    "opacity": 1}}
                         for id in selected_nodes_id] + [
                         {"selector": 'edge[id= "{}"]'.format(edge['id']),
                          "style": {'opacity': 1,  # "line-color": edges_color,
                                    'z-index': 5000}} for edge in edgedata if edge['source'] in selected_nodes_id
                                                                              or edge['target'] in selected_nodes_id] + [
                         {"selector": 'node[id = "{}"]'.format(id),
                          "style": {"opacity": 1}}
                         for id in all_nodes_id if id not in slct_nodesdata and id in all_slct_src_trgt]


    # if slct_edgedata and False:  #TODO: Not doing much at the moment
    #     for edge in edgedata:
    #         if edge['source'] in edgedata:
    #             stylesheet.append({
    #                 "selector": 'node[id = "{}"]'.format(edge['target']),
    #                 "style": {'background-color': FOLLOWING_COLOR, 'opacity': 0.9}})
    #             stylesheet.append({"selector": 'edge[id= "{}"]'.format(edge['id']),
    #                                "style": {'opacity': 0.9,
    #                                          "line-color": "blue",
    #                                          # "mid-target-arrow-color": FOLLOWING_COLOR,
    #                                          # "mid-target-arrow-shape": "vee",
    #                                          'z-index': 5000}})
    #         if edge['target'] in edgedata:
    #             stylesheet.append({"selector": 'node[id = "{}"]'.format(edge['source']),
    #                                "style": {'background-color': FOLLOWER_COLOR,
    #                                          'opacity': 0.9,
    #                                          'z-index': 9999}})
    #             stylesheet.append({"selector": 'edge[id= "{}"]'.format(edge['id']),
    #                                "style": {'opacity': 1,
    #                                          "line-color": "blue",
    #                                          "mid-target-arrow-color": FOLLOWER_COLOR,
    #                                          "mid-target-arrow-shape": "vee",
    #                                          'z-index': 5000}})


    triggered = [tr['prop_id'] for tr in dash.callback_context.triggered]
    if 'btn-get-png.n_clicks' in triggered or 'btn-get-png-modal.n_clicks' in triggered:
        stylesheet[0]['style']['color'] = 'black'
        net_download_activation = True
    else:
        net_download_activation = False


    stylesheet_modal  = stylesheet
    return stylesheet, stylesheet_modal, net_download_activation
