import pandas as pd
import os
import arguments as args

cooc_file = os.path.join(args.cooc_dir, 'cooccurrences.csv')
selected_cooc_file = os.path.join(args.cooc_dir, 'cooccurrences.selected.csv')

df = pd.read_csv(cooc_file, index_col=0)

df_f = df
# filter the ones not equal to another
df_f = df_f.loc[df_f.item_left != df_f.item_right]
# filter minimum total count
df_f = df_f.loc[df_f.total_count > args.cooc_min_count]
# filter rato
df_f = df_f.loc[df_f.ratio > args.cooc_min_ratio]

df['selected'] = False
df.loc[df_f.index, 'selected'] = True
df = df.sort_values(['selected', 'ratio', 'total_count'], ascending=False)

df.to_csv(selected_cooc_file)
