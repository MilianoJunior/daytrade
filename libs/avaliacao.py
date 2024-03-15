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

    def update_data_and_plot(self):
        # Encerra o processo anterior se ele ainda estiver rodando
        if self.process is not None and self.process.is_alive():
            self.process.terminate()
            self.process.join()  # Espera o processo ser encerrado

        # Cria e inicia um novo processo
        self.process = Process(target=self.plot_graph, args=(self.position_data['acumulado'], self.position_data['resultado']))
        self.process.start()

    def plot_graph(self, acumulado, resultado):
        import matplotlib.pyplot as plt
        plt.figure(figsize=(12, 6))

        plt.subplot(2, 1, 1)
        plt.plot(acumulado, label='Soma das recompensas', color='blue')
        plt.title('Trading Performance')
        plt.ylabel('Ganhos')
        plt.legend()

        plt.subplot(2, 1, 2)
        plt.plot(resultado, label='Reward', color='green')
        plt.xlabel('Step')
        plt.ylabel('Reward')
        plt.legend()

        plt.tight_layout()
        plt.show()

    # def plot_trading_results(self):
    #     ''' Plota os resultados do trading de forma dinâmica em um thread separado '''
    #
    #     def run_plot():
    #         fig, axs = plt.subplots(2, 1, figsize=(12, 6))
    #
    #         def update(frame):
    #             axs[0].clear()
    #             axs[1].clear()
    #
    #             axs[0].plot(self.position_data['acumulado'], label='Soma das recompensas', color='blue')
    #             axs[0].set_title('Trading Performance')
    #             axs[0].set_ylabel('Ganhos')
    #             axs[0].legend()
    #
    #             axs[1].plot(self.position_data['resultado'], label='Reward', color='green')
    #             axs[1].set_xlabel('Step')
    #             axs[1].set_ylabel('Reward')
    #             axs[1].legend()
    #
    #         ani = FuncAnimation(fig, update, interval=1000)  # Atualiza a cada 1000 ms
    #         plt.tight_layout()
    #         plt.show()
    #
    #     # Inicia o thread de plotagem
    #     plot_thread = threading.Thread(target=run_plot)
    #     plot_thread.start()

    def plot_trading_results(self):
        ''' Plota os resultados do trading'''

        plt.figure(figsize=(12, 6))
        plt.subplot(2, 1, 1)
        plt.plot(self.position_data['acumulado'], label='Soma das recompensas', color='blue')
        plt.title('Trading Performance')
        plt.ylabel('Ganhos')
        plt.legend()
        plt.subplot(2, 1, 2)
        plt.plot(self.position_data['resultado'], label='Reward', color='green')
        plt.xlabel('Step')
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
