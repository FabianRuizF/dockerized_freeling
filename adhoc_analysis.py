import pandas as pd
#pd.set_option('display.max_colwidth',None)
#pd.set_option('display.max_columns',None)

not_used_columns = ["lemma","degree","polite"]

df_token = pd.read_csv("morph_matrix_token.csv")
df_type = pd.read_csv("morph_matrix_type.csv")

df_token = df_token.loc[:, ~df_token.columns.str.contains('^Unnamed')]
df_type = df_type.loc[:, ~df_type.columns.str.contains('^Unnamed')]

try:
    df_token=df_token.drop(columns=not_used_columns,axis=1)
    df_type=df_type.drop(columns=not_used_columns,axis=1)
except:
    pass

df_token.to_csv("morph_matrix_token.csv",index=False)
df_type.to_csv("morph_matrix_type.csv",index=False)





health_df = pd.read_csv("health_pat.csv")
groups = df_token.groupby("id")
content_list = ["noun","verb","adjective","adverb"]
person_list = ["1","2","3"]
metric_list = []
for group_name,df_group in groups:
    noun_len = len(df_group[df_group.pos=='noun'])
    verb_len = len(df_group[df_group.pos=='verb'])

    person_len = person= len(df_group.dropna(subset=["person"]))
    content_words_len = len(df_group[df_group.pos.isin(content_list)])
    all_words_len = len(df_group)

    noun_vs_all = noun_len/all_words_len
    noun_vs_content = noun_len/content_words_len
    verbs_vs_all = verb_len/all_words_len
    verbs_vs_content =  verb_len /content_words_len
    metric_list.append([noun_vs_all,noun_vs_content,verbs_vs_all,verbs_vs_content,all_words_len,content_words_len,person_len])



cols = ['noun_all_ratio','noun_content_ratio','verb_all_ratio','verb_content_ratio','all_words','only_content',"only_person_token"]
metric_df = pd.DataFrame(metric_list, columns=cols)
health_df = pd.concat([health_df, metric_df], axis=1)




df_token["tense"] = df_token["tense"].fillna("empty")
df_token.loc[df_token.tense=="imperfect","tense"]  = "past"


import itertools

df_token = df_token.dropna(subset=["person"])
df_token["person"] = df_token["person"].astype(int).astype(str)

person_list = ["1", "2","3"]
tense_list = ['empty', 'present', 'past', 'conditional', 'future']
index_list = list(itertools.product(person_list, tense_list))

groups=df_token.groupby(["id"])


df_person_metric = []
for group_name,df_group in groups:
    only_person= len(df_group.dropna(subset=["person"]))
    count_group = df_group.groupby(["person","tense"],dropna=True)
    group_sizes = count_group.size()
    for index_ in index_list:
        if(index_ in group_sizes.index):
            continue
        else:
            group_sizes=group_sizes.append(pd.Series([0],index=[index_]))
    group_sizes = group_sizes.sort_index()
    group_sizes = pd.DataFrame(group_sizes).transpose()
    group_sizes.columns = group_sizes.columns.get_level_values(0) +" "+ group_sizes.columns.get_level_values(1) + " " + "token"
    df_person_metric.append(group_sizes)


df_person_metric = pd.concat(df_person_metric)
df_person_metric = df_person_metric.reset_index()

health_df = pd.concat([health_df,df_person_metric],axis=1)









df_type["tense"] = df_type["tense"].fillna("empty")
df_type.loc[df_type.tense=="imperfect","tense"]  = "past"
df_type = df_type.dropna(subset=["person"])
df_type["person"] = df_type["person"].astype(int).astype(str)

person_list = ["1", "2","3"]
tense_list = ['empty', 'present', 'past', 'conditional', 'future']
index_list = list(itertools.product(person_list, tense_list))

groups=df_type.groupby(["id"])

person_metric_list =[]
df_person_metric = []
for group_name,df_group in groups:
    only_person= len(df_group.dropna(subset=["person"]))
    person_metric_list.append(only_person)
    count_group = df_group.groupby(["person","tense"],dropna=True)
    group_sizes = count_group.size()
    for index_ in index_list:
        if(index_ in group_sizes.index):
            continue
        else:
            group_sizes=group_sizes.append(pd.Series([0],index=[index_]))
    group_sizes = group_sizes.sort_index()
    group_sizes = pd.DataFrame(group_sizes).transpose()
    group_sizes.columns = group_sizes.columns.get_level_values(0) +" "+ group_sizes.columns.get_level_values(1) + " " + "type"
    df_person_metric.append(group_sizes)


df_person_metric = pd.concat(df_person_metric)
df_person_metric = df_person_metric.reset_index()

health_df["only_person_type"] = person_metric_list
health_df = pd.concat([health_df,df_person_metric],axis=1)


health_df.to_csv("result_colombia_chile_v2.csv")



