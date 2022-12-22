# General functions and routines used in the dashboard

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image


##### Dashboard main page
def prompt_to_csv(df):
    df_download = df
    df_download['Filename']='p'+df_download['ID'].astype('str')+'_1.png'
    df_download = df[['Prompt','Filename']].drop_duplicates(subset='Filename')
    return df_download.to_csv().encode('utf-8')

##### Manual assessment

def add_previous_manual_assessments():
    '''
    This is a routine to allow the user to upload prior manual ratings and override
    current ratings. This way the user can restart a manual assessment.
    '''
    # Create dict to translate uploaded score into str format used during manual assessment
    Bool_str_dict = {True:'Yes',False:'No'}

    st.subheader('Add previous assessments')
    st.write('Upload results of previous assessment (as downloaded from summary page) to add these results and skip these images in your current manual assessment. Note that you can only add results for images which you have uploaded using the same file name.')

    uploaded_ratings = st.file_uploader('Select .csv for upload', accept_multiple_files=False)
    if uploaded_ratings != None:
        try:
            uploaded_ratings_df = pd.read_csv(uploaded_ratings)
            overlapping_files_df =pd.merge(st.session_state['eval_df'],uploaded_ratings_df,on='File_name',how='inner')
            st.write('Number of matching file names found: '+ str(len(overlapping_files_df)))
            st.write('Click "Add results" button to add / override current ratings with uploaded ratings.')
        except UnicodeDecodeError:
            st.write('WARNING: The uploaded file has to be a .csv downloaded from the "Assessment summary" page.')


    submitted = st.button("Add results")
    if submitted:
        try:
            for row in uploaded_ratings_df.itertuples():
                st.session_state['eval_df'].loc[
                    st.session_state['eval_df']['File_name']==row.File_name,'manual_eval']=True
                st.session_state['eval_df'].loc[
                    st.session_state['eval_df']['File_name']==row.File_name,'manual_eval_completed']=True
                st.session_state['eval_df'].loc[
                    st.session_state['eval_df']['File_name']==row.File_name,'manual_eval_task_score']=Bool_str_dict[row.Score]

            # Reset page after ratings were submitted
            st.experimental_rerun()
        except NameError:
            st.write('You need to upload a .csv file before you can add results.')


##### Assessment summary
def plot_style_simple(results_df, return_table = False):
    '''
    Simple plot function for plotting just one dataframe of results
    '''
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
    '''
    Plot function which can plot to dataframe for comparison
    '''
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
    '''
    Routine used to give user the choice between showing results as bar chart or table
    '''
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
    '''
    Routine used to allow user to visualise uploaded results before completing any assessments
    '''
    st.write('Complete {0} assessment or upload .csv with saved {0} assessment to generate summary.'.format(type_str))

    # Display file uploader
    file_upload = st.file_uploader("Upload .csv with saved {0} assessment to plot prior results.".format(type_str))
    if file_upload != None:
        file_upload_df = pd.read_csv(file_upload).copy()
        print_results_tabs(file_upload=None, results_df=file_upload_df)