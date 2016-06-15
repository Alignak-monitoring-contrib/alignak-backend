from alignak_backend.models import register_models

from graphviz import Digraph

dot = Digraph(format='png')
#dot.node_attr.update(color='lightblue2', style='filled')
#dot.graph_attr.update(nodesep='0.1')
dot.graph_attr.update(size="140,140")
#dot.edge_attr.update(weight='2.1')

models = register_models()

done = []
for name, schema in models.iteritems():
    for key, value in schema['schema'].iteritems():
        if not key.startswith("_"):
            if value['type'] == 'objectid':
                if name + " \/ " + value['data_relation']['resource'] not in done:
                    dot.edge(name, value['data_relation']['resource'])
                    done.append(name + " \/ " + value['data_relation']['resource'])
            elif value['type'] == 'list' and 'schema' in value:
                if value['schema']['type'] == 'objectid':
                    if name + " \/ " + value['schema']['data_relation']['resource'] not in done:
                        dot.edge(name, value['schema']['data_relation']['resource'])
                        done.append(name + " \/ " + value['schema']['data_relation']['resource'])

dot.render('model_schema', view=False)