# -*- coding=utf-8 -*-

#change data set:
#change file directory
#different split symbol for edges.txt

import random
import math
from collections import deque
import operator

#NUM_FEATURE = 3000
NUM_NODES = 5118
NUM_CATEGORY = 6

#number of local regions and local region size
LOCAL_MAX = 10
NODE_MAX = 40

def get_features():
    in_file = open("../data/blogcatalog/features.txt")
    #in_file = open("../data/flickr/features.txt")
    A = []
    while True:
        line = in_file.readline()

        if not line:
            break

        items = line.strip().split(",")
        A.append(items)
    in_file.close()
    return A

def get_usercategory():
    in_file = open("../data/blogcatalog/usercategory.txt")
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


def get_edges():
    in_file = open("../data/blogcatalog/edges.txt")
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

def get_ranked_nodes(): # get nodes ranked by edge num
    infile = open("../data/blogcatalog/edges.txt")
    #infile = open("../data/flickr/edges.txt")
    node_dict = {}

    while True:
        line = infile.readline()

        if not line:
            break

        #node_num = int(line.strip().split("\t")[0])
        items = line.strip().split(",")
        #items = line.strip().split(" ") #TODO:flickr
        node1 = items[0]
        if node1 in node_dict:
            node_dict[node1] += 1
        else:
            node_dict[node1] = 1

        #node2 = items[1]
        ##undirect edges, every edge count twice
        #if node2 in node_dict:
            #node_dict[node2] += 1
        #else:
            #node_dict[node2] = 1

    sort_nodes = sorted(node_dict.iteritems(), key=operator.itemgetter(1), reverse=True)
    nodes = [int(node[0]) for node in sort_nodes]
    infile.close()
    return nodes

def get_local_region(edges, ranked_nodes):
    visited = [0] * NUM_NODES
    new_edges = []
    S = {}
    ranked_nodes = get_ranked_nodes()

    pos = 0
    for i in range(LOCAL_MAX): # find LOCAL_MAX local regions

        # first: get a start node
        start_pos = pick_start_node(visited, ranked_nodes, pos)
        start = ranked_nodes[start_pos]

        # next: pick NODE_MAX nodes by BFS, which become a local region
        visited[start-1] = 1
        pick_nodes = pick_region_nodes(start, edges, visited)
        print "find a local region:"
        print pick_nodes

        # get edges of local region
        user_edges = [(user1, user2) for (user1, user2) in edges if\
                      user1 in pick_nodes and user2 in pick_nodes
                      ]
        print user_edges

        # get S for this local region
        for i in range(NODE_MAX):
            for j in range(i+1, NODE_MAX):
                s = get_similarity(pick_nodes[i], pick_nodes[j], user_edges)
                S[(pick_nodes[i], pick_nodes[j])] = s

        new_edges.extend(user_edges)
        pos = start_pos + 1

    return new_edges, S

def pick_start_node(visited, ranked_nodes, pos):
    for i in range(pos, NUM_NODES):
        if visited[ranked_nodes[i]-1] == 0:
            return i
    raise NameError("can't find start node")

def pick_region_nodes(start, edges, visited):
    nodes = deque()
    nodes.append(start)
    pick_num = 1
    pick_nodes = [start]

    while pick_num < NODE_MAX:
        current = nodes.popleft()
        neighbor_nodes = [user2 for (user1, user2) in edges if\
                            user1 == current and\
                            visited[user2-1] == 0]

        left_num = NODE_MAX - pick_num
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


def is_dissimilar_pair(user1, user2, usercategory):
    for i in range(NUM_CATEGORY):
        if usercategory[user1][i] == usercategory[user2][i] and\
           usercategory[user1][i] == '1':
            return False

    return True

def get_similarity(user1, user2, user_edges):
    user1_neighbors = []
    user2_neighbors = []

    for user, user_t in user_edges:
        if (user == user1) and user_t not in user1_neighbors:
            user1_neighbors.append(user_t)

        if (user_t == user1) and user not in user1_neighbors:
            user1_neighbors.append(user)

        if (user == user2) and user_t not in user2_neighbors:
            user2_neighbors.append(user_t)

        if (user_t == user2) and user not in user2_neighbors:
            user2_neighbors.append(user)

    num1 = len(user1_neighbors)
    num2 = len(user2_neighbors)
    num3 = len([user for user in user1_neighbors if user in user2_neighbors])

    return num3 / math.sqrt(num1 * num2)

def sample_nodes(edges, ranked_nodes):
    visited = [0] * NUM_NODES

    sampled_nodes = []
    pos = 0
    for i in range(LOCAL_MAX): # find LOCAL_MAX local regions

        # first: get a start node
        start_pos = pick_start_node(visited, ranked_nodes, pos)
        start = ranked_nodes[start_pos]

        # next: pick NODE_MAX nodes by BFS, which become a local region
        visited[start-1] = 1
        pick_nodes = pick_region_nodes(start, edges, visited)
        print "find a local region to compute d:"
        print pick_nodes

        sampled_nodes.extend(pick_nodes)

        pos = start_pos + 1

    return sampled_nodes


def compute_d(nodes, usercategory):
    print nodes
    D = []
    for i in range(NUM_NODES):
        row = [0] * NUM_NODES
        D.append(row)

    for i in range(len(nodes)):
        for j in range(i+1, len(nodes)):
            u = nodes[i]
            v = nodes[j]
            if is_dissimilar_pair(u, v, usercategory):
                D[u][v] = D[v][u] = 1

    out_file = open("../data/blogcatalog/d.txt", "w")
    #out_file = open("../data/flickr/d.txt", "w")
    for i in range(NUM_NODES):
        out_file.write("%s\n" %
                       " ".join([str(j) for j in D[i]]))
    out_file.close()

def compute_s(S):
    SMatrix = []
    for i in range(NUM_NODES):
        row = [0] * NUM_NODES
        SMatrix.append(row)

    for (user1, user2), s in S.iteritems():
        SMatrix[user1-1][user2-1] = s
        SMatrix[user2-1][user1-1] = s

    out_file = open("../data/blogcatalog/s.txt", "w")
    #out_file = open("../data/flickr/s.txt", "w")
    for i in range(NUM_NODES):
        out_file.write("%s\n" %
                       " ".join([str(j) for j in SMatrix[i]]))
    out_file.close()

if __name__ == "__main__":
    print "rember to change file name and num macros"

    #A = get_features()
    edges = get_edges()
    ranked_nodes = get_ranked_nodes() #order nodes by edges number
    usercategory = get_usercategory() #ground truth

    new_edges, S = get_local_region(edges, ranked_nodes)
    compute_s(S)

    #sampled_nodes = sample_nodes(edges, ranked_nodes)
    sampled_nodes = random.sample(range(NUM_NODES), LOCAL_MAX * NODE_MAX)
    compute_d(sampled_nodes, usercategory)

    #output S
    s_file = open("../data/blogcatalog/stuple.txt", "w")
    #s_file = open("../data/flickr/stuple.txt", "w")
    for (user1, user2), s in S.iteritems():
        s_file.write("%s %s %s\n" % (user1, user2, s))
    s_file.close()

    #output D
    #d_file = open("d.txt", "w")
    #for (user1, user2) in D:
        #d_file.write("%s %s\n" % (user1, user2))
    #d_file.close()

    #output new_edges
    edge_file = open("../data/blogcatalog/new_edges.txt", "w")
    #edge_file = open("../data/flickr/new_edges.txt", "w")
    for edge in new_edges:
        edge_file.write("%d %d\n" % edge)
    edge_file.close()
    #for key, value in di.iteritems():
        #print key, value
