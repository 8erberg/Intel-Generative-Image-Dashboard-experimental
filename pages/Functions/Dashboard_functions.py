# General functions and routines used in the dashboard

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image

#TODO: add better comments to functions

##### Assessment summary
def plot_style_simple(results_df, return_table = False):
  eval_sum = results_df.groupby('Task')['Score'].sum()
  eval_count = results_df.groupby('Task')['Score'].count()
  eval_share = (eval_sum/eval_count)*100

  if return_table:
    return_series = results_df.groupby('Task')['Score'].sum()/results_df.groupby('Task')['Score'].count()*100
    return_series = return_series.rename('Percentage correct')
    return return_series

  # Add small amount to make the bars on plot not disappear
  eval_share = eval_share+1

  fig = plt.figure(figsize=(12, 3))
  sns.barplot(x=eval_share.index, y=eval_share.values, palette='GnBu')
  plt.xticks(rotation=-45)
  plt.ylabel('Percentage correct')
  plt.xlabel(' ')
  return fig

def plot_style_combined(results_df, uploaded_df = None, return_table=False):
  # Create joined dataframe of results and uploadd_df
  uploaded_results_df = uploaded_df
  manual_results_df['Model']='Current'
  uploaded_results_df['Model']='Uploaded'
  results_df = pd.concat([manual_results_df,uploaded_results_df])

  # Create scores for plot
  eval_sum = results_df.groupby(['Model','Task'])['Score'].sum()
  eval_count = results_df.groupby(['Model','Task'])['Score'].count()
  eval_share = (eval_sum/eval_count)*100
  eval_share = eval_share.reset_index()

  if return_table:
    return_series = results_df.groupby(['Task','Model'])['Score'].sum()/results_df.groupby(['Task','Model'])['Score'].count()*100
    return_series = return_series.rename('Percentage correct')
    return return_series

  # Add small amount to make the bars on plot not disappear
  eval_share['Score'] = eval_share['Score']+1

  # Create plot
  fig = plt.figure(figsize=(12, 3))
  sns.barplot(data=eval_share,x='Task',y='Score',hue='Model', palette='GnBu')
  plt.xticks(rotation=-45)
  plt.ylabel('Percentage correct')
  plt.xlabel(' ')
  return fig


def print_results_tabs(file_upload, results_df, file_upload_df=None):
  # Create a tab for bar chart and one for table data
  tab1, tab2 = st.tabs(["Bar chart", "Data table"])
  with tab1:
    # If df was uploaded for comparison, we create comparison plot, else simple plot
    if file_upload == None:
      fig = plot_style_simple(results_df)
      st.pyplot(fig)
    else:
      fig = plot_style_combined(results_df,file_upload_df)
      st.pyplot(fig)

  with tab2:
    # If df was uploaded for comparison, we create comparison table, else simple table
    if file_upload == None:
      table = plot_style_simple(results_df, return_table=True)
      st.write(table)
    else:
      table = plot_style_combined(results_df,file_upload_df, return_table=True)
      st.write(table)


def pre_assessment_visualisation(type_str):
  st.write('Complete {0} assessment or upload .csv with saved {0} assessment to generate summary.'.format(type_str))

  # Display file uploader
  file_upload = st.file_uploader("Upload .csv with saved {0} assessment to plot prior results.".format(type_str))
  if file_upload != None:
    file_upload_df = pd.read_csv(file_upload).copy()
    print_results_tabs(file_upload=None, results_df=file_upload_df)