# -*- coding=utf-8 -*-

def read_dict():
    dict_file = open("dict1.txt")

    di = {}

    while True:
        word = dict_file.readline().strip()

        if not word:
            break

        if word not in di:
            di[word] = 0

    dict_file.close()
    return di

def output_dict(di):
    dict_file = open("dict1.txt", "w")

    for key in di.keys():
        dict_file.write("%s\n" % (key))

    dict_file.close()

def count_keywords(di, file_name):

    input_file = open(file_name)

    content = input_file.read().strip()
    input_file.close()
    words = content.split(" ")

    for word in words:
        if word in di:
            di[word] = 1

    return di

if __name__ == "__main__":
    di = read_dict()
    #output_dict(di)
    count_keywords(di, "/tmp/weibo/1660361312/weibos.txt_result.txt")

    for key, value in di.iteritems():
        print key, value

