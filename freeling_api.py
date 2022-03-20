import string

from xml.dom import minidom
import lxml.etree as ET
import pandas as pd
import lxml.etree
import os
from collections import Counter
import time

def time_now():
    return time.strftime("%Y-%m-%d %H:%M:%S")


LANGUAGE="it"
FILE_TYPE = f"{LANGUAGE}.cfg"
BASE_NAME = "Gonza_Dataset"
ID_COLUMN = "ID Particpant"
TEXT_COLUMN = "text"


file_text = """
FC Barcelona president Joan Laporta has
warned Chelsea off star striker Leonel Messi.
Aware of Chelsea owner Roman Abramovich’s
interest in the young Argentine, Laporta said last
night: ”I will answer as always, Messi is not for
sale and we do not want to let him go
"""

list_of_text = [file_text,file_text]

with open(FILE_TYPE, 'r') as file:
    freeling_config = file.read() 



def restart_freeling():
    os.system("docker kill freeling_container")
    os.system("docker restart freeling_container")

def change_output_from_to(from_,to_,config):
    config = config.replace(f"OutputFormat={from_}",f"OutputFormat={to_}")
    with open(FILE_TYPE, 'w') as file:
        file.write(config) 


def write_to_input(text):
    with open('./freeling_files/input_file', 'w') as file:
        file.write(text) 

def remove_first_and_last_line():
    os.system('''  sed -i '$ d' ./freeling_files/output_file ; sed -i '1d' ./freeling_files/output_file ''')

def call_freeling():
    os.system('''
    docker exec -u 0  freeling_container  bash -c "analyzer_client localhost:50005 /root/freeling_files/input_file > /root/freeling_files/output_file"
    ''')

def get_tree():
    with open('./freeling_files/output_file', 'r') as xml_file:
        xml_tree = lxml.etree.parse(xml_file) 
    return xml_tree

def calc_noun_verb_metric(xml_tree):
    pos_list = xml_tree.xpath("//token//@pos")  

    content_list = ["noun","verb","adjective","adverb"]

    pos_counter = Counter(pos_list)
    content_counter = { x: count for x, count in pos_counter.items() if x in content_list }


    all_words_sum = sum(pos_counter.values())
    only_content_words_sum = sum(content_counter.values())


    verbs_vs_all = content_counter["verb"] /  all_words_sum
    verbs_vs_content = content_counter["verb"] / only_content_words_sum

    noun_vs_all = content_counter["noun"] /  all_words_sum
    noun_vs_content =  content_counter["noun"] / only_content_words_sum

    return verbs_vs_all,verbs_vs_content,noun_vs_all,noun_vs_content

def get_form_xml(xml_tree):
    lemma_list = xml_tree.xpath("//token/@form")
    return lemma_list

def get_lemma_xml(xml_tree):
    lemma_list = xml_tree.xpath("//token/@lemma")
    return lemma_list


def get_morph_naf(xml_tree):
    list_of_morph = xml_tree.xpath("//term/@morphofeat")
    list_of_separated_morph = []
    for morph_ in list_of_morph:
        morph_dict = dict()
        for morph_values in morph_.split("|"):
            key = morph_values.split("=")[0]
            value = morph_values.split("=")[1]
            morph_dict[key] = value
        list_of_separated_morph.append(morph_dict)
    return list_of_separated_morph

def morph_pipeline():
    call_freeling()
    remove_first_and_last_line()
    xml_tree = get_tree()
    morph = get_morph_naf(xml_tree)
    df = pd.DataFrame(morph)
    return df


def formlemma_pipeline():
    call_freeling()
    #remove_first_and_last_line()
    xml_tree = get_tree()
    form = get_form_xml(xml_tree)
    lemma = get_lemma_xml(xml_tree)
    return form,lemma

list_of_df= []

change_output_from_to('xml','naf',freeling_config)
restart_freeling()
time.sleep(18)




data_df = pd.read_csv(f"{BASE_NAME}.csv",sep=";")
data_df=data_df.fillna("")
for index,row in data_df.iterrows():
    if(row[TEXT_COLUMN]==""):
        continue
    no_punct_string =  row[TEXT_COLUMN].translate(str.maketrans('', '', string.punctuation))
    write_to_input(no_punct_string)
    df = morph_pipeline()
#    id_ = row["ID"]+ "_" + row["cond"]
    id_ = row[ID_COLUMN]
    df["id"] = id_
    list_of_df.append(df)
    print(f"{time_now()}: finished row {index} with id {id_}")
    #df["lemma"] = lemma
    #df["form"]  = form


change_output_from_to('naf','xml',freeling_config)
restart_freeling()  
time.sleep(18)

list_of_lemma=[]
list_of_form=[]

for index,row in data_df.iterrows():
    if(row[TEXT_COLUMN]==""):
        continue

    no_punct_string =  row[TEXT_COLUMN].translate(str.maketrans('', '', string.punctuation))
    write_to_input(no_punct_string)
    forms,lemmas = formlemma_pipeline()
#    id_ = row["ID"]+ "_" + row["cond"]
    id_ = row[ID_COLUMN]
    list_of_lemma.extend(lemmas)
    list_of_form.extend(forms)
    print(f"{time_now()}: finished row {index} with id {id_}")

df = pd.concat(list_of_df)
df = df.rename(columns={"type":"class"})

df["token"] = list_of_form
df["lemma"] = list_of_lemma


df_type=df[~df.duplicated(subset=["id","class","token"],keep='first')]


##DROPNING NOT USEFUL COLUMNS

#list_of_banned_columns = ["lemma","punctenclose","degree"]
#df.drop(list_of_banned_columns)

df.to_csv(f"./documents/{BASE_NAME}_{LANGUAGE}_morph_matrix_token.csv",index=False)
df_type.to_csv(f"./documents/{BASE_NAME}_{LANGUAGE}_morph_matrix_type.csv",index=False)
