# -*- coding=utf-8 -*-

#generate chunks and neglinks to be used in DCA distance metric learning algorithm
#two input files
#usercategory.txt:
#   this file specify user category relationship,
#   each line in this file identify one user,
#   if user belongs to some category, then the corresponding column is set to 1
#edges.txt
#   each line is of the form (node1, node2) represent that node1 has a edge to node2
#   for undirected graph, there is a symmetric entry, i.e, if (node2, node1) also appears in edges
#   note: node ids begin from 1, not 0.

#what need to do when change data set:
    #change file directory
    #different split symbol for edges.txt
    #change macros for nodes num and category num

import random
from collections import deque
import operator

#NUM_FEATURE = 3000
NUM_NODES = 5209
NUM_CATEGORY = 6

#number of local regions and local region size
region_num = 9
region_size = 50


# read usercategory file and get user * category matrix
# use usercategory information to get chunks information and neglinks information
def get_usercategory(data_set):
    in_file = open("../data/%s/usercategory.txt" % data_set)
    #in_file = open("../data/flickr/usercategory.txt")
    usercategory = []
    while True:
        line = in_file.readline()

        if not line:
            break

        items = line.strip().split(",")
        usercategory.append(items)
    in_file.close()
    return usercategory


# read edge file to get all edges
# use these edges to find local information region
def get_edges(data_set):
    in_file = open("../data/%s/edges.txt" % data_set)
    #in_file = open("../data/flickr/edges.txt")
    edges = []
    while True:
        line = in_file.readline()

        if not line:
            break

        #items = line.strip().split(" ") #TODO:flickr
        items = line.strip().split(",")
        edges.append((int(items[0]), int(items[1])))
    in_file.close()
    return edges


# get ranked nodes: order by edge number a node has
# use this order to pick start node, so node with higher degree tends to be picked earlier
def get_ranked_nodes(data_set): # get nodes ranked by edge num
    infile = open("../data/%s/edges.txt" % data_set)
    #infile = open("../data/flickr/edges.txt")
    node_dict = {}

    while True:
        line = infile.readline()

        if not line:
            break

        items = line.strip().split(",")
        #items = line.strip().split(" ") #TODO:flickr
        node1 = items[0]
        if node1 in node_dict:
            node_dict[node1] += 1
        else:
            node_dict[node1] = 1

    sort_nodes = sorted(node_dict.iteritems(), key=operator.itemgetter(1), reverse=True)
    nodes = [int(node[0]) for node in sort_nodes]
    infile.close()
    return nodes

# get similar nodes pair list by finding local information regions
# nodes in the same local information and has same category are put in the S list
def get_s_with_local_region(edges, ranked_nodes, usercategory, region_num, region_size):
    visited = [0] * NUM_NODES
    S = []

    pos = 0
    for i in range(region_num): # find region_num local regions

        # first: get a start node
        start_pos = pick_start_node(visited, ranked_nodes, pos)
        start = ranked_nodes[start_pos]

        # next: pick region_size nodes by BFS, which become a local region
        visited[start-1] = 1
        pick_nodes = pick_region_nodes(start, edges, visited, region_size)
        #print "find a local region:"
        #print pick_nodes

        # get S for this local region
        for i in range(region_size):
            for j in range(i+1, region_size):
                if not is_dissimilar_pair(pick_nodes[i]-1, pick_nodes[j]-1, usercategory):

                    #because the lables start from 1 in pick nodes,
                    #minus 1 to transfrom it to start from 0
                    S.append((pick_nodes[i]-1, pick_nodes[j]-1))

        pos = start_pos + 1

    return S



# pick nodes as start node successively in ranked_nodes
def pick_start_node(visited, ranked_nodes, pos):
    for i in range(pos, NUM_NODES):
        if visited[ranked_nodes[i]-1] == 0:
            return i
    raise NameError("can't find start node")


# after picking a start node, get a local information region using bfs
def pick_region_nodes(start, edges, visited, region_size):
    nodes = deque()
    nodes.append(start)
    pick_num = 1
    pick_nodes = [start]

    while pick_num < region_size:
        current = nodes.popleft()
        neighbor_nodes = [user2 for (user1, user2) in edges if\
                            user1 == current and\
                            visited[user2-1] == 0]

        left_num = region_size - pick_num
        if len(neighbor_nodes) > left_num:
            samples = random.sample(set(neighbor_nodes), left_num)
            for sample in samples:
                visited[sample-1] = 1
            pick_nodes.extend(samples)
            break
        else:
            random.shuffle(neighbor_nodes)
            for node in neighbor_nodes:
                visited[node-1] = 1
                pick_num += 1
                pick_nodes.append(node)
                nodes.append(node)

    return pick_nodes


# nodes pair that have same category is similar
def is_dissimilar_pair(user1, user2, usercategory):
    for i in range(NUM_CATEGORY):
        if usercategory[user1][i] == usercategory[user2][i] and\
           usercategory[user1][i] == '1':
            return False

    return True

# sample suitable nodes to get dissimilar nodes pair list
def get_d_with_sample(usercategory, region_num, region_size):
    nodes = random.sample(range(NUM_NODES), region_num * region_size)
    #print nodes
    D = []

    for i in range(len(nodes)):
        for j in range(i+1, len(nodes)):
            u = nodes[i]
            v = nodes[j]
            if is_dissimilar_pair(u, v, usercategory):
                D.append((u, v))

    return D


# replace a element in a list by another element
# used by substitude chunks id in generate positive constraints
def replace_list(li, before, after):

    for index, value in enumerate(li):
        if value == before:
            li[index] = after

# generate positive and negative constraints
def generate_constraints(S, D, data_set):

    chunks = [-1] * NUM_NODES
    cid = 0 #begin from zero
    #generate positive constraints
    for u, v in S:
        if chunks[u] == -1 and chunks[v] == -1: #both not alloc
            chunks[u] = chunks[v] = cid
            cid += 1
        elif chunks[u] == -1:
            chunks[u] = chunks[v]
        elif chunks[v] == -1:
            chunks[v] = chunks[u]
        else: #both has been allocated
            if chunks[u] != chunks[v]:
                min_id = min(chunks[u], chunks[v])
                max_id = max(chunks[u], chunks[v])
                replace_list(chunks, max_id, min_id)
                if max_id != cid - 1:
                    replace_list(chunks, cid - 1, max_id)
                    cid -= 1

    chunk_num = cid
    #get negative links
    neglinks = []
    for i in range(chunk_num):
        neglinks.append([0] * (chunk_num))

    for u, v in D:
        if chunks[u] != -1 and chunks[v] != -1 and\
           chunks[u] != chunks[v]:
            neglinks[chunks[u]][chunks[v]] += 1
            neglinks[chunks[v]][chunks[u]] += 1

    #output chunks
    out_file = open("../data/%s/chunks.txt" % data_set, 'w')
    for i in range(NUM_NODES):
        if chunks[i] == -1:
            out_file.write("%s\n" % chunks[i])
        #because DCA algorithm using effective chunks beginning from 1
        #add 1 to do the transfromation
        else:
            out_file.write("%s\n" % (chunks[i] + 1))
    out_file.close()

    #output neglinks
    out_file = open("../data/%s/neglinks.txt" % data_set, "w")
    for i in range(chunk_num):
        out_file.write("%s\n" %
                    " ".join([str(j) for j in neglinks[i]]))
    out_file.close()

def generate_constraint(region_num, region_size, data_set, num_nodes):
    global NUM_NODES
    NUM_NODES = num_nodes
    edges = get_edges(data_set)
    ranked_nodes = get_ranked_nodes(data_set) #order nodes by edges number
    usercategory = get_usercategory(data_set) #ground truth

    S = get_s_with_local_region(edges, ranked_nodes, usercategory, region_num, region_size)
    D = get_d_with_sample(usercategory, region_num, region_size)

    generate_constraints(S, D, data_set)

if __name__ == "__main__":
    print "rember to change file name and num macros"

    generate_constraint(10, 50, "blogcatalog-b", 5209)
