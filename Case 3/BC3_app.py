### Business Case 3

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import dash_table
from dash_table import DataTable
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules

# importing the 4 datasets
products = pd.read_csv('datasets/products.csv')
departments = pd.read_csv('datasets/departments.csv')
orders = pd.read_csv('datasets/orders.csv')
order_products = pd.read_csv('datasets/order_products.csv')

# renaming a column in 'departments'
departments.columns = ['department_id', 'department_name']
# merging the different datasets in one
product_departments = pd.merge(products, departments, how='left', on='department_id').\
                        drop(["department_id"], axis=1)
order_product_departments = pd.merge(order_products, product_departments, how='left', on='product_id').\
                        drop(["product_id"], axis=1)
df = pd.merge(order_product_departments, orders, how='left', on='order_id')


df_prod_dept = pd.merge(products,departments, left_on="department_id", right_on="department_id")\
            .drop(columns=['product_id','department_id'])

department_dict={}
for dept in df_prod_dept['department_name'].unique():
    product_list = df_prod_dept[df_prod_dept['department_name'] == dept]['product_name'].values
    department_dict[dept] = product_list

############################################ components #####################################################

product_options = []
for i in df['product_name'].unique().tolist():
    product_options.append({'label': i, 'value':  i})

department_options = []
for i in df['department_name'].unique().tolist():
    department_options.append({'label': i, 'value':  i})

dropdown_product_1 = dcc.Dropdown(
        id='product1',
        options=product_options,
        value='fresh fruits'
    )

dropdown_product_2 = dcc.Dropdown(
        id='product2',
        options=product_options,
        value='fresh vegetables'
    )

dropdown_substitute = dcc.Dropdown(
    id='substitution',
    options=department_options,
    value='beverages'
    )

dropdown_product_recommendation = dcc.Dropdown(
    id='product_recommendation',
    options=product_options,
    value='bread'
    )


######################################## app itself #######################################################

app = dash.Dash(__name__)

server = app.server

app.layout = html.Div([

    html.H1('Market Basket Analysis: Instacart'),

    html.H4('Authors: Lorenzo Pigozzi, Nguyen Phuc, Ema Mandura, Xavier'),

    html.Br(),

    html.H2('Analysis by pair of products'),


    html.Div([
        html.Div([
            html.Label('Select Product 1'),
            dropdown_product_1
        ], style={'width': '50%'}, className='box'),

        html.Br(),

        html.Div([
            html.Label('Select Product 2'),
            dropdown_product_2
        ], style={'width': '50%'}, className='box')

    ], style={'display': 'flex'} ),



    html.Br(),

    html.Div([
        html.Div([
            dcc.Graph(id='graph_1'),
        ], style={'width': '40%'}, className='box'),

        html.Div([
            dcc.Graph(id='graph_3'),
        ], style={'width': '20%'}, className='box'),

        html.Div([
            dcc.Graph(id='graph_2'),
        ], style={'width': '40%'}, className='box'),

    ], style={'display': 'flex'}),

    html.Br(),
    html.Br(),
    html.Br(),

    html.H2('Top pair of substitute products by deparment'),

    html.Label('Select a department'),

    dropdown_substitute,

    DataTable(
        id='table1',
        data=[]
    ),


    html.Br(),
    html.Br(),


    html.H2('Recommendation System'),

    html.Label('Select a product'),

    dropdown_product_recommendation,

    html.Br(),
    html.Br(),

])

#################################################### callbacks ############################################

@app.callback(
    [Output('graph_1', 'figure'),
     Output('graph_2', 'figure'),
     Output('graph_3', 'figure')
     ],
    [Input('product1', 'value'),
     Input('product2', 'value')
     ]
)

def products_analysis(product1, product2):
    list_of_products = [product1, product2]

    ### plot 1
    df_for_plot = df.groupby(['product_name', 'order_hour_of_day']).size()
    df_for_plot = pd.DataFrame(df_for_plot).reset_index()
    df_for_plot.columns = ['product', 'hour_of_day', 'frequency']
    # manipulating the data with pivot table
    df_for_plot = pd.pivot_table(df_for_plot, values=['frequency'], columns=['product'], index=['hour_of_day'])
    # dropping the multi-index level for the columns
    df_for_plot.columns = df_for_plot.columns.droplevel(0)

    ##plotting##
    data_for_plot = [dict(type='scatter',
                          x=df_for_plot.index,
                          y=df_for_plot[product],
                          name=product)
                     for product in list_of_products
                     ]
    # setting the layout
    plot_1_layout = dict(title=dict(text='Frequency purchases per hour of the day'),
                         xaxis=dict(title='Hour of the day'),
                         yaxis=dict(title='Total Frequency')
                         )
    # displaying the graph
    plot_1 = go.Figure(data=data_for_plot, layout=plot_1_layout)

    ### plot 2
    df_for_plot = df.groupby(['product_name', 'order_dow']).size()
    df_for_plot = pd.DataFrame(df_for_plot).reset_index()
    df_for_plot.columns = ['product', 'order_dow', 'frequency']
    # manipulating the data with pivot table
    df_for_plot = pd.pivot_table(df_for_plot, values=['frequency'], columns=['product'], index=['order_dow'])
    # dropping the multi-index level for the columns
    df_for_plot.columns = df_for_plot.columns.droplevel(0)

    # labels_plot = {}
    ##plotting##
    data_for_plot = [dict(type='scatter',
                          x=df_for_plot.index,
                          y=df_for_plot[product],
                          name=product)
                     for product in list_of_products
                     ]
    # setting the layout
    plot_2_layout = dict(title=dict(text='Frequency purchases per day of the week'),
                         xaxis=dict(title='Day of the week'),
                         yaxis=dict(title='Total Frequency')
                         )
    # displaying the graph
    plot_2 = go.Figure(data=data_for_plot, layout=plot_2_layout)

    ### plot 3
    top_products = pd.DataFrame(df['product_name'].value_counts()).reset_index()
    top_products.columns = ['product_name', 'value']
    top_products = top_products[top_products['product_name'].isin(list_of_products)]
    plot_3 = px.bar(top_products, y='value', x='product_name', orientation='v',
                    color="product_name", color_discrete_sequence=px.colors.qualitative.Antique,
                    title='Quantity purchased')


    return plot_1, plot_2, plot_3



@app.callback(
    Output('table1', 'data'),
    Input('substitution', 'value')
)

def getRulesbyDept(department):
    new_df = df[df['product_name'].isin(department_dict[department])].copy()
    # Pivot the data - lines as orders and products as columns
    pt = pd.pivot_table(new_df, index='order_id', columns='product_name',
                        aggfunc=lambda x: 1 if len(x) > 0 else 0).fillna(0)
    # Apply the APRIORI algorithm to get frequent itemsets
    # Rules supported in at least 5% of the transactions (more info at http://rasbt.github.io/mlxtend/user_guide/frequent_patterns/apriori/)
    frequent_itemsets_by_dept = apriori(pt, min_support=0.01, use_colnames=True)

    # Generate the association rules - by lift
    rulesLift = association_rules(frequent_itemsets_by_dept, metric="lift", min_threshold=0.01)
    rulesLift.sort_values(by='lift', ascending=True, inplace=True)
    rulesLift.drop(["antecedent support", "consequent support", "support", "leverage", "conviction"], axis=1,
                   inplace=True)
    return rulesLift.head(1)

if __name__ == '__main__':
    app.run_server(debug=True)