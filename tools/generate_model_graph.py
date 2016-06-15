from alignak_backend.models import register_models

from graphviz import Digraph

dot = Digraph(format='png',)
#dot.node_attr.update(color='lightblue2', style='filled')
#dot.graph_attr.update(nodesep='0.1')
dot.graph_attr.update(size="140,140")
#dot.edge_attr.update(weight='2.1')

models = register_models()

for name, schema in models.iteritems():
    color = ''
    if name == 'host':
       color = 'red'
    elif name == 'service':
       color = 'green'
    dot.node(name, color=color)
    for key, value in schema['schema'].iteritems():
        style = 'dashed'
        if 'required' in value and value['required']:
            style = 'solid'
        if not key.startswith("_"):
            if value['type'] == 'objectid':
                dot.edge(name, value['data_relation']['resource'], color=color, label=key, fontcolor=color, style=style)
            elif value['type'] == 'list' and 'schema' in value:
                if value['schema']['type'] == 'objectid':
                    dot.edge(name, value['schema']['data_relation']['resource'], color=color, label=key, fontcolor=color, style=style)

dot.render('model_schema', view=False)