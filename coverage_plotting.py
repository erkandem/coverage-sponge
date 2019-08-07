import math
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output,State
from coverage_sponge import engine_factory

engine = engine_factory()
fallback_dropdown_options = [{'label': 'Total', 'value': 'Total'}]


class ModuleSelection:
    def __init__(self, engine):
        self.engine = engine

    def get_options(self):
        data = self.execute_select_module()
        if len(data) > 0:
            obj = self.format_module_options(data)
        else:
            obj = self.default_obj()
        return obj

    def get_dropdown(self):
        obj = self.get_options()
        return self.generate_dropdown(obj)

    def get_submodule_options(self):
        data = self.get_submodules()
        if len(data) > 0:
            data = [[x] for x in data]
            obj = self.format_module_options(data)
        else:
            obj = self.default_obj()
        return obj

    def get_submodule_dropdown(self):
        obj = self.get_submodule_options()
        return self.generate_dropdown(obj)

    def select_modules(self) -> str:
        return '''SELECT DISTINCT module FROM coverage_data;'''

    def execute_select_module(self):
        with self.engine.connect() as con:
            sql = self.select_modules()
            curs = con.execute(sql)
            data = curs.fetchall()
        return data

    def get_submodules(self):
        data = [x[0] for x in self.execute_select_module()]
        splitted = [x.split('/') for x in data]
        unique_top2 = set([x[1] for x in splitted if len(x) > 1])
        reserved_names = {'Total', '__init__.py'}
        unique_top2 = list(unique_top2 - reserved_names)
        return unique_top2

    def get_submodule_to_module_map(self):
        data = [x[0] for x in ms.execute_select_module()]
        splitted = [x.split('/') for x in data]
        unique_top2 = set([x[1] for x in splitted if len(x) > 1])
        reserved_names = {'Total', '__init__.py'}
        unique_top2 = list(unique_top2 - reserved_names)
        module_map = {
            sub: ['/'.join(x) for x in splitted if len(x) > 1 and x[1] == sub]
            for sub in unique_top2
        }
        return module_map

    def format_module_options(self, data):
        return [{'label': x[0], 'value': x[0]} for x in data]

    def default_obj(self):
        return [{'label': 'Total', 'value': 'Total'}]

    def generate_dropdown(self, obj):
        return dcc.Dropdown(
            id='module-dropdown',
            options=obj
        )


class CoverageDataObj:
    def __init__(self, engine):
        self.engine = engine

    def get_formatted_data(self, module: str):
        data = self.get_module_data(module)
        if len(data) > 0:
            obj = self.format_coverage_data_for_plotting(data)
            return obj

    def get_formatted_submodule_data(self, submodule: str):
        data = self.get_submodule_data(submodule)
        if len(data) > 0:
            obj = self.format_coverage_data_for_plotting(data)
            return obj

    def get_plot(self, module: str):
        obj = self.get_formatted_data(module)
        fig = self.generate_plot(module, obj)
        return fig

    def get_submodule_plot(self, submodule: str):
        obj = self.get_formatted_submodule_data(submodule)
        fig = self.generate_plot(submodule, obj)
        return fig

    def select_module_data(self, module: str) -> str:
        return f'''
        SELECT 
            dt, 
            statements, 
            missing, 
            1.0 - (missing * 1.0) / (statements * 1.0) AS coverage
        FROM coverage_data 
        WHERE module = '{module}';
        '''

    def select_submodule_data(self, submodule: str):
        return f'''
        SELECT
            dt,
            sum(statements),
            sum(missing),
            1.0 - (sum(missing) * 1.0) / (sum(statements) * 1.0) AS coverage
        FROM coverage_data
        WHERE module LIKE '%/{submodule}/%'
        GROUP BY dt;'''

    def get_data(self,  sql: str):
        with self.engine.connect() as con:
            curs = con.execute(sql)
            data = curs.fetchall()
        return data

    def get_module_data(self, module: str):
        sql = self.select_module_data(module)
        data = self.get_data(sql)
        return data

    def get_submodule_data(self, submodule: str):
        sql = self.select_submodule_data(submodule)
        data = self.get_data(sql)
        return data

    def format_coverage_data_for_plotting(self, data):
        obj = {
            'x': [x[0] for x in data],
            'statements': [x[1] for x in data],
            'missing': [x[2] for x in data],
            'coverage': [x[3] for x in data]
        }
        return obj

    def default_obj(self):
        obj = {
            'x': [
                '2019-08-02T00:28:00', '2019-08-02T00:40:00',
                '2019-08-02T01:48:00', '2019-08-02T11:47:00',
                '2019-08-02T21:31:00', '2019-08-03T00:29:00',
                '2019-08-03T13:18:00', '2019-08-03T14:55:00',
                '2019-08-03T15:01:00', '2019-08-03T18:11:00',
                '2019-08-04T16:38:00', '2019-08-05T00:20:00',
                '2019-08-05T16:08:00', '2019-08-05T16:21:00',
                '2019-08-05T17:03:00', '2019-08-05T17:42:00',
                '2019-08-05T23:27:00', '2019-08-05T23:48:00',
                '2019-08-06T00:20:00'
            ],
            'statements': [
                4361, 4361, 4361, 4362,
                4362, 4371, 4371, 4373,
                4373, 4373, 4376, 4376,
                4376, 4376, 4376, 4351,
                4351, 4351, 4351
            ],
            'missing':  [
                4001, 3992, 3984, 3911,
                3911, 3917, 3840, 3706,
                3690, 3673, 3639, 3564,
                3529, 3483, 3474, 3451,
                3451, 3398, 3204
            ],
            'coverage': [
                0.08254987388213708, 0.08461362072919054,
                0.08644806237101588, 0.10339293901879876,
                0.10339293901879876, 0.10386639212994742,
                0.12148249828414548, 0.15252686942602334,
                0.15618568488451867, 0.16007317630916995,
                0.168418647166362, 0.18555758683729429,
                0.19355575868372943, 0.20406764168190128,
                0.2061243144424132, 0.20684900022983221,
                0.20684900022983221, 0.21903010802114453,
                0.2636175591817973
            ]
        }
        return obj

    def generate_plot(self, module: str, obj: {}):
        """map data to the visualization"""
        max_ = max(obj['statements'])
        if max_ == 0:
            upper_limit = 10
        else:
            x = math.floor(math.log10(max_))
            upper_limit = math.ceil(max_ / 10 ** x) * (10 ** x)
        coverage = {
                'mode': 'lines',
                'name': 'coverage',
                'x': obj['x'],
                'y': obj['coverage']
              }
        statements = {
                'mode': 'lines',
                'name': 'statements',
                'x': obj['x'],
                'y': obj['statements'],
                'yaxis': 'y2',
                'stackgroup': None
              }
        missing = {
                'mode': 'lines',
                'name': 'missing',
                'x': obj['x'],
                'y': obj['missing'],
                'yaxis': 'y2',
                'stackgroup': None
              }
        data = [go.Scatter(coverage), go.Scatter(statements), go.Scatter(missing)]
        layout = {
                'title': {'text': f"`{module}` Coverage'"},
                'xaxis': {
                  'type': 'date',
                  'title': {'text': '<br>'},
                  'autorange': True
                },
                'yaxis': {
                  'side': 'left',
                  'type': 'linear',
                  'range': [0, 1],
                  'nticks': 6,
                  'tickfont': {'color': 'rgb(31, 119, 180)'},
                  'autorange': False,
                  'tickformat': '.0%'
                },
                'legend': {
                  'x': 1.1166666666666667,
                  'y': 1.0888888888888888
                },
                'yaxis2': {
                  'side': 'right',
                  'type': 'linear',
                  'range': [0, upper_limit],
                  'autorange': False,
                  'overlaying': 'y'
                },
                'autosize': True
              }
        fig = go.Figure(data=data, layout=go.Layout(layout))
        return fig


co = CoverageDataObj(engine)
ms = ModuleSelection(engine)

names = ['Total']

layout = html.Div([
    html.H2('Welcome to the Coverage History'),
    html.Div([
        dcc.RadioItems(
            id='module-folder-radio-switch',
            options=[{'label': x, 'value': x} for x in ['per Module', 'per Folder']],
            value='per Module'
        )
    ], id='module-folder-radio-div'),
    html.Div([
        dcc.Dropdown(
            id='module-dropdown',
            options=fallback_dropdown_options,
            value='Total',
        )
    ], id='dropdown-div'),
    html.Div([
        dcc.Graph(
            id='coverage-graph',
            figure=co.get_plot(module='Total')
        )
    ], id='graph-div')
], id='main-div')

app = dash.Dash()
app.layout = layout


@app.callback(
    Output('coverage-graph', 'figure'),
    [Input('module-dropdown', 'value')],
    [State('module-folder-radio-switch', 'value')]
)
def update_graph(module, selection):
    if selection == 'per Module' and module is not None:
        fig = co.get_plot(module)
    elif selection == 'per Folder' and module is not None:
        fig = co.get_submodule_plot(module)
    else:
        fig = go.Figure()
    return fig


@app.callback(
    Output('module-dropdown', 'options'),
    [Input('module-folder-radio-switch', 'value')]
)
def update_options(selection):
    if selection == 'per Module':
        options = ms.get_options()
    elif selection == 'per Folder':
        options = ms.get_submodule_options()
    else:
        options = fallback_dropdown_options
    return options


if __name__ == '__main__':
    app.run_server(debug=False)
