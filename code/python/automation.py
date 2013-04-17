# -*- coding=utf-8 -*-

"""
this is an automation script to run all dataset
in different condition.
At the same time, it can average the result to let it be more resonable
"""

import os

from generate_constraints import generate_constraint
from dshrink import get_purity
from compute_purity import get_user_category

REPEAT_TIME = 5

def automate():
    # for dataset blogcatalog
    data_set = "blogcatalog"
    num_nodes = 5118
    run_dataset(data_set, num_nodes)

    # for dataset blogcatalog-b
    data_set = "blogcatalog-b"
    num_nodes = 5209
    run_dataset(data_set, num_nodes)

def run_dataset(data_set, num_nodes):
    usercategory = get_user_category(data_set)

    pre_command = r"""matlab -nodisplay -nosplash -nodesktop -wait -r "run('"""
    post_command = r"""');exit;" """
    script_name = "c:\Users\liqi\Desktop\code_Metric_online\data\%s\dca_distance.m" % data_set
    command = pre_command + script_name + post_command

    # different region_num
    file_name = "../data/%s/result/region_num/summary_auto.txt" % data_set
    region_size = 50
    result = []
    for region_num in range(4, 13): #4~12
        average_purity = run_case(data_set, num_nodes,
                region_size, region_num, usercategory, command)
        result.append((region_num, average_purity))

    output_purity(file_name, result)

    #different region_size
    file_name = "../data/%s/result/node_max/summary_auto.txt" % data_set
    region_num = 10
    result = []
    for region_size in range(20, 65, 5): #20~60
        average_purity = run_case(data_set, num_nodes,
                region_size, region_num, usercategory, command)
        result.append((region_size, average_purity))

    output_purity(file_name, result)


def run_case(data_set, num_nodes, region_size, region_num, usercategory, command):

    purity_total = 0
    for i in range(REPEAT_TIME):
        generate_constraint(region_num, region_size, data_set, num_nodes)

        os.system(command)

        purity = get_purity(data_set, usercategory, num_nodes)
        purity_total += purity
        print region_size, region_num, i, purity

    average_purity = purity_total / REPEAT_TIME
    print region_size, region_num, average_purity
    return average_purity


def output_purity(file_name, result):
    out_file = open(file_name, "w")
    for node_max, purity in result:
        print node_max, purity
        out_file.write("%d %f\n" % (node_max, purity))
    out_file.close()


if __name__ == "__main__":
    automate()
