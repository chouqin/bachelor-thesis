# -*- coding=utf-8 -*-

#compute purity for k-means cluster algorithm
#two input files
#usercategory.txt:
#   this file specify user category relationship,
#   each line in this file identify one user,
#   if user belongs to some category, then the corresponding column is set to 1
#result.txt:
#   this file specify the cluster the user belongs using k-means
#   each line tell the cluster number user belongs to


NUM_CATEGORY = 6 # num of user category in ground truth
NUM_NODES = 5118
NUM_CLUSTERS = 6 # num of cluster used by k-means, this num may be different with NUM_CATEGORY


# read usercategory file and get user * category matrix
def get_user_category():
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


# read result file and get a list of clusters represented by a list of user id
def get_clusters():
    #in_file = open("../data/flickr/result/sresult003.txt")
    in_file = open("../data/blogcatalog/result/sresult006.txt")
    clusters = []
    for i in range(NUM_CLUSTERS):
        clusters.append([])

    for i in range(NUM_NODES):
        line = in_file.readline()

        cluster = int(line.strip())
        clusters[cluster-1].append(i)

    in_file.close()
    return clusters


#get the max number of users belongs to a specific category in a cluster
def get_max_pi(cluster, usercategory):
    category_count = [0] * NUM_CATEGORY
    for node in cluster:
        for category in range(NUM_CATEGORY):
            if usercategory[node][category] == '1':
                category_count[category] += 1
    return max(category_count)


# compute the purity of k-means clustering
def get_purity(clusters, usercategory):
    purity_sum = 0

    for cluster in clusters:
        purity_sum += get_max_pi(cluster, usercategory)

    return float(purity_sum) / NUM_NODES


if __name__ == '__main__':
    print "rember to change file name and num macros"

    usercategory = get_user_category()
    clusters = get_clusters()

    print get_purity(clusters, usercategory)
