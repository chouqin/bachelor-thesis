# -*- coding=utf-8 -*-

#compute purity for dshrink cluster algorithm
#two input file
#usercategory.txt:
#   this file specify user category relationship,
#   each line in this file identify one user,
#   if user belongs to some category, then the corresponding column is set to 1
#result.txt:
#   this file specify the cluster the user belongs using k-means
#   each line represent a cluster, which contains a list of user ids belonging to this cluster


NUM_CATEGORY = 6
NUM_NODES = 5118


# read usercategory file and get user * category matrix
def get_user_category(data_set):
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


# read result file and get a list of clusters represented by a list of user id
def get_clusters(file_name):
    #in_file = open("../data/flickr/result/result001_handled.txt")
    in_file = open("../data/blogcatalog-b/result/region_num/%s" % file_name)
    clusters = []
    while True:
        line = in_file.readline()

        if not line:
            break

        items = line.strip().split(", ")
        cluster = [int(i) for i in items]
        clusters.append(cluster)
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


# compute the purity of dshrink clustering
def get_purity(file_name, usercategory):
    clusters = get_clusters(file_name)
    purity_sum = 0

    for cluster in clusters:
        purity_sum += get_max_pi(cluster, usercategory)

    return float(purity_sum) / NUM_NODES


if __name__ == '__main__':
    print "rember to change file name and num macros"

    usercategory = get_user_category()

    #file_names = [
        #(20, '20_handled.txt'),
        #(25, '25_handled.txt'),
        #(30, '30_handled.txt'),
        #(35, '35_handled.txt'),
        #(40, '40_handled.txt'),
        #(45, '45_handled.txt'),
        #(50, '50_handled.txt'),
        #(55, '55_handled.txt'),
        #(60, '60_handled.txt'),
    #]

    file_names = [
        #(4, '4_handled.txt'),
        #(5, '5_handled.txt'),
        #(6, '6_handled.txt'),
        #(7, '7_handled.txt'),
        #(8, '8_handled.txt'),
        #(9, '9_handled.txt'),
        (10, '10_handled.txt'),
        #(11, '11_handled.txt'),
        #(12, '12_handled.txt'),
    ]

    result = []
    for node_max, name in file_names:
        result.append((node_max, get_purity(name, usercategory)))

    #output result
    #out_file = open("../data/blogcatalog/result/node_max/summary.txt", "w")
    out_file = open("../data/blogcatalog-b/result/region_num/summary_tmp.txt", "w")
    for node_max, purity in result:
        print node_max, purity
        out_file.write("%d %f\n" % (node_max, purity))
    out_file.close()

    #print get_purity(clusters, usercategory)
