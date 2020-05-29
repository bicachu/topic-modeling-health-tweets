import base64
import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import plotly.graph_objects as go

from dash.dependencies import Input, Output, State

# Define styles and local images
external_stylesheets = ['assets/style.css']
img_logo = 'assets/img/twitter_logo_blk.png'
git_logo = 'assets/img/github_logo.png'
encoded_image_twt = base64.b64encode(open(img_logo, 'rb').read())
encoded_image_git = base64.b64encode(open(git_logo, 'rb').read())
# Initialize the app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Load data using number of topics as indices
df = pd.read_pickle(r'data/sttm_all_topics.pkl')

# Load data for words in each topic and corresponding scores
topic_words_df = pd.read_pickle(r'data/topic_words.pkl')

# Load data for topic name descriptions
topic_names_df = pd.read_pickle(r'data/topic_names.pkl')

# Convert date to datetime
df['date'] = pd.to_datetime(df['date'], errors='coerce')
# Add column for year
df['year'] = df['date'].dt.year

# Make a copy of data frames
dfc = df.copy()
topic_words_dfc = topic_words_df.copy()
topic_names_dfc = topic_names_df.copy()


def get_options(options):
    """
    returns a list of dictionaries, which have keys 'label' and 'value'
    (to use with dropdown selections)
    """
    dict_list = []
    for i in sorted(options, reverse=False):
        dict_list.append({'label': i, 'value': i})

    return dict_list


def get_marks(years_list):
    """
    returns dictionary of range marks, which have keys 'label' and 'value'
    (to use with range slider selections)
    """
    marks_dict = {}
    for val in years_list:
        marks_dict[val] = {'label': str(val),
                           'style': {'color': '#E4E4E4'}}
    return marks_dict


def get_filtered_df(df, num_topics):
    """
    returns a filtered data frame based on number of topics
    """
    return df[df['num_topics'] == num_topics]


def convert_list_to_string(lst):
    """
    returns a single concatenated string from a list of strings
    """
    s = ', '.join(lst)
    return s


def get_words_from_dict(d, num_words, index):
    """
    returns a list of lists containing each topic's top n-words
    num_words must be a value less than or equal to 10
    """
    top_words_list = [d[index][val][0] for val in range(0, num_words)]
    top_words = convert_list_to_string(top_words_list)
    return top_words


# Default and filter dfs to model with 10 topics
dfc = dfc.loc[10]
topic_words_dfc = topic_words_dfc[topic_words_dfc['num_clusters'] == 10]
topic_names_dfc = topic_names_dfc[topic_names_dfc['num_topics'] == 10]

# Create bubble chart of words in each topic
bubble_figure = go.Figure()

trace_default_visibilities = []  # create a list to specify which topics to display by default

for topic_num in topic_words_dfc.topic_num.values:
    filtered_df = topic_words_dfc[topic_words_dfc['topic_num'] == topic_num]
    if topic_num == 0:
        trace_default_visibilities.append(True)
    else:
        trace_default_visibilities.append('legendonly')

    bubble_figure.add_trace(go.Scatter(
        name=str(topic_num + 1),
        x=filtered_df.iloc[0]['doc_count'][0:5],
        y=filtered_df.iloc[0]['word_importance'][0:5],
        mode='markers+text',
        opacity=0.6,
        hovertext=filtered_df.iloc[0]['top_words'][0:5],
        hoverlabel=dict(font=dict(color='#FFFFFF')),
        marker=dict(
            size=filtered_df.iloc[0]['num_topic_occurence'][0:5],
            sizemode='area',
            sizeref=2. * max(filtered_df.iloc[0]['num_topic_occurence'][0:5]) / (40. ** 2),
            sizemin=4
        ),
        text=filtered_df.iloc[0]['top_words'][0:5],
        textposition='bottom center',
        visible=trace_default_visibilities[topic_num])
    )

    bubble_figure.update_layout(
        margin=dict(t=15, b=0, l=20, r=0),
        xaxis=dict(title='Tweet Count',
                   showgrid=False),
        yaxis=dict(title='Word Importance',
                   showgrid=False),
        font=dict(color='white'),
        legend=dict(
            itemsizing='constant',
            title=dict(text='   Topic #')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

# Create a global variable to store trace visibilities and access from functions
global_trace_visibilities = trace_default_visibilities.copy()

# Create data table of topic descriptions
topic_desc_df = pd.DataFrame(data=[topic_names_dfc.topic_names.iloc[0].keys(),
                                   topic_names_dfc.topic_names.iloc[0].values()]).T
topic_desc_df.columns = ['Topic', 'Description']
topic_desc_df['Topic'] += 1  # increment topic # so there is not a 'topic 0'

n_topics = len(dfc['dominant_topic'].unique())  # get number of topics
years_range = dfc['year'].unique()  # create list of years range
news_sources = dfc['username'].unique()  # create list of new sources

# Create pivot table of users vs topics
user_topic_counts = pd.pivot_table(data=dfc,
                                   values='name',
                                   index='username',
                                   columns='dominant_topic',
                                   aggfunc='count',
                                   fill_value=0)

user_topic_counts.columns = ['Topic {}'.format(i) for i in range(1, n_topics + 1)]
user_topic_counts['total_topics'] = user_topic_counts.sum(axis=1)  # add column to sum total topics
# Convert topic counts to percentages for each user
user_topic_counts_ratio = user_topic_counts.apply(lambda x: (x / user_topic_counts['total_topics']))
user_topic_counts_ratio = user_topic_counts_ratio.drop(columns=['total_topics'])

# Create pivot table of years vs topics
year_topic_counts = pd.pivot_table(data=dfc,
                                   values='date',
                                   index='year',
                                   columns='dominant_topic',
                                   aggfunc='count',
                                   fill_value=0)
year_topic_counts.columns = ['Topic {}'.format(i) for i in range(1, n_topics + 1)]

nav_tab_selected_style = {
    'backgroundColor': '#434140',
    'padding': '1px'
}
tab_selected_style = {
    'backgroundColor': '#31302F',
    'padding': '1px'
}

# Define Dash's HTML Index Template
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Health Tweets Dashboard</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Define the app
app.layout = html.Div(
    children=[
        html.Div(
            id='top-bar',
            className='top-bar',
            children=[
                html.Img(
                    src='data: image/png;base64,{}'.format(encoded_image_twt.decode()),
                    height='50vh'),
                html.H3('Short Text Topic Modeling on Health-Related Tweets Dashboard'),
                html.Caption(
                    children=[
                        html.A(
                            children=[
                                html.Img(src='data: image/png;base64,{}'.format(encoded_image_git.decode()),
                                         height='25vh')],
                            href='https://github.com/bicachu/topic-modeling-health-tweets')
                    ])
            ]),
        html.Div(
            className='body',
            children=[
                html.Div(
                    className='three columns',
                    children=[
                        html.Div(
                            className='nav-panel bg-lightgrey',
                            children=[
                                dcc.Tabs(
                                    className='control-tabs bg-lightgrey',
                                    id='tabs-nav-bar',
                                    children=[
                                        dcc.Tab(
                                            label='About',
                                            className='control-tab',
                                            selected_className='control-tab--selected selected-left',
                                            selected_style=nav_tab_selected_style,
                                            children=[
                                                html.Div(className='nav-content bg-lightgrey',
                                                         children=[
                                                             html.H6('Project Overview'),
                                                             html.P(
                                                                 'This project explores health-specific tweets from '
                                                                 'Twitter news sources, both domestic and global, '
                                                                 'using unsupervised machine learning methods like '
                                                                 'topic modeling. The objective is to identify '
                                                                 'patterns, trends, and topic concentrations across '
                                                                 'time and across different news sources that can lead '
                                                                 'to insights and drive action from businesses, '
                                                                 'pharmaceutical companies, and other stakeholders in '
                                                                 'the health industry.'),
                                                             html.P(
                                                                 'The most commonly used model for topic modeling is '
                                                                 'the Latent Dirichlet Allocation (LDA) model. However,'
                                                                 ' it does not handle short texts, like tweets, '
                                                                 'well. A better model was used which is a Gibbs '
                                                                 'Sampling Dirichlet Multinomial Mixture (GSDMM). It '
                                                                 'is designed to handle a corpus where each document '
                                                                 'has less than 50 words. It is similar to LDA with '
                                                                 'the key difference being that it assumes that a '
                                                                 'document belongs completely to a single topic, '
                                                                 'addressing the overlapping concerns that LDA can '
                                                                 'lead to.'

                                                             ),
                                                             html.P(
                                                                 "In the 'Figures' Tab, you can understand the data "
                                                                 'behind each visual figure and how the filters '
                                                                 'impact them.'
                                                             ),
                                                             html.P("In the 'Explore' Tab, you can change the number "
                                                                    'of topics, news sources, and year ranges to '
                                                                    'explore the results of the topic modeling. The '
                                                                    'corresponding heat maps/bubble plots will update '
                                                                    'accordingly.'
                                                                    )
                                                         ])
                                            ]),
                                        dcc.Tab(
                                            label='Figures',
                                            className='control-tab bg-lightgrey',
                                            selected_className='control-tab--selected',
                                            selected_style=nav_tab_selected_style,
                                            children=[
                                                html.Div(className='nav-content bg-lightgrey',
                                                         children=[
                                                             html.H6('Figures Overview'),
                                                             html.P(
                                                                 'To make the topics generated by the models humanly '
                                                                 'interpretable, it is helpful to view the top 10 '
                                                                 'distributed words in each topic. Using the top '
                                                                 'words, the topic descriptions were manually defined '
                                                                 'for each model respectively. Each k-topic model has '
                                                                 'its own unique set of k topic descriptions. Changing '
                                                                 'the number of news sources or year range criteria '
                                                                 'does not affect the topic descriptions.'
                                                             ),
                                                             html.P(
                                                                 'For each topic, the top 5 words can be viewed in the '
                                                                 'bubble chart. The tweet count represents the number '
                                                                 'of tweets that the word appears in and the word '
                                                                 'importance represents its proportion within the '
                                                                 'topic. The size of the bubbles increase relative to '
                                                                 'one another as the number of other topics in that '
                                                                 'model share the same word in their top ten words. '
                                                                 'Therefore, words with smaller bubble diameters are '
                                                                 'more reflective and highly specific to that '
                                                                 'particular topic. '
                                                             ),
                                                             html.P(
                                                                 'The sources heatmap represents the proportion of '
                                                                 'tweets that belong to each particular topic for the '
                                                                 'respective news source. Similarly, the years heatmap '
                                                                 'represents the total count of tweets that belong to '
                                                                 'each topic for that given calendar year. Changing '
                                                                 'the number of topics, news sources, and years range '
                                                                 'will all change the heatmaps as well.'
                                                             )])
                                            ]),
                                        dcc.Tab(
                                            label='Explore',
                                            className='control-tab bg-lightgrey',
                                            selected_className='control-tab--selected selected-right',
                                            selected_style=nav_tab_selected_style,
                                            children=[
                                                html.Div(
                                                    className='div-for-dropdown bg-lightgrey',
                                                    children=[
                                                        html.H5('Number of Topics:'),
                                                        dcc.Dropdown(
                                                            id='topics-selector',
                                                            className='div-for-dropdown',
                                                            clearable=False,
                                                            options=get_options(
                                                                df.index.unique()),
                                                            value=10,
                                                            placeholder='Select number of topics'),
                                                        html.H5('Years Range: '),
                                                        dcc.RangeSlider(
                                                            id='date-range-slider',
                                                            updatemode='mouseup',
                                                            allowCross=True,
                                                            min=year_topic_counts.index.min(),
                                                            max=year_topic_counts.index.max(),
                                                            marks=get_marks(
                                                                year_topic_counts.index.unique()),
                                                            value=[
                                                                year_topic_counts.index.min(),
                                                                year_topic_counts.index.max()
                                                            ]),
                                                        html.H5('News Sources:'),
                                                        dcc.Dropdown(
                                                            id='news-selector',
                                                            className='news-selector',
                                                            options=get_options(
                                                                df['name'].unique()),
                                                            multi=True,
                                                            value=df['name'].unique(),
                                                            searchable=False,
                                                            placeholder='No Sources Selected'),
                                                        html.Br(),
                                                    ]),
                                            ]),
                                    ]),
                            ])
                    ]),
                html.Div(
                    className='five-custom columns',
                    children=[
                        html.Div(
                            className='div-for-topics',
                            children=[
                                dash_table.DataTable(
                                    id='topic-table',
                                    data=topic_desc_df.to_dict('records'),
                                    columns=[{'id': c, 'name': c}
                                             for c in topic_desc_df.columns],
                                    fixed_rows={'headers': True},
                                    tooltip_data=[
                                        {
                                            'Description': 'Top 5 words: ' + get_words_from_dict(
                                                get_filtered_df(topic_names_dfc,
                                                                len(topic_desc_df)).iloc[0]['top_words'], 5,
                                                topic_num)
                                        }
                                        for topic_num in range(0, 10)
                                    ],
                                    style_as_list_view=True,
                                    style_table={
                                        'height': '26vh',
                                        'width': '20vw',
                                        'overflowY': 'auto',
                                        'border': '1px solid white'
                                    },
                                    style_header={
                                        'color': '#FFFFFF',
                                        'fontWeight': 'bold',
                                        'backgroundColor': 'rgba(126, 124, 124, 0.5)',
                                        'borderTop': '0px',
                                        'padding': '2px',
                                        'width': '20%'

                                    },
                                    style_cell={
                                        'backgroundColor': 'rgb(50, 50, 50)',
                                    },
                                    style_data={
                                        'fontSize': 10,
                                        'fontWeight': 'normal',
                                    },
                                    style_data_conditional=[],
                                    style_cell_conditional=[
                                        {
                                            'if': {'column_id': 'Topic'},
                                            'width': '20%',
                                            'textAlign': 'center',
                                        },
                                    ],
                                    css=[
                                        {  # override default css for selected/focused table cells
                                            'selector': 'td.cell--selected, td.focused',
                                            'rule': 'background-color: rgba(54, 134, 255, 0.25) !important;'
                                        },
                                        {
                                            'selector': 'td.cell--selected *, td.focused *',
                                            'rule': 'color: #FFFFFF !important;',
                                        }
                                    ]
                                )
                            ]),
                        html.Div(
                            dcc.Loading(
                                id='bubble-load',
                                color='rgb(66, 141, 252)',
                                children=[
                                    dcc.Graph(
                                        id='bubble-plot',
                                        figure=bubble_figure,
                                    )]),
                            className='div-for-bubble')
                    ]),
                html.Div(
                    className='four-custom columns',
                    children=[
                        html.Div(className='heatmap-panel',
                                 children=[
                                     dcc.Tabs(
                                         className='heatmap-tabs-container',
                                         parent_className='heatmap-tabs',
                                         id='heatmap-tabs',
                                         children=[
                                             dcc.Tab(
                                                 label='Sources',
                                                 className='heatmap-tab bg-lightgrey',
                                                 selected_className='heatmap-tab--selected bg-lightgrey',
                                                 selected_style=tab_selected_style,
                                                 children=[
                                                     dcc.Loading(
                                                         id='heatmap-news',
                                                         color='rgb(66, 141, 252)',
                                                         children=[
                                                             html.Div(
                                                                 dcc.Graph(
                                                                     figure={
                                                                         'data': [go.Heatmap(
                                                                             x=user_topic_counts_ratio.columns.tolist(),
                                                                             y=user_topic_counts_ratio.index.tolist(),
                                                                             z=user_topic_counts_ratio.values.tolist(),
                                                                             colorscale='YlGnBu',
                                                                             colorbar=dict(
                                                                                 thickness=20,
                                                                                 xpad=5))],
                                                                         'layout': go.Layout(
                                                                             autosize=True,
                                                                             margin=dict(l=106, r=0, b=50, t=10,
                                                                                         pad=2),
                                                                             xaxis=dict(
                                                                                 tickangle=-30,
                                                                                 tickcolor='#FFFFFF'),
                                                                             yaxis=dict(
                                                                                 tickcolor='#FFFFFF'),
                                                                             font=dict(color='white'),
                                                                             paper_bgcolor='rgba(0,0,0,0)',
                                                                             plot_bgcolor='rgba(0,0,0,0)',
                                                                         )}
                                                                 ),
                                                                 className='div-for-heatmaps'
                                                             )
                                                         ])
                                                 ]),
                                             dcc.Tab(
                                                 label='Years',
                                                 className='heatmap-tab bg-lightgrey',
                                                 selected_className='heatmap-tab--selected bg-lightgrey',
                                                 selected_style=tab_selected_style,
                                                 children=[
                                                     dcc.Loading(
                                                         id='heatmap-years',
                                                         color='rgb(66, 141, 252)',
                                                         children=[
                                                             html.Div(
                                                                 dcc.Graph(
                                                                     figure={
                                                                         'data': [go.Heatmap(
                                                                             x=year_topic_counts.columns.tolist(),
                                                                             y=year_topic_counts.index.tolist(),
                                                                             z=year_topic_counts.values.tolist(),
                                                                             colorscale='YlGnBu',
                                                                             colorbar=dict(
                                                                                 thickness=20,
                                                                                 xpad=5))],
                                                                         'layout': go.Layout(
                                                                             xaxis=dict(
                                                                                 tickangle=-30,
                                                                                 tickcolor='#FFFFFF'),
                                                                             yaxis=dict(
                                                                                 type='category',
                                                                                 tickcolor='#FFFFFF',
                                                                                 tickmode='array',
                                                                                 tickvals=year_topic_counts.index.tolist(),
                                                                                 ticktext=year_topic_counts.index.tolist(),
                                                                                 autorange='reversed'),
                                                                             autosize=True,
                                                                             margin=dict(l=104, r=0, b=50, t=10,
                                                                                         pad=2),
                                                                             font=dict(color='#FFFFFF'),
                                                                             paper_bgcolor='rgba(0,0,0,0)',
                                                                             plot_bgcolor='rgba(0,0,0,0)',
                                                                         )}
                                                                 ),
                                                                 className='div-for-heatmaps'
                                                             )
                                                         ])
                                                 ])
                                         ])
                                 ])
                    ]),
                html.Div(
                    id='hidden-div',  # Hidden div to store global variable for traces visibility
                    style={'display': 'none'},
                    children=[
                        dcc.Store(
                            id='topic-trace-list',
                            data=global_trace_visibilities
                        )
                    ]
                )
            ])
    ])


# Callback for bubble chart update
@app.callback(Output('bubble-plot', 'figure'),
              [Input('topics-selector', 'value')])
def update_bubble_plot(selected_num_topics):
    topic_words_dfc = topic_words_df[topic_words_df['num_clusters'] == selected_num_topics]

    bubble_figure = go.Figure()

    trace_default_visibilities = []  # create a list to specify which topics to display by default

    for topic_num in topic_words_dfc.topic_num.values:
        filtered_df = topic_words_dfc[topic_words_dfc['topic_num'] == topic_num]
        if topic_num == 0:
            trace_default_visibilities.append(True)  # display first topic only on initialization
        else:
            trace_default_visibilities.append('legendonly')

        bubble_figure.add_trace(go.Scatter(
            name=str(topic_num + 1),
            x=filtered_df.iloc[0]['doc_count'][0:5],
            y=filtered_df.iloc[0]['word_importance'][0:5],
            mode='markers+text',
            opacity=0.6,
            hovertext=filtered_df.iloc[0]['top_words'][0:5],
            hoverlabel=dict(font=dict(color='#FFFFFF')),
            marker=dict(
                size=filtered_df.iloc[0]['num_topic_occurence'][0:5],
                sizemode='area',
                sizeref=2. * max(filtered_df.iloc[0]['num_topic_occurence'][0:5]) / (40. ** 2),
                sizemin=4
            ),
            text=filtered_df.iloc[0]['top_words'][0:5],
            textposition='bottom center',
            visible=trace_default_visibilities[topic_num])
        )

        bubble_figure.update_layout(
            autosize=True,
            margin=dict(t=18, b=0, l=10, r=0, pad=0),
            xaxis=dict(title='Tweet Count',
                       showgrid=False,
                       zeroline=False),
            yaxis=dict(title='Word Importance',
                       showgrid=False,
                       zeroline=False),
            font=dict(color='white'),
            legend=dict(
                itemsizing='constant',
                title=dict(text='   Topic #')),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )

    return bubble_figure


@app.callback(Output('topic-trace-list', 'data'),
              [Input('topics-selector', 'value'),
               Input('bubble-plot', 'restyleData')],
              [State('topic-trace-list', 'data')])
def refresh_traces_visibility(selected_num_topics, toggled_topic, traces):
    ctx = dash.callback_context

    input_changed = ctx.triggered[0]['prop_id']  # records which input component triggered the current callback
    global_trace_visibilities = traces

    if input_changed == 'topics-selector.value':
        topic_words_dfc = topic_words_df[topic_words_df['num_clusters'] == selected_num_topics]
        global_trace_visibilities = []  # reset traces
        for topic_num in topic_words_dfc.topic_num.values:
            if topic_num == 0:
                global_trace_visibilities.append(True)  # display first topic only on initialization
            else:
                global_trace_visibilities.append('legendonly')
    elif input_changed == 'bubble-plot.restyleData':
        for i in range(0, len(toggled_topic[1])):
            temp_topic_num = toggled_topic[1][i]  # topic refers to index here
            if toggled_topic[0]['visible'][i] == True:
                global_trace_visibilities[temp_topic_num] = True
            else:  # item is toggled off: toggled_topic[0]['visible'] == ['legendonly']:
                global_trace_visibilities[temp_topic_num] = 'legendonly'

    return global_trace_visibilities


# Callback for update topics display table
@app.callback([Output('topic-table', 'data'),
               Output('topic-table', 'columns'),
               Output('topic-table', 'tooltip_data')],
              [Input('topics-selector', 'value')])
def update_topic_descriptions(selected_num_topics):
    filtered_df = topic_names_df[topic_names_df['num_topics'] == selected_num_topics]  # filter for number of topics

    # Create data frame of topic descriptions
    topic_desc = pd.DataFrame(data=[filtered_df.topic_names.iloc[0].keys(),
                                    filtered_df.topic_names.iloc[0].values()]).T
    topic_desc.columns = ['Topic', 'Description']
    topic_desc['Topic'] += 1  # increment topic # so there is not a 'topic 0'

    data = topic_desc.to_dict('records')
    columns = [{'id': c, 'name': c} for c in topic_desc.columns]
    tooltip_data = [{
        'Description': 'Top 5 words: ' + get_words_from_dict(
            filtered_df.iloc[0]['top_words'],
            5, topic_num)
    }
        for topic_num in range(0, selected_num_topics)
    ]

    return data, columns, tooltip_data


# Callback for toggling topic descriptions based on bubble chart
@app.callback(Output('topic-table', 'style_data_conditional'),
              [Input('topic-trace-list', 'data')])
def update_topics_highlighted(traces):
    # Create temp list of all indices for traces selected
    selected_traces_idx = [i for i, val in enumerate(traces) if val is True]

    style_data_conditional = [
        {
            'if': {'filter_query': '{Topic} = ' + str(index + 1)},
            'color': 'rgb(66, 141, 252)',
            'fontWeight': 'bold'
        }
        for index in selected_traces_idx
    ]

    return style_data_conditional


# Callback for both heat maps
@app.callback([Output('heatmap-news', 'children'),
               Output('heatmap-years', 'children')],
              [Input('topics-selector', 'value'),
               Input('news-selector', 'value'),
               Input('date-range-slider', 'value')])
def update_heatmap(selected_num_topics, selected_sources_values, selected_range_values):
    n_topics = selected_num_topics
    if selected_sources_values is None or len(selected_sources_values) == 0:
        invalid_content = html.Div(
            'No news sources have been selected for the model  \
            analysis. \
            Please select at least one option from the dropdown.',
            style={
                'color': 'rgb(66, 141, 252)',
                'padding': '20px',
                'font-size': '20pt',
                'border': '1px solid lightgrey'
            }
        )
        return invalid_content, invalid_content

    years_range = [*range(selected_range_values[0], selected_range_values[1] + 1, 1)]  # create list of years range
    filtered_df = df[df.name.isin(selected_sources_values) & df.year.isin(years_range)]  # apply filters

    user_topic_counts = pd.pivot_table(data=filtered_df.loc[n_topics],
                                       values='name',
                                       index='username',
                                       columns='dominant_topic',
                                       aggfunc='count',
                                       fill_value=0)

    user_topic_counts.columns = ['Topic {}'.format(i) for i in range(1, n_topics + 1)]
    user_topic_counts['total_topics'] = user_topic_counts.sum(axis=1)  # add column to sum total topics

    # Convert topic counts to percentages for each news source
    user_topic_counts_ratio = user_topic_counts.apply(lambda x: (x / user_topic_counts['total_topics']))
    user_topic_counts_ratio = user_topic_counts_ratio.drop(columns=['total_topics'])

    year_topic_counts = pd.pivot_table(data=filtered_df.loc[n_topics],
                                       values='date',
                                       index='year',
                                       columns='dominant_topic',
                                       aggfunc='count',
                                       fill_value=0)
    year_topic_counts.columns = ['Topic {}'.format(i) for i in range(1, n_topics + 1)]

    # Store value z-values
    z_usr = user_topic_counts_ratio.values.tolist()
    z_yr = year_topic_counts.values.tolist()

    # Add topic names to heat map hover info
    filtered_topics = topic_names_df[topic_names_df['num_topics'] == n_topics]
    topic_names = [filtered_topics.topic_names.iloc[0][i] for i in range(0, n_topics)]
    hovertext_usr = []
    for yi, yy in enumerate(user_topic_counts_ratio.index.tolist()):
        hovertext_usr.append(list())
        for xi, xx in enumerate(topic_names):
            hovertext_usr[-1].append('<b>Source:</b> {}<br />'
                                     '<b>Topic:</b> {}<br />'
                                     '<b>Value:</b> {}'.format(yy, xx, z_usr[yi][xi]))
    hovertext_yr = []
    for yi, yy in enumerate(year_topic_counts.index.tolist()):
        hovertext_yr.append(list())
        for xi, xx in enumerate(topic_names):
            hovertext_yr[-1].append('<b>Year:</b> {}<br />'
                                    '<b>Topic:</b> {}<br />'
                                    '<b>Value:</b> {}'.format(yy, xx, z_yr[yi][xi]))

    graph1 = dcc.Graph(figure={'data': [go.Heatmap(
        x=user_topic_counts_ratio.columns.tolist(),
        y=user_topic_counts_ratio.index.tolist(),
        z=user_topic_counts_ratio.values.tolist(),
        colorscale='YlGnBu',
        colorbar=dict(
            thickness=20,
            xpad=5),
        text=hovertext_usr,
        hoverinfo='text')],
        'layout': go.Layout(
            autosize=True,
            margin=dict(l=106, r=0, b=50, t=10, pad=2),
            xaxis=dict(
                tickangle=-30,
                tickcolor='#FFFFFF'),
            yaxis=dict(
                tickcolor='#FFFFFF'),
            font=dict(color='white'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )})

    graph2 = dcc.Graph(figure={'data': [go.Heatmap(
        x=year_topic_counts.columns.tolist(),
        y=year_topic_counts.index.tolist(),
        z=year_topic_counts.values.tolist(),
        colorscale='YlGnBu',
        colorbar=dict(
            thickness=20,
            xpad=5),
        text=hovertext_yr,
        hoverinfo='text'
    )],
        'layout': go.Layout(
            xaxis=dict(
                tickangle=-30,
                tickcolor='#FFFFFF'),
            yaxis=dict(
                type='category',
                tickcolor='#FFFFFF',
                tickmode='array',
                tickvals=year_topic_counts.index.tolist(),
                ticktext=year_topic_counts.index.tolist(),
                autorange='reversed'),
            autosize=True,
            margin=dict(l=104, r=0, b=50, t=10, pad=2),
            font=dict(color='#FFFFFF'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )})

    return graph1, graph2


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
