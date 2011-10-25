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
    """
    Creates a spiral galaxy with given spirals (arms) and system count.
    The galaxy is unlinked and just creates the galaxy shape
    """
    sep = 2*math.pi/spirals

    spiral_list = []

    for x in range(spirals):
        spiral_list.append(x*sep)


    galaxy = {}

    for system in range(system_count):
        spiral_id = random.randint(0,spirals-1)
        length = random.random()
        dev_x = random.random()*random.choice([-1,1])*(1.0-length)*0.3
        dev_y = random.random()*random.choice([-1,1])*(1.0-length)*0.3
        dev_z = random.random()*random.choice([-1,1])*(1.0-length)*0.3
        spiral_flow = length*(math.pi*(36.0/180.0))+spiral_list[spiral_id]
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
    """
    Connects unconnected systems together.  Each system is randomly assigned a link level.
    Link level represents the total number of connected systems to any one system.
    Link level is randomly chosen from an array link_levels which should be an array of integers
    """

    # Loop though the galaxy and assign link levels
    for system in galaxy:
        galaxy[system]["link_level"] = random.choice(link_levels)

    # Once link levels are defined
    # Loop though again and assign jumps based on distance
    for system in galaxy:
        # sort galaxy by nearest neighbors
        neighbors = []
        # Calculate distances between stars
        for nei in galaxy:
            if nei != system:
                dx = galaxy[nei]['position_x'] - galaxy[system]['position_x']
                dy = galaxy[nei]['position_y'] - galaxy[system]['position_y']
                dz = galaxy[nei]['position_z'] - galaxy[system]['position_z']
                dist = math.sqrt(dx*dx+dy*dy+dz*dz)
                neighbors.append((dist,nei))

        # Sort by distance
        neighbors = sorted(neighbors, key=lambda foo: foo[0]) #sort by dist

        # Assign links based on system's link level
        for link in range(galaxy[system]['link_level']):
            # find it
            satisfied = False
            while not satisfied:
                try:
                    nearest = neighbors.pop(0)[1]
                except IndexError:
                    satisfied = True
                    continue

                # Determine how many systems target is already linked with
                try:
                    linksize = len(galaxy[nearest]['destinations'])
                except KeyError:
                    # destinations not found, system is unlinked
                    linksize = 0
                    galaxy[nearest]['destinations'] = []

                # See if target system has room for one more link
                if galaxy[nearest]['link_level'] > linksize:
                    # Add source system to target system
                    galaxy[nearest]['destinations'].append(system)

                    # Add target system to source system making sure destinations exists first
                    try:
                        galaxy[system]['destinations'].append(nearest)
                    except:
                        galaxy[system]['destinations'] = [nearest]

                    # All links found for source system
                    satisfied = True

    # Pass the altered galaxy back
    return galaxy

def define_galaxy_security(galaxy, security_depth):
    """
    Defines the security for a galaxy.
    Creates a secure zone focused around system 1 padded out to security_depth
    """
    G = nx.Graph()

    # Create a graph so we can determine depth to system 1
    for system in galaxy:
        for dest in galaxy[system]['destinations']:
            G.add_edge(system, dest)

    # Loop though the galaxy
    for system in galaxy:
        # Determine depth and assign security
        if nx.shortest_path_length(G,source=system, target=1) > security_depth:
            galaxy[system]["security"] = 0
        else:
            galaxy[system]["security"] = 1

    return galaxy

def plot_kml(galaxy):
    """
    Hacky function to dump a galaxy to a kml.  Be sure pykml is installed before using.
    """
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

def create_full_galaxy():
    """
    Creates a galaxy in its final form.
    """
    gal = create_spiral_galaxy(system_count=100, spirals=5)
    gal = link_galaxy(gal, [1,2,2,3,3,3,4])
    gal = define_galaxy_security(gal, 4)

    return gal
