import streamlit as st
import numpy as np
from itertools import compress
from PIL import Image
from pages.Functions.Assessment_functions import CLIP_single_object_classifier, CLIP_multi_object_recognition_DSwrapper, CLIP_object_negation, DETR_multi_object_counting_DSwrapper


# Create dictionary to hold functions
fun_dict = {
    'Multiple object types':CLIP_multi_object_recognition_DSwrapper, 
    'Single object':CLIP_single_object_classifier,
    'Negation':CLIP_object_negation,
    'Numbers (multiple objects)':DETR_multi_object_counting_DSwrapper,
    'Simple arithmetic':DETR_multi_object_counting_DSwrapper}


st.title('Automated Assessment')
st.write('On this page you can use automated assessment algorithms to assess how good uploaded images match their respective prompts.')
st.write(' ')
st.sidebar.image('Graphics/IL_Logo.png')

try:
    # Create necessary variables
    prompt_dir = st.session_state['prompt_dir']
    curr_eval_df = st.session_state['eval_df']
    curr_eval_df['Picture_index']=curr_eval_df.index.values

    # Assess how many images are available for automatic assessment
    automated_eval_available = sum(curr_eval_df['automated_eval'])

    # Add task name to eval_df
    temp_prompt_dir=prompt_dir[['ID','Representations','Task_specific_label']]
    temp_prompt_dir['Prompt_no']=temp_prompt_dir['ID'].astype('str')
    curr_eval_df = curr_eval_df.merge(temp_prompt_dir,on='Prompt_no')
except KeyError:
    automated_eval_available = 0


# If images for assessment available: create form to start assessment
# Else: Note to upload images for assessment
if automated_eval_available > 0:
    
    with st.form("auto_assessment_form",clear_on_submit=True):
        # Form info statment
        st.write('Select tasks to assess with the automated assessment:')

        # Add selection for available categories
        assess_multi_object = st.checkbox(
            'Multiple object types ({0} images available)'.format(
                len(curr_eval_df.loc[
                    (curr_eval_df['automated_eval']==True)&
                    (curr_eval_df['Task']=='Multiple object types')])
            ))
        assess_single_object = st.checkbox(
            'Single object type ({0} images available)'.format(
                len(curr_eval_df.loc[
                    (curr_eval_df['automated_eval']==True)&
                    (curr_eval_df['Task']=='Single object')])
            ))

        negation = st.checkbox(
            'Negation ({0} images available)'.format(
                len(curr_eval_df.loc[
                    (curr_eval_df['automated_eval']==True)&
                    (curr_eval_df['Task']=='Negation')])
            ))

        numbers = st.checkbox(
            'Numbers / Counting ({0} images available)'.format(
                len(curr_eval_df.loc[
                    (curr_eval_df['automated_eval']==True)&
                    (curr_eval_df['Task']=='Numbers (multiple objects)')])
            ))

        arithmetic = st.checkbox(
            'Simple arithmetic ({0} images available)'.format(
                len(curr_eval_df.loc[
                    (curr_eval_df['automated_eval']==True)&
                    (curr_eval_df['Task']=='Simple arithmetic')])
            ))
        
        submitted = st.form_submit_button("Start automated assessment")
        if submitted:
            # Create list for tasks which were selected for assessment
            selected_tasks = list(
                compress(
                    ['Multiple object types','Single object','Negation','Numbers (multiple objects)','Simple arithmetic'], 
                    [assess_multi_object,assess_single_object,negation,numbers,arithmetic]))
            # Create dataset to loop over with assessment
            assessed_df = curr_eval_df.loc[
                    (curr_eval_df['automated_eval']==True)&
                    (curr_eval_df['Task'].isin(selected_tasks))]
            results_column = []
            
            for row in assessed_df.itertuples():
                # Apply task based classifier and safe in list
                temp_image = Image.open(st.session_state['uploaded_img'][row.Picture_index])
                temp_result = fun_dict[row.Task](
                    temp_image,row.Representations,row.Task_specific_label)
                results_column.append(temp_result)

            assessed_df['Score']=results_column
            st.session_state['auto_eval_df']=assessed_df[['File_name','Prompt_no','Picture_index','Task','Score']]
            st.write('Completed assessment. Access results on the summary page.')
else:
    st.write('Upload files on dashboard starting page to start automated assessment.')

#st.write(st.session_state['auto_eval_df'])