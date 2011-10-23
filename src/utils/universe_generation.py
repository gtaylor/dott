

def get_universe():
    """
    Creates a universe and returns a dict with important universe information
    """

    import networkx as nx

    # Generate a connected network of nodes
    G = nx.newman_watts_strogatz_graph(100,2,0.9)

    # Assign a 2d position to the nodes
    locs = nx.spectral_layout(G)

    # Create the Solar Systems by looping though the node list created by networkx
    systemlist = {}

    for node in G.nodes():
        system = dict()
        system["name"] = 'Unnamed System SX-%s' % node

        dests = []
        for dest in G[node]:
            dests.append(dest)

        system["destinations"] = dests

        system["coordinates"] = locs[node]

        # Determine security level by distance to node 1
        if nx.shortest_path_length(G,source=node, target=1) > 3:
            system["security"] = 0
        else:
            system["security"] = 1

        systemlist[node] = system

    # Create a security zone from

    return systemlist

