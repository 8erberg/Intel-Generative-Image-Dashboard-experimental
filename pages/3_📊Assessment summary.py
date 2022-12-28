import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
from pages.Functions.Dashboard_functions import plot_style_simple, plot_style_combined, pre_assessment_visualisation
side_image = Image.open('Graphics/IL_Logo.png')
st.sidebar.image(side_image)

def pre_assessment_visualisation(type_str):
    '''
    Routine used to allow user to visualise uploaded results before completing any assessments
    '''
    st.write('Complete {0} assessment or upload .csv with saved {0} assessment to generate summary.'.format(type_str))

    # Display file uploader
    file_upload = st.file_uploader("Upload .csv with saved {0} assessment to plot prior results.".format(type_str), accept_multiple_files=True)
    if len(file_upload) > 0:
        print_results_tabs(file_upload=file_upload, results_df=None)

def multi_comparison_plotI(results_df = None, uploaded_df_list = []):
  # If list of uploaded_dfs is provided, we transform them into pd.Dfs and add the file name as model name
  # Multiple file uploader returns empty list as default
  file_upload_names = [x.name for x in uploaded_df_list]
  plot_df_list = [pd.read_csv(x) for x in uploaded_df_list]
  for i_df in range(len(file_upload_names)):
    plot_df_list[i_df]= plot_df_list[i_df].assign(Model=file_upload_names[i_df])

  # If results df is provided, add it to list of dfs to plot
  if type(results_df) == pd.DataFrame:
    plot_df_list.append(results_df)

  # Concat all frames to joined dataframe
  plot_df = pd.concat(plot_df_list)

  # Calculate the grouped percentage scores per task category and model
  grouped_series = plot_df.groupby(['Task','Model'])['Score'].sum()/plot_df.groupby(['Task','Model'])['Score'].count()*100
  grouped_series = grouped_series.rename('Percentage correct')

  # Create plot
  eval_share = grouped_series.reset_index()
  # Add small amount to make the bars on plot not disappear
  eval_share['Percentage correct'] = eval_share['Percentage correct']+1

  # Create plot
  fig = plt.figure(figsize=(12, 3))
  sns.barplot(data=eval_share,x='Task',y='Percentage correct',hue='Model', palette='GnBu')
  plt.xticks(rotation=-65)
  plt.xlabel(' ')
  return fig,grouped_series


def print_results_tabs(file_upload, results_df):
    '''
    #Routine used to give user the choice between showing results as bar chart or table
    '''
    # Create a tab for bar chart and one for table data
    fig, table = multi_comparison_plotI(results_df=results_df, uploaded_df_list=file_upload)
    tab1, tab2 = st.tabs(["Bar chart", "Data table"])
    with tab1:
      st.pyplot(fig)

    with tab2:
        st.write(table)


@st.cache
def convert_df_to_csv(df):
  # IMPORTANT: Cache the conversion to prevent computation on every rerun
  return df[['File_name','Prompt_no','Task','Score']].to_csv().encode('utf-8')

assessment_result_frames = {}


st.title('Assessment Summary')
st.header('Manual assessment')


try:
  if sum(st.session_state['eval_df']['manual_eval_completed'])>0:
    # Display file uploader
    manual_file_upload = st.file_uploader("Upload .csv with saved manual assessment for model comparison", accept_multiple_files=True)
    # Create dataset for manual summary plots
    manual_eval_df = st.session_state['eval_df']
    manual_eval_df['Score'] = manual_eval_df['manual_eval_task_score'].map({'Yes':True, 'No':False})
    manual_results_df = manual_eval_df.loc[
      (manual_eval_df['manual_eval']==True)&
      (manual_eval_df['manual_eval_completed']==True)]
    manual_results_df['Model']='Manual assessment'

    assessment_result_frames['Manual assessment'] = manual_results_df

    # Add plots / tables to page
    #try:
    #  manual_file_upload_df = pd.read_csv(manual_file_upload).copy()
    #  print_results_tabs(file_upload=manual_file_upload, results_df=manual_results_df, file_upload_df=manual_file_upload_df)
    #except ValueError:
    print_results_tabs(file_upload=manual_file_upload, results_df=manual_results_df)

    st.download_button(
      label="Download manual assessment data",
      data=convert_df_to_csv(manual_results_df),
      file_name='manual_assessment.csv',
      mime='text/csv',
    )
  else:
    pre_assessment_visualisation(type_str='manual')
except KeyError:
  pre_assessment_visualisation(type_str='manual')

st.write(' ')
st.header('Automated assessment')
try:
  # Create dataset for automated summary plots
  auto_eval_df = st.session_state['auto_eval_df']
  auto_eval_df['Model']='Automated assessment'
  assessment_result_frames['Automated assessment'] = auto_eval_df

  # Display file uploader
  auto_file_upload = st.file_uploader("Upload .csv with saved automated assessment for model comparison", accept_multiple_files=True)  

  # Add plots / tables to page
  #try:
  #  auto_file_upload_df = pd.read_csv(auto_file_upload).copy()
  #  print_results_tabs(file_upload=auto_file_upload, results_df=auto_eval_df, file_upload_df=auto_file_upload_df)
  #except ValueError:
  #  print_results_tabs(file_upload=auto_file_upload, results_df=auto_eval_df)
  print_results_tabs(file_upload=auto_file_upload, results_df=auto_eval_df)

  st.download_button(
    label="Download automated assessment data",
    data=convert_df_to_csv(auto_eval_df),
    file_name='automated_assessment.csv',
    mime='text/csv',
  )
except KeyError:
  pre_assessment_visualisation(type_str='automated')


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

