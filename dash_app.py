# Importar pacotes
import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely import wkt

# Criar aplicativo
app = dash.Dash(__name__, external_stylesheets=["https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css"])

# Carregar dados
dados = pd.read_csv('./dados_tratados/CURSO_CONTEXTO_MAPA.csv')

dados["CO_MODALIDADE"] = dados["CO_MODALIDADE"].apply(lambda x: "EAD" if x == 0 else "Presencial")

# Converter a coluna 'geometry' para o formato GeoJSON apropriado
dados['geometry'] = dados['geometry'].apply(wkt.loads)
dados = gpd.GeoDataFrame(dados)

# CSS para o painel
estilo_painel = {
    'border': '1px solid #D3D3D3',
    'border-radius': '5px',
    'padding': '10px',
    'margin': '10px',
}

# CSS para o cabeçalho do painel
estilo_cabecalho_painel = {
    'background-color': '#f5f5f5',
    'border-bottom': '1px solid #D3D3D3',
    'padding': '10px',
}

# CSS para o corpo do painel
estilo_corpo_painel = {
    'padding': '10px',
}

# CSS para o botão do mapa
estilo_botao_mapa = {
    'display': 'flex',
    'justify-content': 'center',
    'margin-top': '10px',
}

# Aplicar estilo para os gráficos
estilo_grafico_horizontal = {
    'paper_bgcolor': 'rgba(255, 255, 255, 0.8)',
    'plot_bgcolor': 'rgba(255, 255, 255, 0.8)',
    'font_family': 'Arial',
    'margin': dict(l=50, r=20, t=50, b=50),  # Ajustar a margem esquerda para acomodar rótulos longos
    'legend': dict(
        title='',
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5,
        font=dict(size=12),
        bgcolor='rgba(0,0,0,0)'
    ),
    'xaxis': dict(title='Total Inscritos', tickfont=dict(size=10)),
    'yaxis': dict(tickfont=dict(size=10))
}

# Criar o layout
app.layout = html.Div(className='container', children=[
    # Título e Filtros
    html.Div(className='panel panel-default', style=estilo_painel, children=[
        html.Div(className='panel-heading', style=estilo_cabecalho_painel, children=[
            html.H1('Microdados do ENADE 2021', className='text-center mt-4 mb-4'),
        ]),
        html.Div(className='panel-body', style=estilo_corpo_painel, children=[
            # Conteúdo dos filtros
            html.Div(className='row justify-content-center', children=[
                html.Div(className='col-md-4', children=[
                    html.Label('CURSO:', className='font-weight-bold'),
                    dcc.Dropdown(
                        id='co-grupo-dropdown',
                        options=[{'label': grp, 'value': grp} for grp in dados['CO_GRUPO'].unique()],
                        value=['Matemática (Licenciatura)', 'Física (Licenciatura)'],
                        multi=True
                    ),
                ]),
                html.Div(className='col-md-4', children=[
                    html.Label('AGRUPAR POR:', className='font-weight-bold'),
                    dcc.RadioItems(
                        id='color-radio',
                        options=[
                            {'label': ' Categoria', 'value': 'CO_CATEGAD'},
                            {'label': ' Região', 'value': 'CO_REGIAO_CURSO'},
                            {'label': ' Modalidade', 'value': 'CO_MODALIDADE'}
                        ],
                        value='CO_CATEGAD',
                        labelStyle={'display': 'block'}
                    ),
                ]),
            ]),
        ]),
    ]),

    # Gráfico de Barras e Boxplot
    html.Div(className='row', children=[
        # Gráfico de Barras
        html.Div(className='col-md-6', children=[
            html.Div(className='panel panel-default', style=estilo_painel, children=[
                html.Div(className='panel-heading', style=estilo_cabecalho_painel, children=[
                    html.H3('Total de inscritos por curso', className='text-center mb-3'),
                ]),
                html.Div(className='panel-body', style=estilo_corpo_painel, children=[
                    dcc.Graph(id='grafico-barras-horizontal'),
                ]),
            ]),
        ]),

        # Boxplot
        html.Div(className='col-md-6', children=[
            html.Div(className='panel panel-default', style=estilo_painel, children=[
                html.Div(className='panel-heading', style=estilo_cabecalho_painel, children=[
                    html.H3('Nota geral por curso', className='text-center mb-3'),
                ]),
                html.Div(className='panel-body', style=estilo_corpo_painel, children=[
                    dcc.Graph(id='grafico-boxplot-horizontal'),
                ]),
            ]),
        ]),
    ]),

    # Mapa
    html.Div(className='panel panel-default', style=estilo_painel, children=[
        html.Div(className='panel-heading', style=estilo_cabecalho_painel, children=[
            html.H3('Distribuição geográfica de notas e número de inscritos', className='text-center mb-3'),
        ]),
        html.Div(className='panel-body', style=estilo_corpo_painel, children=[
            dcc.Graph(id='mapa'),
            # Botão do Mapa
            html.Div(style=estilo_botao_mapa, children=[
                dcc.RadioItems(
                    id='map-value-radio',
                    options=[
                        {'label': ' Nota Geral', 'value': 'NT_GER'},
                        {'label': ' Total Inscritos', 'value': 'Total_Inscritos'}
                    ],
                    value='NT_GER',
                    labelStyle={'display': 'inline-block', 'margin': '10px'}
                ),
            ]),
        ]),
    ]),
])

# Callback para atualizar os gráficos
@app.callback(
    [dash.dependencies.Output('grafico-barras-horizontal', 'figure'),
     dash.dependencies.Output('grafico-boxplot-horizontal', 'figure')],
    [
        dash.dependencies.Input('co-grupo-dropdown', 'value'),
        dash.dependencies.Input('color-radio', 'value')
    ]
)
def atualizar_graficos(co_grupo_valores, valor_cor):
    dados_filtrados = dados.copy()
    if co_grupo_valores:
        dados_filtrados = dados_filtrados[dados_filtrados['CO_GRUPO'].isin(co_grupo_valores)]

    x = dados_filtrados.groupby(['CO_GRUPO', valor_cor]).agg({'Total_Inscritos': 'sum'}).reset_index()
    x['Total_Inscritos'] = np.log2(x['Total_Inscritos'].astype(float))

    # Categorias únicas do valor_cor
    categorias_unicas = x[valor_cor].unique()

    # Definir a sequência ÚNICA de cores para cada categoria
    sequencia_cores = px.colors.qualitative.Set1[:len(categorias_unicas)]

    # Mapear cada categoria para uma cor na sequência de cores
    mapa_cores = {categoria: sequencia_cores[i] for i, categoria in enumerate(categorias_unicas)}

    x_ordenado = x.sort_values(by=['CO_GRUPO', 'Total_Inscritos'], ascending=[True, True])

    # Aplicar o mapeamento de cores tanto para o gráfico de barras quanto para o boxplot
    grafico_barras = px.bar(
        x_ordenado,
        y='CO_GRUPO',
        x='Total_Inscritos',
        color=valor_cor,
        orientation='h',
        title='',
        template='plotly_white',
        barmode='group',
        color_discrete_map=mapa_cores,
        labels={'Total_Inscritos': 'Total Inscritos', 'CO_GRUPO': 'Curso'}
    )

    grafico_barras.update_layout(estilo_grafico_horizontal)

    grafico_boxplot = px.box(
        dados_filtrados,
        y='CO_GRUPO',
        x='NT_GER',
        color=valor_cor,
        orientation='h',
        title='',
        template='plotly_white',
        color_discrete_map=mapa_cores,
        labels={'NT_GER': 'Nota Geral', 'CO_GRUPO': 'Curso'}
    )

    grafico_boxplot.update_layout(estilo_grafico_horizontal)

    return grafico_barras, grafico_boxplot

# Callback para atualizar o mapa
@app.callback(
    dash.dependencies.Output('mapa', 'figure'),
    [
        dash.dependencies.Input('co-grupo-dropdown', 'value'),
        dash.dependencies.Input('map-value-radio', 'value')
    ]
)
def atualizar_mapa(co_grupo_valores, valor_mapa):
    dados_filtrados = dados.copy()
    if co_grupo_valores:
        dados_filtrados = dados_filtrados[dados_filtrados['CO_GRUPO'].isin(co_grupo_valores)]

    # Agrupar dados por code_muni e calcular o valor médio para cada município
    dados_agrupados = dados_filtrados.groupby('code_muni').agg({valor_mapa: 'mean', 
                                                                'name_muni': lambda x: list(x.unique()),
                                                                'name_state': lambda x: list(x.unique()),
                                                                'CO_ORGACAD': lambda x: list(x.unique()),
                                                                'CO_CATEGAD': lambda x: list(x.unique()),
                                                                'CO_MODALIDADE': lambda x: list(x.unique())
                                                               }).reset_index()

    mapa = px.choropleth_mapbox(
        dados_agrupados,
        geojson=dados_filtrados.__geo_interface__,  # __geo_interface__ para obter dados em formato GeoJSON
        locations='code_muni',  # code_muni como identificador de localização
        featureidkey="properties.code_muni",
        color=valor_mapa,
        color_continuous_scale='RdBu',
        labels={valor_mapa: 'Média da Nota Geral' if valor_mapa == 'NT_GER' else 'Total de Inscritos'},
        hover_data={'code_muni': False, valor_mapa: True, 'name_muni': True,
                    'name_state': True, 'CO_ORGACAD': True, "CO_CATEGAD": True,
                    "CO_MODALIDADE": True}  # Dados adicionais do pop-up
    )

    mapa.update_geos(fitbounds="locations", visible=False)

    # Definir ponto inicial do mapa
    lat_lon_inicial = {"lat": -14.235, "lon": -51.9253}
    zoom_inicial = 3

    mapa.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        mapbox_style="carto-positron",
        mapbox_center=lat_lon_inicial,
        mapbox_zoom=zoom_inicial
    )

    return mapa

# Executar o app
if __name__ == '__main__':
    app.run_server(debug=True)
