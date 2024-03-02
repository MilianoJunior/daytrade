import matplotlib.pyplot as plt

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
        self.cumulative_rewards = 0

    def record_step(self, state, action, price, reward, position, verbose=False):
        ''' Armazena as experiências do agente a cada interação com o ambiente'''

        if verbose:
            print('State: ',state,' Ação: ', action, ' Preço: ', price, ' Recompensa: ', reward, ' Posição: ', position)
        self.cumulative_rewards += reward
        self.data['actions'].append(action)
        self.data['prices'].append(price)
        self.data['rewards'].append(reward)
        self.data['positions'].append(position)
        self.data['cumulative_rewards_const'] = self.cumulative_rewards
        self.data['cumulative_rewards'].append(self.cumulative_rewards)

    def start_episode(self):
        ''' Inicializa o episódio'''

        self.data = {
            'actions': [],
            'prices': [],
            'rewards': [],
            'positions': [],
            'cumulative_rewards': 0,
            'cumulative_rewards': []
        }

    def plot_trading_results(self):
        ''' Plota os resultados do trading'''

        plt.figure(figsize=(12, 6))
        plt.subplot(2, 1, 1)
        plt.plot(self.data['prices'], label='Price', color='blue')
        plt.title('Trading Performance')
        plt.ylabel('Price')
        plt.legend()
        plt.subplot(2, 1, 2)
        plt.plot(self.data['rewards'], label='Reward', color='green')
        plt.xlabel('Step')
        plt.ylabel('Reward')
        plt.legend()

        plt.tight_layout()
        plt.show()

    def get_total_reward(self):
        ''' Retorna a recompensa total acumulada'''

        return self.data['cumulative_rewards_const']

    def end_episode(self):
        ''' Finaliza o episódio no sistema de avaliação'''

        self.plot_trading_results()
