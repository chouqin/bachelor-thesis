# -*- coding=utf-8 -*-

#implementation of dshrink cluster algorithm described in the paper
# Community Detection in Imcomplete Networks
# input: distance.txt
# distance matrix represent each node pair's distance

#nodes type constant
TYPE_NORMAL = 1
TYPE_COMBINE = 2 # this type of nodes are 'super nodes' that are combined by other nodes
TYPE_NONE = 3
# after node has been combined into super nodes, mark this node as type none
# to note that this node does not exist any more

MAX_DISTANCE = 100 #need to change accordingly

epsilon = 3

STEP_SIZE = 40

NUM_NODES = 5209

#import numpy as np #use numpy to compute median distance
from collections import deque
import random
import operator

from compute_purity import get_max_pi

# class Node definition
class Node(object):

    def __init__(self, ntype=TYPE_NORMAL, children_list=None,
                 nearest_neighbor=MAX_DISTANCE, anearest_neighbors=[]):
        self.ntype = TYPE_NORMAL
        self.children_list = children_list
        self.nearest_neighbor = nearest_neighbor #just need a value, the smallest distance between this node and other nodes
        self.anearest_neighbors = anearest_neighbors


    #dic is total distance between nodes in this cluster and all the other nodes
    #sit[i] is total distance between node i and any other nodes
    def get_dic(self, sit):
        dic = 0
        for i in self.children_list:
            dic += sit[i]
        return dic


    def __str__(self):
        return "%s %s %s" % (self.children_list, self.nearest_neighbor, self.anearest_neighbors)


# read input file to get the distance matrix
def compute_dm(data_set):
    input_file = open("../data/%s/dca_distance.txt" % data_set)
    #input_file = open("../data/flickr/distance.txt")
    dm = []

    while True:
        line = input_file.readline()

        if not line:
            break

        values = [float(i) for i in line.strip().split(",")]
        dm.append(values)

    input_file.close()
    return dm


# initial nodes
# at the beginning, each node is normal node which only contains one node
def initial_nodes(dm):
    nodes = []
    for i in range(NUM_NODES):
        node = Node()
        node.children_list = [i]
        for j in range(NUM_NODES):
            if i == j:
                continue
            if dm[i][j] < node.nearest_neighbor:
                node.nearest_neighbor = dm[i][j]
        nodes.append(node)

    return nodes


# compute dt and sit for later use
# dm is the total distance between any two nodes
# sit[i] is the total distance between node i and any nodes
def compute_dt_sit(dm):
    node_num = NUM_NODES
    dt = 0
    sit = [0] * node_num
    for i in range(node_num):
        for j in range(node_num):
            dt += dm[i][j]
            sit[i] += dm[i][j]

    return dt, sit


# compute the total distance between any node in cluster s and any node in cluster t
def compute_du(dm, s, t):
    du = 0
    for i in s.children_list:
        for j in t.children_list:
            du += dm[i][j]

    return du


# compute delta qd: the gains of distance-based modularity
# for combine a list of cluster into a cluster
def compute_delta_qd(dm, dt, node_list, nodes, sit):
    dust = 0
    dsdt = 0
    for s in node_list:
        for t in node_list:
            if s != t:
                dust += dt * compute_du(dm, nodes[s], nodes[t])
                dsdt += nodes[s].get_dic(sit) * nodes[t].get_dic(sit)
    return dust - dsdt

# get a list of clusters to be combined
# each cluster is represented by a list of node labels
def get_community_list(nodes, dm):
    visited = [0] * NUM_NODES
    community_list = []

    # get a list of nodes label which contain nodes not none
    real_nodes = get_realnodes(nodes)
    random.shuffle(real_nodes)

    pos = 0
    while pos < len(real_nodes):

        # first pick a start node to start bfs
        # pick nodes from real_nodes which has not been visited, starting from pos
        start_pos = pick_start_node(visited, real_nodes, pos)
        if start_pos is None:
            break
        start = real_nodes[start_pos]

        visited[start] = 1
        node_list = bfs(nodes, start, visited, dm)
        community_list.append(node_list)

        # all the nodes before pos has been visited
        pos = start_pos + 1

    return community_list


def get_realnodes(nodes):
    real_nodes = []
    for i in range(NUM_NODES):
        if nodes[i].ntype != TYPE_NONE:
            real_nodes.append(i)

    return real_nodes



# pick a start node successively in real_nodes
def pick_start_node(visited, real_nodes, pos):
    for i in range(pos, len(real_nodes)):
        if visited[real_nodes[i]] == 0:
            return i
    return None


# using bfs to get a list of clusters after picking a start node
def bfs(nodes, start, visited, dm):
    node_list = deque()
    node_list.append(start)
    pick_nodes = [start]
    max_fr = 0
    min_fr = MAX_DISTANCE

    #while len(node_list) > 0 and\
          #len(pick_nodes) < STEP_SIZE:
    while len(node_list) > 0:
        current = node_list.popleft()

        for node in nodes[current].anearest_neighbors:
            #if len(pick_nodes) >= STEP_SIZE:
                #break
            if nodes[node].ntype == TYPE_NONE:
                print "none type node %d is in %d's anearest_neighbors" % (node, current)
                print "start is", start
                print "node queue is", node_list
                print "pick_nodes is", pick_nodes
                exit(0)
            if visited[node] == 0:
                can_pick, max_distance, min_distance = try_pick_node(max_fr, min_fr, dm, pick_nodes, node)
                if can_pick:
                    visited[node] = 1
                    max_fr, min_fr = max_distance, min_distance
                    node_list.append(node)

                    # put it here to get try_pick_node right
                    pick_nodes.append(node)

    return pick_nodes


# if adding a node cause max_fr - min_fr > epsilon, stop adding
def try_pick_node(max_fr, min_fr, dm, pick_nodes, v):
    max_distance = 0
    min_distance = MAX_DISTANCE
    for i in pick_nodes:
        if dm[i][v] > max_distance:
            max_distance = dm[i][v]
        elif dm[i][v] < min_distance:
            min_distance = dm[i][v]

    if max_distance > max_fr:
        max_fr = max_distance
    if min_distance < min_fr:
        min_fr = min_distance

    can_pick = epsilon >= max_fr - min_fr

    return can_pick, max_fr, min_fr


# update max_fr, min_fr after adding a node to the node list
def update_max_min_fr(max_fr, min_fr, dm, u, v):
    if dm[u][v] > max_fr:
        return dm[u][v], min_fr
    elif dm[u][v] < min_fr:
        return max_fr, dm[u][v]
    return max_fr, min_fr


# after combine a list of nodes into a super node
# compute the distance between this super node and all other nodes
def recompute_distance(nodes, dm, community, label):
    nodes_num = len(community)
    for i in range(NUM_NODES):
        if i not in community and nodes[i].ntype != TYPE_NONE:
            dm[i][label] = dm[label][i] = sum([dm[i][j] for j in community]) / nodes_num #use average distance
            #dm[i][label] = dm[label][i] = min([dm[i][j] for j in community])

# after a iteration of combines, recompute nearest_neighbors for all nodes of type not none
def compute_nearest_neighbors(nodes, dm):
    for i in range(NUM_NODES):
        if nodes[i].ntype != TYPE_NONE:
            nodes[i].nearest_neighbor = MAX_DISTANCE
            for j in range(NUM_NODES):
                if nodes[j].ntype != TYPE_NONE and\
                   i != j and\
                   dm[i][j] < nodes[i].nearest_neighbor:
                    nodes[i].nearest_neighbor = dm[i][j]


# after a iteration of combines, recompute anearest_neighbors for all nodes of type not none
def compute_anearest_neighbors(nodes, dm):
    #sort anearest_neighbors by distance with current node
    for i in range(NUM_NODES):
        if nodes[i].ntype != TYPE_NONE:
            nodes[i].anearest_neighbors = []
            distance_list = dm[i]
            sorted_list = sorted(enumerate(distance_list), key=operator.itemgetter(1))
            for index, _ in sorted_list:
                if nodes[index].ntype != TYPE_NONE and\
                   is_anearest_neighbor(i, index, dm, nodes):
                    nodes[i].anearest_neighbors.append(index)


# two nodes is anearest_neighbors is described in the paper
def is_anearest_neighbor(s, t, dm, nodes):
    return (dm[s][t] == nodes[s].nearest_neighbor and
            (dm[s][t] - nodes[t].nearest_neighbor) <= epsilon) or\
            (dm[s][t] == nodes[t].nearest_neighbor and
             (dm[s][t] - nodes[s].nearest_neighbor) <= epsilon)


# the process to combine a list of nodes into a super node
def combine_local_community(nodes, dm, community):

    #first: given the smallest label to the community
    label = min(community)
    new_node = Node(ntype=TYPE_COMBINE)

    #next: get the super nodes children_list, which is nodes label this node contains
    new_node.children_list = []
    for i in community: #ensure nodes[i] != TYPE_NONE
        new_node.children_list.extend(nodes[i].children_list)

    nodes[label] = new_node

    #next: recompute the distance between these nodes
    recompute_distance(nodes, dm, community, label)

    #finally: mark combined nodes as none type, except the label node
    for i in community:
        if i != label:
            nodes[i].ntype = TYPE_NONE


# get the minimum and maxmum distance in the distance matrix
def get_minimum_distance(distance):
    minimum = MAX_DISTANCE
    maxmum = 0
    for i in range(NUM_NODES):
        for j in range(i+1, NUM_NODES):
            if distance[i][j] != 0:
                if distance[i][j] < minimum:
                    minimum = distance[i][j]
                elif distance[i][j] > maxmum:
                    maxmum = distance[i][j]

    return minimum, maxmum

def get_purity(data_set, usercategory, num_nodes):
    global NUM_NODES
    NUM_NODES = num_nodes
    nodes = dshrink(data_set)
    purity_sum = 0
    for node in nodes:
        if node.ntype != TYPE_NONE:
            purity_sum += get_max_pi(node.children_list, usercategory)

    return float(purity_sum) / NUM_NODES

# the main procedure of the dshrink algorithm
def dshrink(data_set):
    #first get dm, dm_original
    #dm_original is just of a copy a dm, but it is needed to compute delta qd
    #because dm may be updated during each iteration
    dm_original = compute_dm(data_set)
    dm = []
    for i in dm_original:
        new_list = [j for j in i]
        dm.append(new_list)

    #use this mdistance and maxdistance to determine epsilon
    #mdistance, maxdistance = get_minimum_distance(dm)
    ##median = np.median(np.array(dm))
    #print mdistance, maxdistance
    #exit(0)

    #next initial list of nodes, compute their nearest_neighbor and anearest_neighbors
    nodes = initial_nodes(dm)
    compute_anearest_neighbors(nodes, dm)

    #for node in nodes:
        #if node.ntype != TYPE_NONE:
            #print node

    #compute dt and sit for later use
    dt, sit = compute_dt_sit(dm)

    while True:
        # in each loop, find a list of local communities,
        # combine each community as a single node,
        # stop when delta_qd >= 0
        community_list = get_community_list(nodes, dm)

        decrease = False

        for community in community_list:
            if len(community) == 1:
                continue
            delta_qd = compute_delta_qd(dm_original, dt, community, nodes, sit)
            if delta_qd < 0:
                #print "here combine community", community
                decrease = True
                combine_local_community(nodes, dm, community)
            #else:
                #print "combine failed because delta_qd < 0", community

        #when there is no combine, stop
        if not decrease:
            break
        else:
            #don't need to compute anearest_neighbors in each combine
            #compute it after all combines
            compute_nearest_neighbors(nodes, dm)
            compute_anearest_neighbors(nodes, dm)

        for node in nodes:
            if node.ntype != TYPE_NONE:
                #print node
                #assure that each cluster has no duplicate node label
                if len(set(node.children_list)) != len(node.children_list):
                    print "has duplicate entry!!!!", node
                    exit(0)


    #print "finally"
    #out_file = open("../data/blogcatalog-b/result/region_num/10_handled.txt", "w")
    #for node in nodes:
        #if node.ntype != TYPE_NONE:
            #print node
            #out_file.write("%s\n" %
                           #", ".join([str(i) for i in node.children_list]))
    #out_file.close()

    return nodes

if __name__ == "__main__":
    print "rember to change file name and num macros"
    print "also need to change max distance accordingly"

    #dshrink()
