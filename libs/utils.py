import pandas as pd

def tratar_dataframe(data):
    """
    Processa o DataFrame para ser usado no ambiente de negociação.

    :param data: DataFrame contendo os dados do WIN$.
    :return: DataFrame processado.
    """
    try:
        # Converter a coluna Data para o tipo datetime
        data['Data'] = pd.to_datetime(data['Data'], format='%d.%m.%Y')

        # Converter a coluna Vol. para float
        data['Vol.'] = data['Vol.'].str.replace('K', '000')
        data['Vol.'] = data['Vol.'].str.replace('M', '000000')
        data['Vol.'] = data['Vol.'].str.replace(',', '')
        data['Vol.'] = data['Vol.'].astype(float)

        # Converter a coluna Var% para float
        data['Var%'] = data['Var%'].str.replace('%', '')
        data['Var%'] = data['Var%'].str.replace(',', '.')
        data['Var%'] = data['Var%'].astype(float)

        # Verificar se há valores nulos
        qtd_null = data.isnull().sum()

        # Se houver valores nulos
        if data.isnull().values.any():
            # Preencher os valores nulos com a média
            data = data.fillna(data.mean())

        # Inverter o DataFrame
        data = data.iloc[::-1]

        return data
    except Exception as e:
        print('Erro ao processar o DataFrame: ', e)
        raise e

def excluir_zeros(df):
    """
    Exclui as linhas que contém zeros do DataFrame.

    :param df: DataFrame contendo os dados do WIN$.
    :return: DataFrame sem as linhas que contém zeros.
    """
    try:
        # Excluir as linhas que contém zeros
        df = df[(df != 0).all(1)]

        return df
    except Exception as e:
        print('Erro ao excluir as linhas que contém zeros: ', e)
        raise e

def excluir_valores(df):
    ''' Exclui valores discrepantes'''
    try:
        # verifica as diferenças entre os valores das colunas bid e ask
        df['diferenca'] = df['ask'] - df['bid']
        df_counts = df['diferenca'].value_counts()
        # print('diferenca:', df_counts)
        # print('----'*10)
        df = df[(df['diferenca'] < 50) & (df['diferenca'] > -50)]
        df_counts = df['diferenca'].value_counts()

        df = df.drop('diferenca', axis=1)
        df = df.drop('time', axis=1)
        df = df.drop('time_msc', axis=1)

        # Excluir a coluna timestamp

        return df
    except Exception as e:
        print('Erro ao excluir as linhas que contém zeros: ', e)
        raise e

def normalize(df):
    ''' Normaliza os valores do DataFrame'''
    try:
        # Normalizar os valores do DataFrame
        std = df.std()
        mean = df.mean()

        df = (df - df.mean()) / df.std()
        return df
    except Exception as e:
        print('Erro ao normalizar os valores do DataFrame: ', e)
        raise e