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

