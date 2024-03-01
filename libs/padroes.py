import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

flags = {
    2: 'tick alterou o preço Bid',
    4: 'tick alterou o preço Ask',
    8: 'tick alterou o último preço da oferta',
    16: 'tick alterou o volume',
    32: 'tick é resultado de uma compra',
    64: 'tick é resultado de uma venda'
}


import pandas as pd
import time

class Padroes:

    def __init__(self):
        self.preco = None
        self.armazena = pd.DataFrame(columns=['time', 'bid', 'ask', 'freq', 'regularidade', 'amplitude', 'duracao'])

    def frequencia_hist(self, serie):
        '''Calcula a frequência de um padrão em uma série.'''

        inicio = time.time()

        # Agrupar por 'bid' e 'ask' e contar a frequência
        frequencias = serie.groupby(['bid', 'ask']).size().reset_index(name='freq')

        # Juntar os resultados com a série original para adicionar a coluna 'freq'
        serie = pd.merge(serie, frequencias, on=['bid', 'ask'], how='left')

        # Atualizar 'self.armazena' com as novas frequências
        for _, row in frequencias.iterrows():
            bid = row['bid']
            ask = row['ask']
            freq = row['freq']

            # Verificar se o par (bid, ask) já existe
            index = self.armazena[(self.armazena['bid'] == bid) & (self.armazena['ask'] == ask)].index
            if index.empty:
                # Criar nova linha e usar pd.concat para adicionar ao DataFrame
                new_row = pd.DataFrame({'bid': [bid], 'ask': [ask], 'freq': [freq], 'regularidade': [0], 'amplitude': [0], 'duracao': [0]})
                self.armazena = pd.concat([self.armazena, new_row], ignore_index=True)
            else:
                # Atualizar frequência se já existir
                self.armazena.loc[index[0], 'freq'] = freq

        # Atualizar 'regularidade' baseado na nova 'freq'
        self.armazena['regularidade'] = self.armazena['freq'] / len(self.armazena)

        # Atualizar a série original com a frequência e regularidade final
        # serie = serie.drop(columns=['freq_temp'])  # Remover a coluna temporária de frequência
        serie = pd.merge(serie, self.armazena[['bid', 'ask', 'freq', 'regularidade']], on=['bid', 'ask'], how='left')

        print(f"Tempo de execução: {time.time() - inicio}")
        return serie

    def frequencia_inst(self, serie)->int:
        """
        Calcula a frequência de um padrão em uma série.
        Quantas vezes o padrão aparece na série.
        ex: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] -> [1, 2, 3] = 1
        frequencia[x] = quantidade de vezes que o padrão x aparece na série
        """
        # verifica o valor de bid e ask
        if isinstance(serie, list):
            times = serie[0]
            bid = serie[1]
            ask = serie[2]
        else:
            times = serie['time']
            bid = serie['bid']
            ask = serie['ask']
        value = self.armazena.query(f'bid == {bid} and ask == {ask}')
        if value.empty:
            self.armazena.loc[len(self.armazena)] = [times, bid, ask, 1, 0, 0, 0]
            return [1], [0]
        else:
            self.armazena.loc[value.index, 'freq'] += 1
            self.armazena.loc[value.index, 'time'] = times
            self.armazena.loc[value.index, 'regularidade'] = self.armazena.loc[value.index, 'freq'] / len(self.armazena)
        return self.armazena['freq'].values[value.index], self.armazena.loc[value.index, 'regularidade'].values


    def regularidade(self, serie):
        """
        Calcula a regularidade de um padrão em uma série.
        é a frequência dividida pelo número de ticks
        """

        return []



    def amplitude(self, serie):
        """
        Calcula a amplitude de um padrão em uma série.
        """
        return []

    def duracao(self, serie):
        """
        Calcula a duração de um padrão em uma série.
        """
        return []

    def grafico(self, bid_counts, ask_counts):
        """
        Gera um gráfico do padrão em uma série.
        """
        # Limitar o número de barras no gráfico
        # Resetar o índice da série


        for i in range(len(bid_counts)):
            print(f"{bid_counts.index[i]}: {bid_counts[i]}")

        for i in range(len(ask_counts)):
            print(f"{ask_counts.index[i]}: {ask_counts[i]}")

        bid_counts = bid_counts.reset_index(drop=True)
        ask_counts = ask_counts.reset_index(drop=True)

        # Limitar o número de barras no gráfico
        num_bars = min(50, len(bid_counts), len(ask_counts))
        bid_counts = bid_counts[:num_bars]
        ask_counts = ask_counts[:num_bars]

        # Plotar o histograma para bid_counts
        plt.figure(figsize=(10, 5))
        plt.hist(bid_counts, bins=num_bars, alpha=0.5, label='bid_counts')
        plt.title('Histograma de Frequência - Bid Counts')
        plt.xlabel('Valores Únicos')
        plt.ylabel('Frequência')
        plt.legend(loc='upper right')
        plt.show()

        # Plotar o histograma para ask_counts
        plt.figure(figsize=(10, 5))
        plt.hist(ask_counts, bins=num_bars, alpha=0.5, label='ask_counts', color='g')
        plt.title('Histograma de Frequência - Ask Counts')
        plt.xlabel('Valores Únicos')
        plt.ylabel('Frequência')
        plt.legend(loc='upper right')
        plt.show()


        return []

# bid_counts = serie['bid'].value_counts()
# ask_counts = serie['ask'].value_counts()
# if bid_counts.empty:
#     print("A série bid_counts está vazia.")
# else:
#     print("A série bid_counts contém dados.")
#
# if ask_counts.empty:
#     print("A série ask_counts está vazia.")
# else:
#     print("A série ask_counts contém dados.")
# self.grafico(bid_counts, ask_counts)
#
# # print(counts)
# # return bid_counts, ask_counts
# print(bid_counts)
# print(ask_counts)
# return []