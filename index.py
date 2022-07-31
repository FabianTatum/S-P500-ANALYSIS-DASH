#!/usr/bin/env python
# coding: utf-8

# -------------------------------------------
# -------------------------------------------
# ||||      IMPORTACION DE LIBRERIAS    |||||
# -------------------------------------------
# -------------------------------------------
# TODO: Importación de librerias y utilidades

from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px

import yfinance as yf
import pandas as pd
import numpy as np

# TODO: Extracción de tabla con las principales características de las empresas que componene el S&P500
wiki = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
wiki_sp500 = wiki[0]
wiki_sp500

# TODO: función arreglar anomalias
x = lambda x : x.replace('.', '-')
wiki_sp500['Symbol'] = wiki_sp500['Symbol'].apply(x)

# TODO: List de nombres del SP500
tickers = list(wiki_sp500['Symbol'])

# TODO: Traer datos de las Acciones de yahoo finance api
raw_data = yf.download(tickers=tickers, start='2000-01-01', end='2021-12-31', interval='1d', threads=True, group_by='ticker')


# TODO: Convertir tabla a Single Index
df_original = raw_data.stack(level=0).rename_axis(['Date', 'Ticker']).reset_index(level=1)
df_original.reset_index()

# TODO: Obtener una copia del dataframe original
df = df_original.copy().sort_values(['Date', 'Ticker'])
df.reset_index(inplace=True)

# TODO: Agregar dia de la semana al dataframe
days = {
    0:'Mon',
    1:'Tues',
    2:'Weds',
    3:'Thurs',
    4:'Fri',
    5:'Sat',
    6:'Sun'
}
df['Week_Day'] = df['Date'].dt.dayofweek
# df['Week_Day'] = df['Week_Day'].apply(lambda x: days[x])

# TODO: Separar en 500 dataframes para realizar los diferentes calculos recomendados
list_sp500 = df['Ticker'].unique()
list_df = []
for i in list_sp500:
    df_ticker = df[df['Ticker'] == i]
    # TODO: Retorno GAP
    df_ticker['GAP_Ret'] = np.log(df_ticker['Open'] / df_ticker['Close'].shift(1)).fillna(0)
    # TODO: Retorno Intradia
    df_ticker['Intra_Ret'] = np.log(df_ticker['Close'] / df_ticker['Open']).fillna(0)
    # TODO: Variación
    df_ticker['Variations'] = (df_ticker['Adj Close'].pct_change()).fillna(0)
    # TODO: Volatilidad
    df_ticker['Volatility'] = (df_ticker['Variations'].rolling(250).std()*100*(250)**0.5).fillna(0)
    list_df.append(df_ticker)


# TODO: Concatener dataframes con los calculos en un solo dataframe
df_cal = pd.DataFrame()
for i in list_df:
    df_cal = pd.concat([df_cal, i], ignore_index=True)


# TODO: Agregar año de la fecha
df_cal['Year'] = pd.DatetimeIndex(df_cal['Date']).year


# TODO: Agregar Año y Fecha
df_cal['Year/Month'] = df_cal['Date'].dt.strftime('%Y-%m')


# TODO: Agregar industrias del SP500
df_cal = pd.merge(df_cal, wiki_sp500[['Symbol', 'GICS Sector']], how='left', left_on='Ticker', right_on='Symbol')


# TODO: Agregar la Varianzar porcentual del Intradia
df_cal['Var_Pct_Intra'] = (((df_cal['Close'] - df_cal['Open']) / df_cal['Open']) * 100)

df_cal = df_cal.sort_values('Date')

# ------------------------------------------
# ------------------------------------------
# ||||      MUESTRAS Y AGRUPACIONES    |||||
# ------------------------------------------
# ------------------------------------------

# TODO: Agrupar por cada fecha
df_date = df_cal.groupby('Date', as_index=False).mean()

# TODO: Agrupar por dia de la semana
df_days = df_cal.groupby('Week_Day', as_index=False).mean()

# TODO: Agrupar por Empresa
df_tic = df_cal.groupby('Ticker', as_index=False).mean()
df_tic_nine_gap = df_tic.sort_values('GAP_Ret', ascending=False)[:10]
df_tic_nine_intra = df_tic.sort_values('Intra_Ret', ascending=False)[:10]
df_tic_nine_volat = df_tic.sort_values('Volatility')[:10]

# TODO: Agrupar por Industria
df_ind = df_cal.groupby('GICS Sector', as_index=False).mean()
df_ind = df_ind.sort_values('Var_Pct_Intra', ascending=False)


# ---------------------------
# ---------------------------
# ||||      GRAFICOS    |||||
# ---------------------------
# ---------------------------

# TODO: Descripcion general de los datos
fig_box_year_gap = px.box(df_date, x='Year', y='GAP_Ret', title='Distribución de la Media de los Retornos GAP Anualmente')
fig_box_year_intra = px.box(df_date, x='Year', y='Intra_Ret', title='Distribución de la Media de los Retornos Intradiario')
fig_bar_year_vol = px.bar(df_days, x='Week_Day', y='Volume', title='Distribución de los Volumenes por Dia de la Semana')
fig_bar_year_vol.update_traces(marker_color='rgb(172, 250, 246 )', marker_line_color='rgb(34, 156, 150 )',
                  marker_line_width=1.5, opacity=0.6)

# TODO: Graficos para dias de la semana segun el GAP
fig_bar_days_gap = px.bar(df_days, x='Week_Day', y='GAP_Ret', title='Media del Retorno GAP en los Dias de la Semana')
fig_bar_days_gap.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)',
                  marker_line_width=1.5, opacity=0.6)

fig_line_days_gap = px.line(df_date, x='Date', y='GAP_Ret', color='Week_Day', markers=True, title='Media de los retornos GAP por Año')


# TODO: Graficos para dias de la semana segun Intradiario
fig_bar_days_intra = px.bar(df_days, x='Week_Day', y='Intra_Ret', title='Media del Retorno Intradiario según cada día de la Semana')
fig_bar_days_intra.update_traces(marker_color='rgb(228,179,245)', marker_line_color='rgb(130,19,168)',
                  marker_line_width=1.5, opacity=0.6)

fig_line_days_intra = px.line(df_date, x='Date', y='Intra_Ret', color='Week_Day', markers=True, title='Media de los Retornos Intradiario por Año')

# TODO: Graficos para Alta Volatilidad
fig_line_av = px.line(df_date, x='Date', y='Volatility')


# TODO: Graficos Mejores industrias
fig_bar_ind_vpct = px.bar(df_ind, x='GICS Sector', y='Var_Pct_Intra')
fig_bar_ind_vpct.update_traces(marker_color='rgb(176, 192, 237)', marker_line_color='rgb(39, 79, 193)',
                  marker_line_width=1.5, opacity=0.6)

# TODO: Graficos para Mejores Empresas
fig_bar_tic_gap = px.bar(df_tic_nine_gap, x='Ticker', y='GAP_Ret', title='Media de los retornos GAP por cada Empresa')
fig_bar_tic_gap.update_traces(marker_color='rgb(208, 200, 21)', marker_line_color='rgb(255, 255, 0 )',
                  marker_line_width=1.5, opacity=0.6)

fig_bar_tic_intra = px.bar(df_tic_nine_intra, x='Ticker', y='Intra_Ret', title='Media de los retornos Intradiarios por cada Empresa')
fig_bar_tic_intra.update_traces(marker_color='rgb(115, 205, 24)', marker_line_color='rgb(178, 240, 116)',
                  marker_line_width=1.5, opacity=0.6)

fig_bar_tic_volat = px.bar(df_tic_nine_volat, x='Ticker', y='Volatility', title='Media de la Volatilidad por cada Empresa')
fig_bar_tic_volat.update_traces(marker_color='rgb(241, 151, 151)', marker_line_color='rgb(194, 35, 35)',
                  marker_line_width=1.5, opacity=0.6)

# ----------------------------------------------------
# ----------------------------------------------------
# ||||      PUNTO DE ENTRADA DE LA APLICACION    |||||
# ----------------------------------------------------
# ----------------------------------------------------

# TODO: Punto de entrada de la aplicación
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])

server = app.server

# TODO: Cuerpo de la aplicación
app.layout = dbc.Container(children=[
    
    html.H1(children='Analisis del S&P500', className='p-5 text-center'),

    html.H3(children='Descripción de los datos'),

    dcc.Graph(
        id='fig_box_year_gap',
        figure=fig_box_year_gap
    ),

    dcc.Graph(
        id='fig_box_year_intra',
        figure=fig_box_year_intra
    ),

    dcc.Graph(
        id='fig_bar_year_vol',
        figure=fig_bar_year_vol
    ),

    html.H3(children='- Cuál es el mejor día de la semana para invertir teniendo en cuenta los Retornos GAP'),

    dcc.Graph(
        id='fig_bar_days_gap',
        figure=fig_bar_days_gap
    ),


    dcc.Graph(
        id='fig_line_days_gap',
        figure=fig_line_days_gap
    ),

    html.H3(children='- Cuál es el mejor día de la semana para invertir teniendo en cuenta los Retornos Intradiarios'),

    dcc.Graph(
        id='fig_bar_day_intra',
        figure=fig_bar_days_intra
    ),

    dcc.Graph(
        id='fig_line_days_intra',
        figure=fig_line_days_intra
    ),

    html.P(children='Según el Retorno Intradiario, observando tanto por año como por la media de los valores el mejor Día de la Semana para invertir es el Jueves'),

    html.H3(children='- Cuáles son las mejores industrias que pertenecen al S&P500'),
    
    dcc.Graph(
        id='fig_bar_ind_Ptc',
        figure=fig_bar_ind_vpct
    ),

    html.P(children='Tomando el cambio porcentual, desde que cada empresa se incluye en el S&P500, Las mejores industrias para realizar una inversión son las de Salud, Tecnología y Bienes Inmuebles.'),

    html.H3(children='- Cuáles son los momentos de alta volatilidad que afectaron el S&P500'),

    dcc.Graph(
        id='fig_line_av',
        figure=fig_line_av
    ),

    html.P(children='Podemos observar 2 Picos distintivos en la volatilidad del S&P500:'),
    html.P(children=' - La crisis financiara de 2008, la cuál fue influenciada por la burbuja de las hipotecas'),
    html.P(children=' - La Pandemia de 2020, la cuál afecto al Todas las Estructuras financieras'),

    html.H2(children='- Cuáles son las mejores empresas del S&P500 para realizar una inversión'),

    dcc.Graph(
        id='fig_bar_tic_gap',
        figure=fig_bar_tic_gap
    ),

    html.P(children='En este caso puede ser lógico que una empresa como Moderna a causa del fenómeno de las vacunas y la información fuera de la apertura tenga elevado retorno GAP'),

    dcc.Graph(
        id='fig_bar_tic_intra',
        figure=fig_bar_tic_intra
    ),

    html.P(children='En este caso Carrier en el Retorno Intradiario, pero debemos tener en cuenta que es una empresa muy reciente.'),
    html.P(children='En este caso NVR Inc. es una empresa con mas tradición, pero su retorno puede ser menor.'),

    dcc.Graph(
        id='fig_bar_tic_volat',
        figure=fig_bar_tic_volat
    ),

    html.P(children='Organon & Co y Otis Elevator muestra una volatilidad muy pequeña, pero debemos tener en cuenta que son empresas muy recientes.'),
    html.P(children='Carrier como tercera opción, es una empresa mas tradicional y con menor volatilidad, asi que se presenta como una buena opción.'),
])

if __name__ == '__main__':
    app.run_server(debug=False)
