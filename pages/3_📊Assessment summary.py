import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
side_image = Image.open('Graphics/IL_Logo.png')
st.sidebar.image(side_image)

@st.cache
def convert_df_to_csv(df):
  # IMPORTANT: Cache the conversion to prevent computation on every rerun
  return df[['File_name','Prompt_no','Task','Score']].to_csv().encode('utf-8')

def plot_style_simple(results_df, return_table = False):
  eval_sum = results_df.groupby('Task')['Score'].sum()
  eval_count = results_df.groupby('Task')['Score'].count()
  eval_share = (eval_sum/eval_count)*100

  if return_table:
    return results_df.groupby('Task')['Score'].sum()/results_df.groupby('Task')['Score'].count()

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
    return results_df.groupby(['Task','Model'])['Score'].sum()/results_df.groupby(['Task','Model'])['Score'].count()

  # Create plot
  fig = plt.figure(figsize=(12, 3))
  sns.barplot(data=eval_share,x='Task',y='Score',hue='Model', palette='GnBu')
  plt.xticks(rotation=-45)
  plt.ylabel('Percentage correct')
  plt.xlabel(' ')
  return fig

assessment_result_frames = {}



st.title('Assessment Summary')

st.header('Manual assessment')


try:
  if sum(st.session_state['eval_df']['manual_eval_completed'])>0:
    # Display file uploader
    manual_file_upload = st.file_uploader("Upload .csv with saved manual assessment for model comparison")
    if manual_file_upload != None:
      manual_file_upload_df = pd.read_csv(manual_file_upload)

    # Create dataset for manual summary plots
    manual_eval_df = st.session_state['eval_df']
    manual_eval_df['Score'] = manual_eval_df['manual_eval_task_score'].map({'Yes':True, 'No':False})
    manual_results_df = manual_eval_df.loc[
      (manual_eval_df['manual_eval']==True)&
      (manual_eval_df['manual_eval_completed']==True)]

    assessment_result_frames['Manual assessment'] = manual_results_df

    # Create a tab for bar chart and one for table data
    tab1, tab2 = st.tabs(["Bar chart", "Data table"])
    with tab1:
      # If df was uploaded for comparison, we create comparison plot, else simple plot
      if manual_file_upload == None:
        fig = plot_style_simple(manual_results_df)
        st.pyplot(fig)
      else:
        fig = plot_style_combined(manual_results_df,manual_file_upload_df)
        st.pyplot(fig)

    with tab2:
      # If df was uploaded for comparison, we create comparison table, else simple table
      if manual_file_upload == None:
        table = plot_style_simple(manual_results_df, return_table=True)
        st.write(table)
      else:
        table = plot_style_combined(manual_results_df,manual_file_upload_df, return_table=True)
        st.write(table)

    st.download_button(
      label="Download manual assessment data",
      data=convert_df_to_csv(manual_results_df),
      file_name='manual_assessment.csv',
      mime='text/csv',
    )
  else:
    st.write('Complete manual assessment to generate summary.')
except KeyError:
  st.write('Complete automated assessment to generate summary.')


st.write(' ')
st.header('Automated assessment')
try:
  # Create dataset for automated summary plots
  auto_eval_df = st.session_state['auto_eval_df']
  assessment_result_frames['Automated assessment'] = auto_eval_df

  # Display file uploader
  auto_file_upload = st.file_uploader("Upload .csv with saved automated assessment for model comparison")  


  # If df was uploaded for comparison, we create comparison plot, else simple plot
  if auto_file_upload == None:
    fig = plot_style_simple(auto_eval_df)
    st.pyplot(fig)
  else:
    fig = plot_style_combined(auto_eval_df,auto_file_upload)
    st.pyplot(fig)

  st.download_button(
    label="Download automated assessment data",
    data=convert_df_to_csv(auto_eval_df),
    file_name='automated_assessment.csv',
    mime='text/csv',
  )
except KeyError:
  st.write('Complete automated assessment to generate summary.')


try:
  # Start gallery
  st.header('Assessment gallery')

  assessment_method_selected = st.selectbox(
      'Select generation method',
      assessment_result_frames.keys())

  if len(assessment_result_frames.keys())<1:
    st.write('Complete manual or automated assessment to access images in the gallery.')

  # Create needed info frames
  gallery_df = assessment_result_frames[assessment_method_selected]
  curr_prompt_dir = st.session_state['prompt_dir']

  # Select task
  tasks_available = gallery_df.Task.unique().tolist()
  task_selected = st.selectbox('Select task type',tasks_available)
  # Select image type
  type_selected = st.selectbox(
      'Select image type',
      ('Correctly generated images', 'Incorrectly generated images'))
  type_selected_dict = {'Correctly generated images':True, 'Incorrectly generated images':False}
  # Create df for presented images
  gallery_df_print = gallery_df.loc[
    (gallery_df['Score']==type_selected_dict[type_selected])&
    (gallery_df['Task']==task_selected)]
  # Select presented image and prompt
  generation_number = st.number_input('Generation number',min_value=1, max_value=len(gallery_df_print), step=1)
  gallery_row_print = gallery_df_print.iloc[int(generation_number-1)]
  curr_Prompt_no = gallery_row_print.Prompt_no
  curr_Prompt = curr_prompt_dir[curr_prompt_dir['ID']==int(curr_Prompt_no)].Prompt
  curr_Picture_index = gallery_row_print.Picture_index.item()
  # Plot prompt and image
  st.write('Prompt: '+curr_Prompt.item())
  st.image(st.session_state['uploaded_img'][curr_Picture_index],width=350)

  #st.write(auto_df_print)
except IndexError:
  st.write('There is no image availabe in your selected category.')
except KeyError:
  pass
