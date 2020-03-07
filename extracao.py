import pandas as pd
import requests
from datetime import datetime

#arruma layout da tabela
def AjustaDF (df, nome):
    df.columns = ['data', str(nome)]
    date = df['data'].apply(lambda x: datetime.strptime(str(x * 100 + 1), '%Y%m%d').strftime('%d/%m/%Y'))
    df.set_index(date, inplace=True)
    return df.drop(['data'], axis=1)
   
#funcao para extrair dados das series temporaris do Bacen
def bacen (cod, nome = 'V'):
    url = 'http://api.bcb.gov.br/dados/serie/bcdata.sgs.' + str(cod) + '/dados?formato=json'
    #print(url)
    req = requests.get(url)
    df = pd.read_json(req.content)
    print(f'{nome} Tabela {str(cod)}: importacao de dados ok!')
    
    df.set_index('data', inplace=True)
    df.rename(index=str, columns={"valor": str(nome)}, inplace=True)
    return df
 
#funcao para extrair dados das series temporais do SIDRA/IBGE
def ibge (t, p = 'all', v = 'all', ter = 'br', n = '/n1/1', f = 'a', h = 'n', c = '', nome = 'V'):
    #http://api.sidra.ibge.gov.br
    api = 'http://api.sidra.ibge.gov.br/values'
    tabela = '/t/' + str(t)
    periodo = '/p/' + str(p)
    variaveis = '/v/' + str(v)
    
    if n != '/n1/1': 
        pass #quando for inserido referencia territorial personalizada, pular verificacao no parametro 'ter'
    else:
        if ter == 'reg':
            n = '/n2/all'
        elif ter == 'uf':
            n = '/n3/all'
        elif ter == 'mun':
            n = '/n6/all'
        elif ter == 'brreg':
            n = '/n1/1/n2/all'
        elif ter == 'bruf':
            n = '/n1/1/n3/all'
        elif ter == 'brreguf':
            n = '/n1/1/n2/all/n3/all'
        else: 
            pass
    territorio = str(n)
    header = '/h/' + str(h)
    formato = '/f/' + str(f)
    detalhes = str(c)
    
    url = api + tabela + periodo + variaveis + territorio + formato + header + detalhes
    #print(url)
    req = requests.get(url)
    df = pd.read_json(req.content)
    print(f'{nome} Tabela {str(t)}: importacao de dados ok!')
    
    #arruma layout da tabela
    tab = AjustaDF(df[['D1C', 'V']], nome)
    
    return tab
 
# IBGE
inflacao = ibge(1737, v=2266, f='c', nome='inflacao')
varejo = ibge(3416, v=564, f='c', c='/c11046/40312', nome='varejo')
renda = ibge(6392, v=6293, f='c', nome='renda')

dataset_ibge = inflacao.join(varejo).join(renda)

# BACEN
cambiorf = bacen(11753, nome='cambiorf') #cambio real efetivo 11753
cambio = bacen(3698, nome='cambio') #cambio nominal 3698
receita = bacen(22759, nome='receita') #receita de cartoes - gasto de estrangeiros no Brasil (US$ MM) 22759
despesa = bacen(22760, nome='despesa') #despesa de cartoes - gasto de brasileiros no exterior (US$ MM) 22760

dataset_bacen = cambiorf.join(cambio).join(receita).join(despesa)

# JOIN
dataset = dataset_ibge.join(dataset_bacen).loc['01/01/2000':]
dataset.info()
dataset.tail()
