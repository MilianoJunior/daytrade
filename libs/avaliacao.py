import matplotlib.pyplot as plt

class TradingDataStore:
    def __init__(self):
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
        self.data = {
            'actions': [],
            'prices': [],
            'rewards': [],
            'positions': [],
            'cumulative_rewards': 0,
            'cumulative_rewards': []
        }

    def plot_trading_results(self):
        plt.figure(figsize=(12, 6))

        # Plotting prices
        plt.subplot(2, 1, 1)
        plt.plot(self.data['prices'], label='Price', color='blue')
        plt.title('Trading Performance')
        plt.ylabel('Price')
        plt.legend()

        # Plotting rewards
        plt.subplot(2, 1, 2)
        plt.plot(self.data['rewards'], label='Reward', color='green')
        plt.xlabel('Step')
        plt.ylabel('Reward')
        plt.legend()

        plt.tight_layout()
        plt.show()

    def print_summary(self):
        print("Total Cumulative Reward:") #, self.data['cumulative_rewards'])
        # Add more summaries as needed

    def get_total_reward(self):
        return self.data['cumulative_rewards_const']

    def end_episode(self):
        self.plot_trading_results()
        # print('--'*100)
        # print("Total Cumulative Reward:", self.data['cumulative_rewards'])
        # print('--' * 100)

# Usage example:
# data_store = TradingDataStore()
# Inside your trading loop:
# data_store.record_step(action, price, reward, position)
# After simulation:
# data_store.plot_trading_results()
# data_store.print_summary()

''' 
class TradingDataStore:
    def __init__(self):
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
        self.data = {
            'actions': [],
            'prices': [],
            'rewards': [],
            'positions': [],
            'cumulative_rewards': 0,
            'cumulative_rewards': []
        }

    def plot_trading_results(self):
        plt.figure(figsize=(12, 6))

        # Plotting prices
        plt.subplot(2, 1, 1)
        plt.plot(self.data['prices'], label='Price', color='blue')
        plt.title('Trading Performance')
        plt.ylabel('Price')
        plt.legend()

        # Plotting rewards
        plt.subplot(2, 1, 2)
        plt.plot(self.data['rewards'], label='Reward', color='green')
        plt.xlabel('Step')
        plt.ylabel('Reward')
        plt.legend()

        plt.tight_layout()
        plt.show()

    def print_summary(self):
        print("Total Cumulative Reward:") #, self.data['cumulative_rewards'])
        # Add more summaries as needed

    def get_total_reward(self):
        return self.data['cumulative_rewards_const']

    def end_episode(self):
        self.plot_trading_results()
'''