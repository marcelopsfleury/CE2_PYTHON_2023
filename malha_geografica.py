import geobr
import pandas as pd

malha_geografica = geobr.read_municipality(year=2020)

enade = pd.read_csv('./dados_tratados/CURSO_CONTEXTO.csv')

enade_mapa = enade.merge(malha_geografica, left_on='CO_MUNIC_CURSO', right_on='code_muni')

enade_mapa.to_csv('./dados_tratados/CURSO_CONTEXTO_MAPA.csv', index=False, sep=',')