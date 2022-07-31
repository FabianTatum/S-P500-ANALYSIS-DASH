
# TODO: Importación de librerias y utilidades

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
    df_ticker['GAP_Ret'] = np.log(df_ticker['Open'] / df_ticker['Close'].shift(1)).fillna(0)
    df_ticker['Intra_Ret'] = np.log(df_ticker['Close'] / df_ticker['Open']).fillna(0)
    df_ticker['Variations'] = (df_ticker['Adj Close'].pct_change()).fillna(0)
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

df_days = df_cal.groupby('Week_Day', as_index=False).mean()

df_ind = pd.merge(df_cal, wiki_sp500[['Symbol', 'GICS Sector']], how='left', left_on='Ticker', right_on='Symbol')

df_ind['Var_Pct_Intra'] = (((df_ind['Close'] - df_ind['Open']) / df_ind['Open']) * 100)
df_ind['Var_Pct_Intra']

df_ind_g = df_ind.groupby('GICS Sector', as_index=False).sum()

df_ind_g = df_ind_g[['GICS Sector', 'Var_Pct_Intra']].sort_values('Var_Pct_Intra', ascending=False)
df_ind_g

df_cal_sample = df_cal.sample(n=10000)
df_cal_sample

vix = df_cal.groupby('Date', as_index=False).mean()

# ### Cuales son las 9 mejores empresas para invertir

df_tic = df_cal.groupby(['Ticker', 'Year'], as_index=False).mean()
df_tic

df_tic = df_tic[['Ticker', 'GAP_Ret', 'Intra_Ret']].sort_values('GAP_Ret', ascending=False)
df_tic = df_tic[:9]
df_tic

df_tic = df_tic[['Ticker', 'GAP_Ret', 'Intra_Ret']].sort_values('Intra_Ret', ascending=False)
df_tic = df_tic[:9]
df_tic

df_Chg_Pct = (((df_cal['Close'].fillna(method='bfill').iloc[-1])-(df_cal['Open'].fillna(method='bfill').iloc[0]))/(df_cal['Open'].fillna(method='bfill').iloc[0]))*100

