import streamlit as st
import pandas as pd 
import numpy as np
from PIL import Image
import os
path = os.path.dirname(__file__)
st.write(path)

# Setup
## Load prompt directory
prompt_dir = pd.read_csv('Data/Prompt_dir_221128.csv') #second version of prompt_dir
st.session_state['prompt_dir'] = prompt_dir
## Create lists of prompts for manual and automated assessments
st.session_state['automated_tasks'] = ['Multiple object types', 'Single object','Negation']
automated_prompts = prompt_dir.loc[
    (prompt_dir['Auto_assessment']==True)&
    (prompt_dir['Task']).isin(st.session_state['automated_tasks'])].ID.tolist()
manual_prompts = prompt_dir.ID.tolist()

# Page
st.title('Generative Image Benchmark')
st.write('This is an evaluation platform to assess the performance of image generation algorithms developed by Intel Labs. This is the alpha version of the platform and still in development. Refer to the following link for a user guide: https://github.com/8erberg/Intel-Generative-Image-Dashboard/blob/main/README.md')

side_image = Image.open('/Graphics/IL_logo.png')
st.sidebar.image(side_image)


# Generate empty dataset for results, if it does not exist yet
try:
    num_uploaded_images = st.session_state['eval_df'].shape[0]
except KeyError:
    st.session_state['eval_df'] = pd.DataFrame(
        columns=['File_name','Prompt_no','automated_eval','manual_eval','manual_eval_completed','manual_eval_task_score'])
    st.session_state['uploaded_img'] = []

# Create dic for automated asssssment if it does not excist yet
try:
    test_dict = st.session_state['results_dict']
except KeyError:
    st.session_state['results_dict'] = {}

# Data upload setup
st.subheader('Data upload')
#uploaded_files = st.file_uploader('Upload generated images', accept_multiple_files=True)
with st.form("my-form", clear_on_submit=True):
        uploaded_files = st.file_uploader('Select images for upload', accept_multiple_files=True)

        man_assessment_share = st.selectbox(
            'Select share of uploaded images to be used for manual assessment.',
            ('100%', '50%'))

        submitted = st.form_submit_button("Upload images")
        st.session_state['uploaded_img'] = st.session_state['uploaded_img']+uploaded_files


# Add new uploaded images to session state
## Try to append it to pre-existing list, else create new list in session state
## Always reset uploaded files to empty list after they have been added to state
if len(uploaded_files) != 0:
    try:
        # Extract prompts of uploaded files
        file_names = [x.name for x in uploaded_files]
        files_prompts = [x.split('_')[0][1:] for x in file_names]

        # Create manual evaluation df
        df_dict = {'File_name':file_names, 'Prompt_no':files_prompts}
        eval_df = pd.DataFrame(df_dict)
        eval_df['automated_eval'] = eval_df['Prompt_no'].astype('int').isin(automated_prompts)
        eval_df['manual_eval'] = eval_df['Prompt_no'].astype('int').isin(manual_prompts)
        eval_df['manual_eval_completed'] = False
        eval_df['manual_eval_task_score'] = np.nan

        # Exclude given percentage of uploaded images from manual assessment; with random selection
        if man_assessment_share == '50%':
            reassign_number = int(len(eval_df)/2)
            manual_eval_reassign = eval_df['manual_eval']
            random_image_indices = np.random.choice(len(manual_eval_reassign),reassign_number, replace=False)
            manual_eval_reassign.iloc[random_image_indices]=False
            eval_df['manual_eval'] = manual_eval_reassign

        # Join new uploaded df with existing df
        joint_eval_df = pd.concat([st.session_state['eval_df'], eval_df], ignore_index=True)
        
        # Add task name to eval_df
        Prompt_no_task_dict = dict(zip(prompt_dir.ID.astype('str').to_list(),prompt_dir.Task.to_list()))
        joint_eval_df['Task'] = joint_eval_df.Prompt_no.map(Prompt_no_task_dict)
        
        # Save eval_df to session state
        st.session_state['eval_df'] = joint_eval_df

    except KeyError:
        st.session_state['uploaded_img'] = uploaded_files


eval_df = st.session_state['eval_df']
if eval_df.shape[0]!=0:
    # Print current state of uploaded data
    st.write("{0} images uploaded. Reload the page to reset the image upload.".format(str(eval_df.shape[0])))
    st.write("- Available for manual assessment: ", str(sum(eval_df.manual_eval)))
    manual_eval_available = sum(eval_df.manual_eval)
    st.write("- Available for automated assessment: ", str(sum(eval_df.automated_eval)))
else:
    st.write("Upload files to start the assessment.")

#st.write(eval_df)
#st.write(prompt_dir)
#st.session_state['eval_df']
