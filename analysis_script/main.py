#coding:utf-8

import argparse
import sqlite3
import pickle
import random
import nltk
import os
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans


def get_connecter(dbpath):
    con = sqlite3.connect(dbpath)
    con.text_factory = str
    return con


def get_table(con,sql):
    data = {}
    cursor = con.cursor()

    for row in cursor.execute(sql):
        data.update({row[0]:row[1]})

    return data


def insert(con,link,body,sql):
    data = [(link,body)]
    con.executemany(sql,data)
    con.commit()


def fileread(filepath):
    with open(filepath,"r") as f:
        fr = f.read()
    return fr


def filewrite(filepath,text):
    with open(filepath,"w") as f:
        f.write(text)


def objectwrite(filepath,obj):
    with open(filepath,"wb") as f:
        pickle.dump(obj,f)


def objectread(filepath):
    with open(filepath,"rb") as f:
        obj = pickle.load(f)
    return obj


def file2sql(filepath,con):
    hsfiles = os.listdir(filepath)
    sql_insert_link = "insert into link(link,body) values (?,?)"

    for filename in hsfiles:
        full_filepath = filepath + "/" + filename
        text = fileread(full_filepath)
        insert(con,filename,text,sql_insert_link)


def text2nn(con):
    sql_get_link = "select link,body from link"
    sql_insert_noun = "insert into noun(link,body) values (?,?)"

    data = get_table(con,sql_get_link)
    for k,v in data.items():
        words = nltk.word_tokenize(v)
        words_tag = nltk.pos_tag(words)
        noun_lst = []

        for word_tag in words_tag:
            kind_tag = word_tag[1]
            if kind_tag == "NNP" or kind_tag == "NN":
                noun_lst.append(word_tag[0])

        insert(con,k,','.join(noun_lst),sql_insert_noun)


def select_random_nn(data,ratio):
    all_noun_lst = set([])
    each_noun_dict = {}
    sample_noun_dict = {}
    docs = []

    for k,v in data.items():
        noun_lst = v.split(",")

        for noun in noun_lst:
            if len(noun) < 2:
                noun_lst.remove(noun)

        each_noun_dict.update({k:noun_lst})
        all_noun_lst = all_noun_lst | set(noun_lst)

    choice_len = int(int(len(all_noun_lst)) * ratio)
    sample_noun_lst = random.sample(list(all_noun_lst),choice_len)

    for i,(k,v) in enumerate(each_noun_dict.items()):
        print("[sampling {} {}/{}]".format(k,str(i),len(each_noun_dict)))
        noun_lst = []

        for noun in v:
            if noun in sample_noun_lst:
                noun_lst.append(noun)

        if int(len(noun_lst)) > 3:
            sample_noun_dict.update({k:' '.join(noun_lst)})

    return sample_noun_dict


def analysis_tfidf(con):
    sql_get_noun = "select link,body from noun"

    data = get_table(con,sql_get_noun)
    sample_noun_dict = select_random_nn(data,1.0)

    vec = TfidfVectorizer(use_idf=True)
    term_doc = vec.fit_transform(sample_noun_dict.values())

    term_doc_path = "{}/{}".format(picklepath,"term_doc")
    sample_noun_dict_path = "{}/{}".format(picklepath,"sample_noun_dict")

    objectwrite(term_doc_path,term_doc)
    objectwrite(sample_noun_dict_path,sample_noun_dict)


def main(filepath,dbpath,picklepath):
    con = get_connecter(dbpath)
    lines = ""

    # file2sql(filepath,con)
    # text2nn(con)
    # analysis_tfidf(con)

    term_doc_path = "{}/{}".format(picklepath,"term_doc")
    sample_noun_dict_path = "{}/{}".format(picklepath,"sample_noun_dict")

    term_doc = objectread(term_doc_path)
    sample_noun_dict = objectread(sample_noun_dict_path)
    evaluation_dict = {}
    ranking_dict = {}

    print(term_doc.shape)
    input()

    claster_num = int(int(len(sample_noun_dict.keys())) * 0.1)
    clusters = KMeans(n_clusters=claster_num,random_state=0).fit_predict(term_doc)

    for i,(address,doc,cls) in enumerate(zip(sample_noun_dict.keys(),sample_noun_dict.values(),clusters)):
        line = "{},{},{}".format(address,cls,doc)
        lines += line + "\n"
        evaluation_dict.update({address:[cls,term_doc[i,:]]})

    filewrite("./result.csv",lines)

    for n in range(100):
        # select random query
        select_address_name = random.choice(list(evaluation_dict.keys()))
        select_address_cls = evaluation_dict[select_address_name][0]
        select_address_vector = evaluation_dict[select_address_name][1]

        print("select address : {}".format(select_address_name))
        print("select_address cluster : {}".format(str(select_address_cls)))

        # calculate cos similarity
        for k,v in evaluation_dict.items():
            if k != select_address_name:
                target_address_name = k
                target_address_cls = evaluation_dict[target_address_name][0]
                target_address_vector = evaluation_dict[target_address_name][1]

                cos = cosine_similarity(select_address_vector,target_address_vector)
                ranking_dict.update({target_address_name:cos})

        # sort ranking
        hit_count  = 0

        for i,(k,v) in enumerate(sorted(ranking_dict.items(),key=lambda x:x[1],reverse=True)):
            if i < 10:
                print("address : {}".format(k))
                print("cos similarity : {}".format(str(v[0][0])))
                print("cluster : {}".format(str(evaluation_dict[k][0])))

                if evaluation_dict[k][0] == select_address_cls:
                    hit_count += 1

        # print("{},{}".format(str(select_address_cls),str(float(hit_count*1.0/10))))

    con.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--filepath",help="set input file path")
    parser.add_argument("--dbpath",help="set input db path")
    parser.add_argument("--picklepath",help="set output/input pickle path")

    args = parser.parse_args()
    filepath = args.filepath
    dbpath = args.dbpath
    picklepath = args.picklepath

    main(filepath,dbpath,picklepath)
