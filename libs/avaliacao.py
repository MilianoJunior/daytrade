import matplotlib.pyplot as plt
import pandas as pd
import matplotlib
from matplotlib.animation import FuncAnimation
import threading
from multiprocessing import Process
import warnings

# Ignora UserWarning emitidos pelo Matplotlib
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

class TradingDataStore:
    def __init__(self):
        ''' Armazena as experiências do agente e plota os resultados'''

        self.data = {
            'actions': [],
            'prices': [],
            'rewards': [],
            'positions': [],
            'cumulative_rewards_const': 0,
            'cumulative_rewards': []
        }
        self.labes = {0: 'Manter', 1: 'Comprar', 2:'Vender' }
        self.process = None
        self.ordem = 0
        self.contador = 0
        self.cont = 0
        self.cumulative_rewards = 0
        self.position_data = pd.DataFrame(columns=['ordem','horario entrada','horario saida','duracao','ativo','tipo','preco entrada','preco saida','resultado','acumulado'])
        self.data = []

    def record_step(self, state, action, next_state, reward, position, price_adquire, verbose=False):
        ''' Armazena as experiências do agente a cada interação com o ambiente'''

        self.cont += 1

        if self.ordem == 0 and position == 1:
            self.contador += 1
            if verbose:
                print('...' * 25)
                print(self.contador, ' Comprado')
                print('...' * 25)
            self.position_data.loc[self.contador,'ordem'] = self.contador
            self.position_data.loc[self.contador,'horario entrada'] =pd.to_datetime(state.observation[0], unit='s')
            self.position_data.loc[self.contador,'ativo'] = 'WIN$'
            self.position_data.loc[self.contador,'tipo'] = 'Compra'
            self.position_data.loc[self.contador,'preco entrada'] = price_adquire

            self.ordem = 1

        if self.ordem == 0 and position == 2:
            self.contador += 1
            if verbose:
                print('...' * 25)
                print(self.contador, ' Vendido')
                print('...' * 25)
            self.position_data.loc[self.contador, 'ordem'] = self.contador
            self.position_data.loc[self.contador, 'horario entrada'] = pd.to_datetime(state.observation[0], unit='s')
            self.position_data.loc[self.contador, 'ativo'] = 'WIN$'
            self.position_data.loc[self.contador, 'tipo'] = 'Venda'
            self.position_data.loc[self.contador, 'preco entrada'] = price_adquire

            self.ordem = 2
        if verbose:
            print(' ' * 5, self.cont,
                  ' Preco Adq.:', price_adquire,
                  ' Ação:', action,
                  ' Recomp.:', reward,
                  ' Pos.:', position,
                  ' Act bid:', state.observation[1],
                  ' ask:',state.observation[2],
                  ' Next bid:', next_state.observation[1],
                  ' ask:',next_state.observation[2],
                  ' vol:', state.observation[4],
                  ' Cum. Recomp.:', self.cumulative_rewards)

        if self.ordem == 1 and position == 0:
            if verbose:
                print('Compra encerrada')
                print('-------------------')
            self.cumulative_rewards += reward
            self.position_data.loc[self.contador, 'horario saida'] = pd.to_datetime(state.observation[0], unit='s')
            self.position_data.loc[self.contador, 'duracao'] = self.position_data.loc[self.contador, 'horario saida'] - self.position_data.loc[self.contador, 'horario entrada']
            self.position_data.loc[self.contador, 'preco saida'] = next_state.observation[1]
            self.position_data.loc[self.contador, 'resultado'] = reward
            self.position_data.loc[self.contador, 'acumulado'] = self.cumulative_rewards
            self.ordem = 0

        if self.ordem == 2 and position == 0:
            if verbose:
                print('Venda encerrada')
                print('-------------------')
            self.cumulative_rewards += reward
            self.position_data.loc[self.contador, 'horario saida'] = pd.to_datetime(state.observation[0], unit='s')
            self.position_data.loc[self.contador, 'duracao'] = self.position_data.loc[self.contador, 'horario saida'] - \
                                                               self.position_data.loc[self.contador, 'horario entrada']
            self.position_data.loc[self.contador, 'preco saida'] = next_state.observation[2]
            self.position_data.loc[self.contador, 'resultado'] = reward
            self.position_data.loc[self.contador, 'acumulado'] = self.cumulative_rewards
            self.ordem = 0

        self.data.append([state.observation, action, reward, next_state.observation])
    def record_position(self, position):
        ''' Armazena a posição do agente'''

        self.data['positions'].append(position)

    def plot_trading_results(self, explore_rate):
        ''' Plota os resultados do trading'''

        # plotar o valor acumulado das vendas
        df_vendas = self.position_data[self.position_data['tipo'] == 'Venda']
        df_vendas['acumulado'] = df_vendas['resultado'].cumsum()

        # Cria uma cópia do DataFrame antes de modificá-lo
        df_vendas = self.position_data[self.position_data['tipo'] == 'Venda'].copy()
        df_vendas['acumulado'] = df_vendas['resultado'].cumsum()

        plt.figure(figsize=(12, 6))
        plt.subplot(3, 1, 1)
        plt.plot(df_vendas['acumulado'], label='Soma das recompensas Vendas', color='red')
        plt.title('Trading Performance Vendas')
        plt.ylabel('Ganhos')
        plt.legend()

        # Cria uma cópia do DataFrame antes de modificá-lo
        df_compras = self.position_data[self.position_data['tipo'] == 'Compra'].copy()
        df_compras['acumulado'] = df_compras['resultado'].cumsum()

        plt.subplot(3, 1, 2)
        plt.plot(df_compras['acumulado'], label='Soma das recompensas Compras', color='blue')
        plt.xlabel('Trading Performance Vendas')
        plt.ylabel('Reward')
        plt.legend()

        # plotar o valor acumulado total
        plt.subplot(3, 1, 3)
        plt.plot(self.position_data['acumulado'], label='Soma das recompensas Total', color='green')
        plt.xlabel('Trading Performance Total')
        plt.ylabel('Reward')
        plt.legend()

        plt.tight_layout()
        plt.show(block=False)


    def get_total_reward(self):
        ''' Retorna a recompensa total acumulada'''

        return self.data['cumulative_rewards_const']

    def end_episode(self):
        ''' Finaliza o episódio no sistema de avaliação'''
        pass

        # self.plot_trading_results()
