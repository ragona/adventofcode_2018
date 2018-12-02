from graphviz import Digraph


def draw_graph_nodes(nodes, name, in_progress=None, done=None):
    dot = Digraph(name=name, format="png")

    for node in nodes:
        color = 'white'

        if in_progress and node in in_progress:
            color = 'red'
        elif done and node in done:
            color = 'green'

        dot.node(str(node.data), style='filled', fillcolor=color)

        for n in node.children:
            dot.edge(str(node.data), str(n.data))

    render_graph(dot)


def render_graph(dot):
    # render and save
    print("saving {}".format(dot.name))
    dot.render(directory='images/', view=False)
