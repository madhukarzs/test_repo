#!/usr/bin/env python
# coding: utf-8

# In[ ]:



####################################### Import Libraries #######################################
import streamlit as st
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.colors as clr
import plotly.figure_factory as ff
from PIL import Image
from streamlit_elements import dashboard
from contextlib import contextmanager
from abc import ABC, abstractmethod
from types import SimpleNamespace
from uuid import uuid4
import json
from streamlit_elements import mui, editor, sync, lazy
from streamlit_elements import nivo
from streamlit_elements import elements, mui, html
from streamlit import session_state as state
from sklearn.manifold import TSNE
import plotly.graph_objects as go
import seaborn as sns
import hydralit as hy
import hydralit_components as hc
from hydralit import HydraHeadApp
from hydralit_components import HyLoader, Loaders

class Dashboard:

    DRAGGABLE_CLASS = "draggable"

    def __init__(self):
        self._layout = []

    def _register(self, item):
        self._layout.append(item)

    @contextmanager
    def __call__(self, **props):
        # Draggable classname query selector.
        props["draggableHandle"] = f".{Dashboard.DRAGGABLE_CLASS}"

        with dashboard.Grid(self._layout, **props):
            yield

    class Item(ABC):

        def __init__(self, board, x, y, w, h, **item_props):
            self._key = str(uuid4())
            self._draggable_class = Dashboard.DRAGGABLE_CLASS
            self._dark_mode = False
            board._register(dashboard.Item(self._key, x, y, w, h, **item_props))

        def _switch_theme(self):
            self._dark_mode = not self._dark_mode

        @contextmanager
        def title_bar(self, padding="5px 15px 5px 15px", dark_switcher=True):
            with mui.Stack(
                className=self._draggable_class,
                alignItems="center",
                direction="row",
                spacing=1,
                sx={
                    "padding": padding,
                    "borderBottom": 1,
                    "borderColor": "divider",
                },
            ):
                yield

                if dark_switcher:
                    if self._dark_mode:
                        mui.IconButton(mui.icon.DarkMode, onClick=self._switch_theme)
                    else:
                        mui.IconButton(mui.icon.LightMode, sx={"color": "#ffc107"}, onClick=self._switch_theme)

        @abstractmethod
        def __call__(self):
            """Show elements."""
            raise NotImplementedError
            
class Editor(Dashboard.Item):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._dark_theme = True
        self._index = 0
        self._tabs = {}
        self._editor_box_style = {
            "flex": 1,
            "minHeight": 0,
            "borderBottom": 1,
            "borderTop": 1,
            "borderColor": "divider"
        }

    def _change_tab(self, _, index):
        self._index = index

    def update_content(self, label, content):
        self._tabs[label]["content"] = content

    def add_tab(self, label, default_content, language):
        self._tabs[label] = {
            "content": default_content,
            "language": language
        }

    def get_content(self, label):
        return self._tabs[label]["content"]

    def __call__(self):
        with mui.Paper(key=self._key, sx={"display": "flex", "flexDirection": "column", "borderRadius": 3, "overflow": "hidden"}, elevation=1):

            with self.title_bar("0px 15px 0px 15px"):
                mui.icon.Terminal()
                mui.Typography("Editor")

                with mui.Tabs(value=self._index, onChange=self._change_tab, scrollButtons=True, variant="scrollable", sx={"flex": 1}):
                    for label in self._tabs.keys():
                        mui.Tab(label=label)

            for index, (label, tab) in enumerate(self._tabs.items()):
                with mui.Box(sx=self._editor_box_style, hidden=(index != self._index)):
                    editor.Monaco(
                        css={"padding": "0 2px 0 2px"},
                        defaultValue=tab["content"],
                        language=tab["language"],
                        onChange=lazy(partial(self.update_content, label)),
                        theme="vs-dark" if self._dark_mode else "light",
                        path=label,
                        options={
                            "wordWrap": True
                        }
                    )

            with mui.Stack(direction="row", spacing=2, alignItems="center", sx={"padding": "10px"}):
                mui.Button("Apply", variant="contained", onClick=sync())
                mui.Typography("Or press ctrl+s", sx={"flex": 1}) 
                             
                    
####################################### Read Relevant Data #######################################
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
cmap_cf = clr.LinearSegmentedColormap.from_list('custom cf', ['#5FBF6D','#34503A'], N=256) ## conditional formatting colormap

# path = 'C:/Users/pk37814/Documents/WayFinder/dx23l_streamlit_v1/Data/'

static_data = pd.read_csv('static_data.csv') #
demo = pd.read_csv('demographics.csv') #
demo_data = pd.read_csv('demographics_data.csv') #
data = pd.read_csv('metrics_master_table_new.csv') #
# data['event_type'] = data['event_type'].apply(lambda x: ' '.join(x.split('_')[1:]).title())
duration = pd.read_csv('duration_data.csv') #
tsne_data = pd.read_csv('tsne_data1.csv')
comorbidity_data = pd.read_csv('comorbidities_data.csv') #
mapdata = pd.read_csv('map_data.csv')

#------------------------------------------adding top menu-----------------------------------------------------------------------
over_theme = {'txc_inactive': 'White','menu_background':'gray','txc_active':'black'}
app = hy.HydraApp(title='MG App',
#                   use_navbar=True,
#                   navbar_sticky=False,
                  navbar_theme=over_theme)  

####################################### Title #######################################
one = True
two=False
three=False
col1,col2,col3 = st.columns([4,1,1])
m = st.markdown("""
<style>
div.stButton > button:first-child {
    height: 3em;
width: 12em; 
font-size:24px !important;
border-radius: 20%;
}
</style>""", unsafe_allow_html=True)

with col1:
    st.markdown("<h1 style='text-align: left; margin-top: -50px;'>Wayfinder - Myasthenia Gravis</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: left; margin-top: -30px;'><i>Diagnosis to Line 3</i></h3>", unsafe_allow_html=True)

# with col2:
#     one = st.button("Cluster Profiles")
# with col3:
#     two = st.button("Cluster Deep-Dive")
    
def set_current_page(page,page_name):
    one = False
    two = False
    three = False
    page = True   
    current_page = page_name
    
if one == True:
    set_current_page(one,"one")
elif two == True:
    set_current_page(two,"two")
elif three == True:
    set_current_page(three,"three")
else:
    one = True
components.html("<div style = 'background-color:#333; height:50px; border-radius:5px; margin:0; padding:0'></div>",height=10)

####################################### adding sidebar #######################################

options = st.sidebar
with options:
    st.header("WayFinder Filters")
#     time_period = st.slider("TIME FRAME",2014,2022)
    
#     insight = st.selectbox("INSIGHT",["Business Rules","Business Rules + ML"])
#     st.write(insight)
    
#     if current_page == "one":
    filter_data = pd.DataFrame([
    #         ["Data Source","Cohort","Total Patients","Known Patients","Criteria"],
            ["SHS Claims","Myasthenia Gravis","29000","16000","Patients who have no history of lung or respiratory problems"],
            ["","Breast Cancer","30000","19000","Patients who have no history of cancer in family"],
            ["","NSCLC","39000","15000","Patients who have no history of lung or respiratory problems"]
        ])

    data_source = st.selectbox("DATA SOURCE",pd.unique(filter_data[0]))
    filter_data = (filter_data[filter_data[0]==data_source]).reset_index()
    patient_cohort = st.selectbox("PATIENT COHORT",pd.unique(filter_data[1]))

####################################### Section1: Cluster Profiles #######################################
 
        
########################################### draggable class #######################################
#if one == True:
@app.addapp()
def Executive_Summary():
    
    st.subheader("What are the key Patient Segments and corresponding distribution?")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        txt = st.text_area('', '''ARCHETYPE 1

         - Slower disease progression from Diagnosis to 3L
         - Low monitoring activity such as MRI/CT scan
         - Low to moderate frequency of adverse events
    ''', height=200)
        components.html(
        """
        <div class="card" style="width: 27rem; height: 15rem; background-color: #92D0AA; border-radius: 20px; border-style: solid; border-color: #195A32">
          <div class="card-body">
            <h3 class="card-title" style="color: white; font-family: Arial, Helvetica, sans-serif; text-align:center; font-size:22px"><i>Archetype 1</i></h3>
            <p class="card-text" style="font-size:20px; font-family: Arial">&nbsp;&nbsp;Number of Patients: <b>"""+static_data['Cluster 1'][0]+"""</b></p>

            <p class="card-text" style="font-size:20px; font-family: Arial">&nbsp;&nbsp;Time Duration(Days): <b>"""+str("{:,}".format(int(static_data['Cluster 1'][1])))+"""</b></p>
            <p class="card-text" style="font-size:20px; font-family: Arial">&nbsp;&nbsp;Average #Physician per Patient: <b>"""+static_data['Cluster 1'][2]+"""</b></p>
          </div>
        </div>
        """, height=270, width=450)
    #  "{:,}".format(analytical_data[analytical_data['cluster']==c]['provid_fin'].nunique())  
    with col2:
        txt = st.text_area('', '''ARCHETYPE 2

         - Slower disease progression from Diagnosis to 3L
         - Low frequency of adverse events and monitoring tests
         - Lower number of unique HCPs visited
    ''', height=200)
        components.html(
        """
        <div class="card" style="width: 27rem; height: 15rem; background-color: #4B9ABB; border-radius: 20px; border-style: solid; border-color: #3B4068">
          <div class="card-body">
            <h3 class="card-title" style="color: white; font-family: Arial, Helvetica, sans-serif; text-align:center; font-size:22px"><i>Archetype 2</i></h3>
            <p class="card-text" style="font-size:20px; font-family: Arial">&nbsp;&nbsp;Number of Patients: <b>"""+static_data['Cluster 2'][0]+"""</b></p>

            <p class="card-text" style="font-size:20px; font-family: Arial">&nbsp;&nbsp;Time Duration(Days): <b>"""+static_data['Cluster 2'][1]+"""</b></p>
            <p class="card-text" style="font-size:20px; font-family: Arial">&nbsp;&nbsp;Average #Physician per Patient: <b>"""+static_data['Cluster 2'][2]+"""</b></p>
          </div>
        </div>
        """, height=270, width=450)

    with col3:
        txt = st.text_area('', '''ARCHETYPE 3

         - Moderate disease progression from Diagnosis to 3L
         - Moderate to high frequency of monitoring and adverse events 
         - Earlier usage of PLEX and IVIGs
    ''', height=200)
        components.html(
        """
        <div class="card" style="width: 27rem; height: 15rem; background-color: #F2E394; border-radius: 20px; border-style: solid; border-color: #F7C505">
          <div class="card-body">
            <h3 class="card-title" style="color: white; font-family: Arial, Helvetica, sans-serif; text-align:center; font-size:22px"><i>Archetype 3</i></h3>
            <p class="card-text" style="font-size:20px; font-family: Arial">&nbsp;&nbsp;Number of Patients: <b>"""+static_data['Cluster 3'][0]+"""</b></p>

            <p class="card-text" style="font-size:20px; font-family: Arial">&nbsp;&nbsp;Time Duration(Days): <b>"""+static_data['Cluster 3'][1]+"""</b></p>
            <p class="card-text" style="font-size:20px; font-family: Arial">&nbsp;&nbsp;Average #Physician per Patient: <b>"""+static_data['Cluster 3'][2]+"""</b></p>
          </div>
        </div>
        """, height=270, width=450)

    with col4:
        txt = st.text_area('', '''ARCHETYPE 4

         - Fast disease progression from Diagnosis to 3L
         - High frequency of monitoring and adverse events
         - Earlier usage of PLEX and IVIGs
    ''', height=200)
        components.html(
        """
        <div class="card" style="width: 27rem; height: 15rem; background-color: #EC5923; border-radius: 20px; border-style: solid; border-color: #8E2E07">
          <div class="card-body">
            <h3 class="card-title" style="color: white; font-family: Arial; text-align:center; font-size:22px"><i>Archetype 4</i></h3>
            <p class="card-text" style="font-size:20px; font-family: Arial">&nbsp;&nbsp;Number of Patients: <b>"""+static_data['Cluster 4'][0]+"""</b></p>

            <p class="card-text" style="font-size:20px; font-family: Arial">&nbsp;&nbsp;Time Duration(Days): <b>"""+static_data['Cluster 4'][1]+"""</b></p>
            <p class="card-text" style="font-size:20px; font-family: Arial">&nbsp;&nbsp;Average #Physician per Patient: <b>"""+static_data['Cluster 4'][2]+"""</b></p>
          </div>
        </div>
        """, height=270, width=450)

    ####################################### Section2: Cluster Distribution #######################################
    col1, col2 = st.columns(2)

    with col1:
        with st.expander("Time Distribution", expanded=True):

            d1 = duration[duration['cluster']=='Cluster 1']['duration']
            d2 = duration[duration['cluster']=='Cluster 2']['duration']
            d3 = duration[duration['cluster']=='Cluster 3']['duration']
            d4 = duration[duration['cluster']=='Cluster 4']['duration']

            fig = ff.create_distplot([d1,d2,d3,d4], group_labels=['Archetype 1', 'Archetype 2', 'Archetype 3', 'Archetype 4'], 
                                     show_hist=True, colors=['#92D0AA','#4B9ABB','#F2E394','#EC5923'], bin_size=50, show_rug=False)
            fig.update_layout(height=650)
            fig.update_yaxes(title=None)
            fig.update_layout(title='Time Distribution')
            fig.update_layout(title_font_size=30)
            fig.update_layout(title_pad_l=270)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        with st.expander("Archetype Visualization", expanded=True):

    #         if st.button('Get tSNE Plot'):
            tsne_data['Archetype'] = tsne_data['Archetype'].astype(str)
            fig = px.scatter(tsne_data, x="tsne-2d-one", y="tsne-2d-two", color="Archetype", 
                             color_discrete_map = {'Archetype 1':'#92D0AA', 'Archetype 2':'#4B9ABB', 'Archetype 3':'#F2E394', 'Archetype 4':'#EC5923'}, opacity=0.7, height=600, category_orders={'cluster':['Archetype 1','Archetype 2','Archetype 3','Archetype 4']})
            fig.update_layout(template='plotly_dark')
            fig.update_yaxes(title=None)
            fig.update_xaxes(title=None)
            fig.update_layout(title='Archetype Visualization')
            fig.update_layout(title_font_size=30)
            fig.update_layout(title_pad_l=270)
            st.plotly_chart(fig, use_container_width=True)
    #         else:
    #             st.write('')

    st.markdown("""<hr style="height:1px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)


@app.addapp()
def Archetype_Journey():
    # ------------------------------------adding bubble chart-----------------------------------------------------------------
    st.subheader("How does the timing of key events differ by archetype ?")
    with st.expander("", expanded=True):
        #col1, col2 = st.columns([0.5, 5])

    #    with col1:
            st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: center;} </style>', unsafe_allow_html=True)
            cluster = st.radio("",('Archetype  1', 'Archetype  2', 'Archetype  3', 'Archetype  4'))

    #    with col2:
            if cluster == 'Archetype  1':
                HtmlFile = open("dx23l_cluster0.html", 'r', encoding='utf-8')
                source_code = HtmlFile.read()
                components.html(source_code, height = 600)

            elif cluster == 'Archetype  2':
                HtmlFile = open("dx23l_cluster1.html", 'r', encoding='utf-8')
                source_code = HtmlFile.read()
                components.html(source_code, height = 600)

            elif cluster == 'Archetype  3':
                HtmlFile = open("dx23l_cluster2.html", 'r', encoding='utf-8')
                source_code = HtmlFile.read()
                components.html(source_code, height = 600)

            elif cluster == 'Archetype  4':
                HtmlFile = open("dx23l_cluster3.html", 'r', encoding='utf-8')
                source_code = HtmlFile.read()
                components.html(source_code, height = 600)

    st.markdown("""<hr style="height:1px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
    
    # --------------patient journey
    st.subheader("How does the disease progression differ by Archetypes ?")
    with st.expander("", expanded=True):
        #col1, col2 = st.columns([0.5, 5])

    #    with col1:
            st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: center;} </style>', unsafe_allow_html=True)
            cluster = st.radio("",('Archetype 1', 'Archetype 2', 'Archetype 3', 'Archetype 4'))

    #    with col2:
            if cluster == 'Archetype 1':
                HtmlFile = open("mg_dx_to_3l_cluster1.html", 'r', encoding='utf-8')
                # st.markdown("""For Expanded View click here: <a href="https://github.com/deployapp-010/test1/blob/master/Cluster1_extension.html" target = "_blank"> Archetype 1 </a>""", unsafe_allow_html=True)
                source_code = HtmlFile.read() 
                components.html(source_code, height = 200)

            elif cluster == 'Archetype 2': 
                HtmlFile = open("mg_dx_to_3l_cluster2.html", 'r', encoding='utf-8')
                # st.markdown("""For Expanded View click here:<a href="https://github.com/deployapp-010/test1/blob/master/Cluster2_extension.html" target = "_blank"> Archetype 2 </a>""", unsafe_allow_html=True)
                source_code = HtmlFile.read() 
                components.html(source_code, height = 200) 

            elif cluster == 'Archetype 3': 
                HtmlFile = open("mg_dx_to_3l_cluster3.html", 'r', encoding='utf-8')
                # st.markdown("""For Expanded View click here:<a href="https://github.com/deployapp-010/test1/blob/master/Cluster3_extension.html" target = "_blank"> Archetype 3 </a>""", unsafe_allow_html=True)
                source_code = HtmlFile.read() 
                components.html(source_code, height = 200) 

            elif cluster == 'Archetype 4': 
                HtmlFile = open("mg_dx_to_3l_cluster4.html", 'r', encoding='utf-8')
                # st.markdown("""For Expanded View click here:<a href="https://github.com/deployapp-010/test1/blob/master/Cluster4_extension.html" target = "_blank"> Archetype 4 </a>""", unsafe_allow_html=True)
                source_code = HtmlFile.read() 
                components.html(source_code, height = 200) 

    st.markdown("""<hr style="height:1px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True) 

    #-----------------------------------------------------------------------------------------------------------------------------    
    st.subheader('How does the events evolve over time across Archetypes ?')

    with st.expander("Event Frequency per Quarter by Archetype", expanded=False):
        col1, col2, col3 = st.columns([0.5,1, 0.2])
        with col1:
            st.markdown("<h6 style='text-align: left; margin-left: 1rem; margin-bottom: 2.55rem; font-size:1.5rem'>Events</h6>", unsafe_allow_html=True)
            HtmlFile = open("dx_to_3l_events_html.html", 'r', encoding='utf-8')
            source_code = HtmlFile.read() 
            components.html(source_code, height = 800)

        with col2:
            st.markdown("<h6 style='text-align: left; margin-left: 1rem; font-size:1.5rem'>Frequency <em>(Each pixel represents frequency of event per quarter)</em></h6>", unsafe_allow_html=True)
            HtmlFile = open("dx_to_3l_bitplot_html_overall_freq.html", 'r', encoding='utf-8')
            source_code = HtmlFile.read() 
            components.html(source_code, height = 800)

        with col3:
                name = ['Diagnosis','Procedure','Treatment']
                cel = [999, 99, 9]

                df = pd.DataFrame({'Name':name,'Cel':cel})

                def color(val):
                    if val == 999:
                        color = '#EA7200'
                    elif val == 99:
                        color = '#32A29A'
                    elif val == 9:
                        color = '#E5C457'
                    return 'background-color: %s' % color
                hide_table_row_index = """
                            <style>
                            tbody th {display:none}
                            .blank {display:none}
                            </style>
                            """


                st.markdown(hide_table_row_index, unsafe_allow_html=True)
                st.table(df.style.applymap(color, subset=['Cel'])
                             .set_properties(**{'font-size': '0pt'}, subset=['Cel'])
                             .set_table_styles([{'selector': 'thead', 'props': [('display', 'none')]}])
                            )

    with st.expander("Event Prevalence per Quarter by Archetype", expanded=False):
        col1, col2, col3 = st.columns([0.5,1, 0.2])
        with col1:
            st.markdown("<h6 style='text-align: left; margin-left: 1rem; margin-bottom: 2.55rem; font-size:1.5rem'>Events</h6>", unsafe_allow_html=True)
            HtmlFile = open("dx_to_3l_events_html.html", 'r', encoding='utf-8')
            source_code = HtmlFile.read() 
            components.html(source_code, height = 800)

        with col2:
            st.markdown("<h6 style='text-align: left; margin-left: 1rem; font-size:1.5rem'>Prevalence <em>(Each pixel represents prevalence of event per quarter)</em></h6>", unsafe_allow_html=True)
            HtmlFile = open("dx_to_3l_bitplot_html_overall_prev.html", 'r', encoding='utf-8')
            source_code = HtmlFile.read() 
            components.html(source_code, height = 800)

        with col3:
            name = ['Diagnosis','Procedure','Treatment']
            cel = [999, 99, 9]

            df = pd.DataFrame({'Name':name,'Cel':cel})

            def color(val):
                if val == 999:
                    color = '#EA7200'
                elif val == 99:
                    color = '#32A29A'
                elif val == 9:
                    color = '#E5C457'
                return 'background-color: %s' % color
            hide_table_row_index = """
                        <style>
                        tbody th {display:none}
                        .blank {display:none}
                        </style>
                        """


            st.markdown(hide_table_row_index, unsafe_allow_html=True)
            st.table(df.style.applymap(color, subset=['Cel'])
                         .set_properties(**{'font-size': '0pt'}, subset=['Cel'])
                         .set_table_styles([{'selector': 'thead', 'props': [('display', 'none')]}])
                        )


    #-------------------------------------------- map ---------------------------------------------------------------------------------
    st.markdown("""<hr style="height:1px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

#     st.subheader("Geographical Distribution across Archetype ?")
    
#     with st.expander("", expanded=True):
#         st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: center;} </style>', unsafe_allow_html=True)
#         cluster = st.radio("",('Archetype 1 ', 'Archetype 2 ', 'Archetype 3 ', 'Archetype 4 '))

# #         col1,col2,col3,col4 = st.columns([1,1,1,1])
# #         with col1:
# #             st.markdown("<h6 style='text-align: left; margin-left: 1rem; margin-bottom: 2.55rem; font-size:1.5rem'>Archetype 1</h6>", unsafe_allow_html=True)
        
#         if cluster == 'Archetype 1 ':
#             cluster1 = mapdata[mapdata['cluster']=='Cluster 1'].groupby('patient_state')['patient_id'].nunique().reset_index()
#             fig = go.Figure(data=go.Choropleth(
#             locations=cluster1['patient_state'], # Spatial coordinates
#             z = cluster1['patient_id'].astype(float), # Data to be color-coded
#             locationmode = 'USA-states', # set of locations match entries in `locations`
#             colorscale = ['#92D0AA','#1d5c35'],
#             #colorbar_title = "Hundreds",
#             ))

#             fig.update_layout(
#     #                     title_text = 'Patient Level Insights',
#                 geo_scope='usa', # limite map scope to USA
#             )

#             st.plotly_chart(fig, use_container_width=True, sharing="streamlit") 
#         elif cluster == 'Archetype 2 ':
# #         with col2:
#             st.markdown("<h6 style='text-align: left; margin-left: 1rem; margin-bottom: 2.55rem; font-size:1.5rem'>Archetype 2</h6>", unsafe_allow_html=True)
#             cluster2 = mapdata[mapdata['cluster']=='Cluster 2'].groupby('patient_state')['patient_id'].nunique().reset_index()
#             fig = go.Figure(data=go.Choropleth(
#             locations=cluster2['patient_state'], # Spatial coordinates
#             z = cluster2['patient_id'].astype(float), # Data to be color-coded
#             locationmode = 'USA-states', # set of locations match entries in `locations`
#             colorscale = ['#b7dded','#2d6d87'],
#             #colorbar_title = "Hundreds",
#             ))

#             fig.update_layout(
#     #                     title_text = 'Patient Level Insights',
#                 geo_scope='usa', # limite map scope to USA
#             )

#             st.plotly_chart(fig, use_container_width=True, sharing="streamlit") 

#         elif cluster == 'Archetype 3 ':
# #         with col3:
#             st.markdown("<h6 style='text-align: left; margin-left: 1rem; margin-bottom: 2.55rem; font-size:1.5rem'>Archetype 3</h6>", unsafe_allow_html=True)
#             cluster3 = mapdata[mapdata['cluster']=='Cluster 3'].groupby('patient_state')['patient_id'].nunique().reset_index()
#             fig = go.Figure(data=go.Choropleth(
#             locations=cluster3['patient_state'], # Spatial coordinates
#             z = cluster3['patient_id'].astype(float), # Data to be color-coded
#             locationmode = 'USA-states', # set of locations match entries in `locations`
#             colorscale = ['#F2E394','#ad992f'],
#             #colorbar_title = "Hundreds",
#             ))

#             fig.update_layout(
#     #                     title_text = 'Patient Level Insights',
#                 geo_scope='usa', # limite map scope to USA
#             )

#             st.plotly_chart(fig, use_container_width=True, sharing="streamlit") 

#         elif cluster == 'Archetype 4 ':
# #         with col4:
#             st.markdown("<h6 style='text-align: left; margin-left: 1rem; margin-bottom: 2.55rem; font-size:1.5rem'>Archetype 4</h6>", unsafe_allow_html=True)
#             cluster4 = mapdata[mapdata['cluster']=='Cluster 4'].groupby('patient_state')['patient_id'].nunique().reset_index()
#             fig = go.Figure(data=go.Choropleth(
#             locations=cluster4['patient_state'], # Spatial coordinates
#             z = cluster4['patient_id'].astype(float), # Data to be color-coded
#             locationmode = 'USA-states', # set of locations match entries in `locations`
#             colorscale = ['#f2aa8f','#EC5923'],
#             colorbar_title = "Hundreds",
#             ))

#             fig.update_layout(
#                 geo_scope='usa', # limite map scope to USA
#             )

#             st.plotly_chart(fig, use_container_width=True, sharing="streamlit") 
################################################ page 2 ###################################################
#elif two == True:
@app.addapp()
def Archetype_Profile():
    
    st.header("Customer Insights")
#     st.subheader('This is 2nd page')
  
#     st.subheader("Biomarker Split")
    
# #     if "w1" not in state:
#     board = Dashboard()
#     w1 = SimpleNamespace(
#         dashboard=board,
#         editor=Editor(board, 0, 0, 6, 11, minW=3, minH=3),
#     )
#     state.w1 = w1
#     w1.editor.add_tab("Card content", Card.DEFAULT_CONTENT, "plaintext")
# #         w1.editor.add_tab("ML Biomarker Split", json.dumps(Pie.DEFAULT_DATA, indent=2), "json")

# #     else:
#     w1 = state.w1 
#     with elements("demo2"):
#         with w1.dashboard(rowHeight=50):
#             HtmlFile = open("mg_dx_to_3l_cluster1.html", 'r', encoding='utf-8')
#             st.markdown("""For Expanded View click here: <a href="http://10.229.61.93:8888/view/wayfinder/streamlit/Data/Cluster1_extension.html" target = "_blank"> Archetype 1 </a>""", unsafe_allow_html=True)
#             source_code = HtmlFile.read() 
#             components.html(source_code, height = 200)

    st.subheader('What are the key attributes of the patients ?')       
    col1, col2 = st.columns(2)

    with col1:
        # CSS to inject contained in a string
        hide_table_row_index = """
                <style>
                tbody th {display:none}
                .blank {display:none}
                </style>
                """

        # Inject CSS with Markdown
        st.markdown(hide_table_row_index, unsafe_allow_html=True)
        st.subheader('Demographics')
        st.table(demo[demo['Demographics'].isin(['Age','Gender(Male)'])].reset_index(drop=True).style.format({"Archetype 1": "{:.1f}%", "Archetype 2": "{:.1f}%","Archetype 3": "{:.1f}%","Archetype 4": "{:.1f}%"}, subset=pd.IndexSlice[demo[demo['Demographics']=='Gender(Male)'].index, :]).format({"Archetype 1": "{:.1f}", "Archetype 2": "{:.1f}","Archetype 3": "{:.1f}","Archetype 4": "{:.1f}"}, subset=pd.IndexSlice[demo[demo['Demographics']=='Age'].index, :]).background_gradient(cmap=cmap_cf, axis=1).set_table_styles([dict(selector="th", props=[('color', 'black'),])]))

        st.subheader('Comorbidities')
        st.table(demo[~(demo['Demographics'].isin(['Age','Gender(Male)','Gender(Female)']))].reset_index(drop=True).style.format({"Archetype 1": "{:.1f}%", "Archetype 2": "{:.1f}%","Archetype 3": "{:.1f}%","Archetype 4": "{:.1f}%"}).background_gradient(cmap=cmap_cf, axis=1).set_table_styles([dict(selector="th", props=[('color', 'black'),])]))


    with col2:
        st.text(" ")
        st.text(" ")
        st.text(" ")
        st.text(" ")
        st.text(" ")

        d = st.selectbox("Select Demographics", tuple(demo_data.columns[2:]))
        if d == 'Age':
            fig = px.box(demo_data, x="Archetype", y="Age", color='Archetype',
                 notched=True, color_discrete_map = {'Archetype 1':'#92D0AA', 'Archetype 2':'#4B9ABB', 'Archetype 3':'#F2E394', 'Archetype 4':'#EC5923'}, height=600,category_orders={'Archetype':['Archetype 1','Archetype 2','Archetype 3','Archetype 4']})
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig = px.bar(comorbidity_data, x='Archetype', y=d, color='Archetype', color_discrete_map = {'Archetype 1':'#92D0AA', 'Archetype 2':'#4B9ABB', 'Archetype 3':'#F2E394', 'Archetype 4':'#EC5923'},
                        category_orders={'Archetype':['Archetype 1','Archetype 2','Archetype 3','Archetype 4']}, height=600)
            fig.update_layout(title='% Patients per Cluster')
            fig.update_layout(title_font_size=30)
            fig.update_layout(title_pad_l=270)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("""<hr style="height:1px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

    st.subheader('What are the key events across the patient clusters?')


    metrics = st.selectbox('Select Metrics', tuple(data['metrics'].unique()))

    # with col2:
    #     if metrics == 'Prevalence':
    #         sort = st.selectbox('Sort by...', tuple(data[data['metrics']=='Prevalence']['cluster'].unique()))
    #     else:
    #         sort = st.selectbox('Sort by...', tuple(data[~(data['metrics']=='Prevalence')]['cluster'].unique()))


    with st.expander("Diagnosis", expanded=True):

        if metrics == 'Prevalence':
            col1, col2 = st.columns(2)
            with col1:
    #             st.table(data.head())
                distribution = pd.pivot_table(data[(data['metrics']==metrics)&(data['data_type']=='Diagnosis')], index='.Archetype.', columns='Archetype').reset_index()
                distribution.columns = distribution.columns.get_level_values(1)
                distribution.fillna(0, inplace=True)
        #         distribution = distribution.sort_values(by=str(sort) ,ascending=False).reset_index(drop=True)

                cmap = clr.LinearSegmentedColormap.from_list('custom', ['#FFFFFF','#FF7F50'], N=256)

                for col in distribution.columns.tolist()[1:]:
                    distribution[col] = distribution[col].apply(lambda x: round(x*100, 1))

                    # CSS to inject contained in a string
                hide_table_row_index = """
                        <style>
                        tbody th {display:none}
                        .blank {display:none}
                        </style>
                        """

                # Inject CSS with Markdown
                st.markdown(hide_table_row_index, unsafe_allow_html=True)            
                st.dataframe(distribution.style.format({"Archetype 1": "{:.1f}%", "Archetype 2": "{:.1f}%","Archetype 3": "{:.1f}%","Archetype 4": "{:.1f}%", "Overall": "{:.1f}%"}).background_gradient(cmap=cmap_cf, axis=1, subset=distribution.filter(regex='Archetype').columns.tolist()).set_table_styles([dict(selector="th", props=[('font-size', '12px'),('color', 'black'),])]), height=500)
            with col2:
                prev_plot = pd.pivot(data[(data['metrics']==metrics)&(data['data_type']=='Diagnosis')], index='.Archetype.', columns='Archetype', values='value').reset_index().T.reset_index()
                prev_plot.columns = prev_plot.iloc[0]
                prev_plot = prev_plot.iloc[1:,:]

                event = st.selectbox('Select Event', tuple(prev_plot.columns.tolist()[1:]))

                fig = px.bar(prev_plot[~(prev_plot['.Archetype.']=='Overall')], x='.Archetype.', y=event, color='.Archetype.', color_discrete_map = {'Archetype 1':'#92D0AA', 'Archetype 2':'#4B9ABB', 'Archetype 3':'#F2E394', 'Archetype 4':'#EC5923'},
                            category_orders={'Archetype':['Archetype 1','Archetype 2','Archetype 3','Archetype 4']}, height=500)
                fig.update_layout(title='Event Patient Prevalence')
                fig.update_layout(title_font_size=30)
                fig.update_layout(title_pad_l=270)
                st.plotly_chart(fig, use_container_width=True)
                pass

        else:
            distribution = pd.pivot_table(data[(data['metrics']==metrics)&(data['data_type']=='Diagnosis')], index='.Archetype.', columns='Archetype').reset_index()
            distribution.columns = distribution.columns.get_level_values(1)
            distribution.fillna(0, inplace=True)
    #         distribution = distribution.sort_values(by=str(sort) ,ascending=False).reset_index(drop=True)

            cmap = clr.LinearSegmentedColormap.from_list('custom', ['#FFFFFF','#FF7F50'], N=256)
            # CSS to inject contained in a string
            hide_table_row_index = """
                    <style>
                    tbody th {display:none}
                    .blank {display:none}
                    </style>
                    """

            # Inject CSS with Markdown
            st.markdown(hide_table_row_index, unsafe_allow_html=True)
            st.dataframe(distribution.style
                    .format({"Archetype 1": "{:.1f}", "Archetype 2": "{:.1f}","Archetype 3": "{:.1f}","Archetype 4": "{:.1f}", "Overall": "{:.1f}", "Standard Deviation": "{:.2f}"}).background_gradient(cmap=cmap_cf, axis=1, subset=distribution.filter(regex='Archetype').columns.tolist()).set_table_styles([dict(selector="th", props=[('font-size', '12px'),('color', 'white'),])]), height=500, width=1500)

    #--------------------------------------------------------------------------
    with st.expander("Procedure"):

        if metrics == 'Prevalence':
            col1, col2 = st.columns(2)
            with col1:
                distribution = pd.pivot_table(data[(data['metrics']==metrics)&(data['data_type']=='Procedure')], index='.Archetype.', columns='Archetype').reset_index()
                distribution.columns = distribution.columns.get_level_values(1)
                distribution.fillna(0, inplace=True)
        #         distribution = distribution.sort_values(by=str(sort) ,ascending=False).reset_index(drop=True)

                cmap = clr.LinearSegmentedColormap.from_list('custom', ['#FFFFFF','#FF7F50'], N=256)

                for col in distribution.columns.tolist()[1:]:
                    distribution[col] = distribution[col].apply(lambda x: round(x*100, 1))
                # CSS to inject contained in a string
                hide_table_row_index = """
                        <style>
                        tbody th {display:none}
                        .blank {display:none}
                        </style>
                        """

                # Inject CSS with Markdown
                st.markdown(hide_table_row_index, unsafe_allow_html=True)
                st.dataframe(distribution.style.format({"Archetype 1": "{:.1f}%", "Archetype 2": "{:.1f}%","Archetype 3": "{:.1f}%","Archetype 4": "{:.1f}%", "Overall": "{:.1f}%"}).background_gradient(cmap=cmap_cf, axis=1, subset=distribution.filter(regex='Archetype').columns.tolist()), height=500)
            with col2:
                prev_plot = pd.pivot(data[(data['metrics']==metrics)&(data['data_type']=='Procedure')], index='.Archetype.', columns='Archetype', values='value').reset_index().T.reset_index()
                prev_plot.columns = prev_plot.iloc[0]
                prev_plot = prev_plot.iloc[1:,:]

                event = st.selectbox('Select Event', tuple(prev_plot.columns.tolist()[1:]))

                fig = px.bar(prev_plot[~(prev_plot['.Archetype.']=='Overall')], x='.Archetype.', y=event, color='.Archetype.', color_discrete_map = {'Archetype 1':'#92D0AA', 'Archetype 2':'#4B9ABB', 'Archetype 3':'#F2E394', 'Archetype 4':'#EC5923'},
                            category_orders={'Archetype':['Archetype 1','Archetype 2','Archetype 3','Archetype 4']}, height=500)
                fig.update_layout(title='Event Patient Prevalence')
                fig.update_layout(title_font_size=30)
                fig.update_layout(title_pad_l=270)
                st.plotly_chart(fig, use_container_width=True)

        else:
            distribution = pd.pivot_table(data[(data['metrics']==metrics)&(data['data_type']=='Procedure')], index='.Archetype.', columns='Archetype').reset_index()
            distribution.columns = distribution.columns.get_level_values(1)
            distribution.fillna(0, inplace=True)
    #         distribution = distribution.sort_values(by=str(sort) ,ascending=False).reset_index(drop=True)

            cmap = clr.LinearSegmentedColormap.from_list('custom', ['#FFFFFF','#FF7F50'], N=256)
            # CSS to inject contained in a string
            hide_table_row_index = """
                    <style>
                    tbody th {display:none}
                    .blank {display:none}
                    </style>
                    """

            # Inject CSS with Markdown
            st.markdown(hide_table_row_index, unsafe_allow_html=True)    
            st.dataframe(distribution.style.format({"Archetype 1": "{:.1f}", "Archetype 2": "{:.1f}","Archetype 3": "{:.1f}","Archetype 4": "{:.1f}", "Overall": "{:.1f}", "Standard Deviation": "{:.2f}"})
                    .background_gradient(cmap=cmap_cf, axis=1, subset=distribution.filter(regex='Archetype').columns.tolist()).set_table_styles([dict(selector="th", props=[('font-size', '12px'),('color', 'black'),])]), height=500, width=1500)

    #--------------------------------------------------------------------------

    with st.expander("Treatment"):


        if metrics == 'Prevalence':
            col1, col2 = st.columns(2)
            with col1:
                distribution = pd.pivot_table(data[(data['metrics']==metrics)&(data['data_type']=='Treatment')], index='.Archetype.', columns='Archetype').reset_index()
                distribution.columns = distribution.columns.get_level_values(1)
                distribution.fillna(0, inplace=True)
        #         distribution = distribution.sort_values(by=str(sort) ,ascending=False).reset_index(drop=True)

                cmap = clr.LinearSegmentedColormap.from_list('custom', ['#FFFFFF','#FF7F50'], N=256)

                for col in distribution.columns.tolist()[1:]:
                    distribution[col] = distribution[col].apply(lambda x: round(x*100, 1))
                # CSS to inject contained in a string
                hide_table_row_index = """
                        <style>
                        tbody th {display:none}
                        .blank {display:none}
                        </style>
                        """

                # Inject CSS with Markdown
                st.markdown(hide_table_row_index, unsafe_allow_html=True)
                st.dataframe(distribution.style.format({"Archetype 1": "{:.1f}%", "Archetype 2": "{:.1f}%","Archetype 3": "{:.1f}%","Archetype 4": "{:.1f}%", "Overall": "{:.1f}%"}).background_gradient(cmap=cmap_cf, axis=1, subset=distribution.filter(regex='Archetype').columns.tolist()).set_table_styles([dict(selector="th", props=[('font-size', '12px'),('color', 'black'),])]), height=500)
            with col2:
                prev_plot = pd.pivot(data[(data['metrics']==metrics)&(data['data_type']=='Treatment')], index='.Archetype.', columns='Archetype', values='value').reset_index().T.reset_index()
                prev_plot.columns = prev_plot.iloc[0]
                prev_plot = prev_plot.iloc[1:,:]

                event = st.selectbox('Select Event', tuple(prev_plot.columns.tolist()[1:]))

                fig = px.bar(prev_plot[~(prev_plot['.Archetype.']=='Overall')], x='.Archetype.', y=event, color='.Archetype.', color_discrete_map = {'Archetype 1':'#92D0AA', 'Archetype 2':'#4B9ABB', 'Archetype 3':'#F2E394', 'Archetype 4':'#EC5923'},
                            category_orders={'Archetype':['Archetype 1','Archetype 2','Archetype 3','Archetype 4']}, height=500)
                fig.update_layout(title='Event Patient Prevalence')
                fig.update_layout(title_font_size=30)
                fig.update_layout(title_pad_l=270)
                st.plotly_chart(fig, use_container_width=True)

        else:
            distribution = pd.pivot_table(data[(data['metrics']==metrics)&(data['data_type']=='Treatment')], index='.Archetype.', columns='Archetype').reset_index()
            distribution.columns = distribution.columns.get_level_values(1)
            distribution.fillna(0, inplace=True)
    #         distribution = distribution.sort_values(by=str(sort) ,ascending=False).reset_index(drop=True)

            cmap = clr.LinearSegmentedColormap.from_list('custom', ['#FFFFFF','#FF7F50'], N=256)
            # CSS to inject contained in a string
            hide_table_row_index = """
                    <style>
                    tbody th {display:none}
                    .blank {display:none}
                    </style>
                    """

            # Inject CSS with Markdown
            st.markdown(hide_table_row_index, unsafe_allow_html=True)
            st.dataframe(distribution.style.format({"Archetype 1": "{:.1f}", "Archetype 2": "{:.1f}","Archetype 3": "{:.1f}","Archetype 4": "{:.1f}", "Overall": "{:.1f}", "Standard Deviation": "{:.2f}"})
                    .background_gradient(cmap=cmap_cf, axis=1, subset=distribution.filter(regex='Cluster').columns.tolist()).set_table_styles([dict(selector="th", props=[('font-size', '12px'),('color', 'black'),])]), height=500, width=1500)

app.run()