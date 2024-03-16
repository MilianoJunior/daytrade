# Importando as bibliotecas
import tensorflow as tf
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers
import numpy as np
import os
import random

class Agente:
    def __init__(self, config):
        '''
            Classe Agente com rede neural para tomar decisões de trading.
            Política de exploração:
                                    - Rondomico;
                                    - Greedy;
        '''
        # Parâmetros de exploração
        self.policy = config['policy']

        # Taxa de exploração
        self.explore_rate = 0.98

        # Inicializa a política de exploração
        if not self.policy == 'random':

            # Inicializa a política de exploração
            self.model = self._build_model()


    def _build_model(self):
        ''' Seleciona a política de exploração'''

        model = tf.keras.Sequential([
            layers.Dense(64, activation='relu', input_shape=(6,)),  # 9 entradas correspondendo aos seus recursos
            layers.Dense(32, activation='relu'),
            layers.Dense(3, activation='linear')  # Saída para os valores Q de 3 ações: comprar, vender, manter
        ])

        model.compile(optimizer='adam', loss='mse')

        return model

    def decide_action(self, state):
        ''' Decide a ação a ser tomada com base no estado atual'''

        if self.policy == 'random':
            return np.random.randint(3)

        if self.explore_rate > np.random.rand():
            return np.random.randint(3)

        # Política de exploração Greedy
        action_probabilities = self.model.predict(state.reshape(1, -1), verbose=0)


        return np.argmax(action_probabilities[0])  # Exploração


    def train(self, data, verbose=False):
        ''' Treina o modelo com base nas experiências'''
        # state, action, reward, next_state
        for state, action, reward, next_state in data:
          target_f = self.equacao_bellman(state, action, reward, next_state)
          if verbose:
              print('......' * 20)
              print('Target_f 2: ', target_f.reshape(1, -1))
              print('state: ', state[None, :])
              print('Reward: ', reward)
          self.model.fit(state[None, :], target_f.reshape(1, -1), epochs=1, verbose=verbose)

    def equacao_bellman(self, state, action, reward, next_state):
        ''' Calcula a equação de Bellman com ajustes.'''

        # Verifique se algum dos estados ou a recompensa contém NaN ou infinito
        if np.any(np.isnan(state)) or np.any(np.isnan(next_state)) or np.isnan(reward):
            print("Existem valores NaN nos estados ou na recompensa.")
            return None

        previsao = self.model.predict(next_state[None, :], verbose=0)

        next = np.argmax(previsao)

        if np.any(np.isnan(next)) or np.any(np.isinf(next)):
            print("Existem valores NaN ou infinitos nos próximos estados.")
            next = random.choice([0, 1, 2])

        target = reward + self.explore_rate * np.amax(next)


        valor_1 = target / 100

        # Garante que valor_2 seja sempre maior que valor_1 e menor que 1
        valor_2 = random.uniform(max(valor_1, 0), 1)

        # Calcula valor_3 para garantir que a soma de valor_1, valor_2 e valor_3 seja 1
        valor_3 = 1 - (valor_1 + valor_2)

        # Prepara a estrutura para alocação dos valores calculados
        casa = [0, 1, 2]
        target_f = np.zeros(3)  # Inicializa com zeros

        # Atribui os valores calculados às posições correspondentes
        index0 = action
        casa.remove(index0)
        index1 = random.choice(casa)
        casa.remove(index1)
        index2 = casa[0]

        # Atribuição dos valores calculados para cada posição
        target_f[index0] = valor_1
        target_f[index1] = valor_2
        target_f[index2] = valor_3

        # Ajuste da taxa de exploração, se necessário
        self.explore_rate -= 0.001

        return target_f





