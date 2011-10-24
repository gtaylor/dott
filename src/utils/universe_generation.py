import math, random
import networkx as nx


def get_universe():
    """
    Creates a universe and returns a dict with important universe information
    """

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

def create_spiral_galaxy(system_count=100, spirals=2):
    sep = 2*math.pi/spirals

    spiral_list = []

    for x in range(spirals):
        spiral_list.append(x*sep)


    galaxy = {}

    for system in range(system_count):
        spiral_id = random.randint(0,spirals-1)
        length = random.random()
        dev_x = random.random()*0.15*random.choice([-1,1])
        dev_y = random.random()*0.15*random.choice([-1,1])
        dev_z = random.random()*0.05*random.choice([-1,1])
        spiral_flow = length*((90.0/180.0)/math.pi)+spiral_list[spiral_id]
        #spiral_flow = spiral_list[spiral_id]
        
        pos_x = math.cos(spiral_flow)*length+dev_x
        pos_y = math.sin(spiral_flow)*length+dev_y
        pos_z = dev_z

        galaxy[system] = {
            'position_x': pos_x,
            'position_y': pos_y,
            'position_z': pos_z,
            'id': system
        }

    return galaxy
        
def link_galaxy(galaxy, link_levels):

    for system in galaxy:
        galaxy[system]["link_level"] = random.choice(link_levels)

    for system in galaxy:
        # sort galaxy by nearest neighbors
        neighbors = []
        for nei in galaxy:
            if nei != system:
                dx = galaxy[nei]['position_x'] - galaxy[system]['position_x']
                dy = galaxy[nei]['position_y'] - galaxy[system]['position_y']
                dz = galaxy[nei]['position_z'] - galaxy[system]['position_z']
                dist = math.sqrt(dx*dx+dy*dy+dz*dz)
                neighbors.append((dist,nei))

        neighbors = sorted(neighbors, key=lambda foo: foo[0]) #sort by dist

        for link in range(galaxy[system]['link_level']):
            # find it
            satisfied = False
            while not satisfied:
                try:
                    nearest = neighbors.pop(0)[1]
                except IndexError:
                    satisfied = True
                    continue
                
                try:
                    linksize = len(galaxy[nearest]['destinations'])
                except KeyError:
                    linksize = 0
                    galaxy[nearest]['destinations'] = []

                if galaxy[nearest]['link_level'] > linksize:
                    galaxy[nearest]['destinations'].append(system)

                    try:
                        galaxy[system]['destinations'].append(nearest)
                    except:
                        galaxy[system]['destinations'] = [nearest]

                    satisfied = True
    return galaxy

def define_galaxy_security(galaxy, security_depth):
    G = nx.Graph()

    for system in galaxy:
        for dest in galaxy[system]['destinations']:
            G.add_edge(system, dest)

    for system in galaxy:
        if nx.shortest_path_length(G,source=system, target=1) > security_depth:
            galaxy[system]["security"] = 0
        else:
            galaxy[system]["security"] = 1

    return galaxy

def plot_kml(galaxy):
    from pykml.factory import KML_ElementMaker as KML
    from lxml import etree

    fld = KML.kml()

    for system in galaxy:
        a = KML.Placemark(
            KML.name('foo'),
            KML.Point(
                KML.coordinates('%f,%f' % (galaxy[system]["position_x"],galaxy[system]["position_y"]))
            )
        )
        fld.append(a)

        for dest in galaxy[system]['destinations']:
            a = KML.Placemark(
                KML.name("foo"),
                KML.LineString(
                    KML.coordinates(
                        "%s,%s %s,%s" % (galaxy[system]["position_x"],galaxy[system]["position_y"], galaxy[dest]["position_x"],galaxy[dest]["position_y"])
                    )
                )
            )
            fld.append(a)

    f = open("test.kml", 'wa')

    f.write(etree.tostring(fld, pretty_print=True))
    f.close()

def woot():
    gal = create_spiral_galaxy(system_count=1000, spirals=5)
    gal = link_galaxy(gal, [2,3,4])
    plot_kml(gal)