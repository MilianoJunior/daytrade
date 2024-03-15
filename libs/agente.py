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
        self.explore_rate = 0.1

        # Inicializa a política de exploração
        if not self.policy == 'random':

            # Inicializa a política de exploração
            self.model = self._build_model()


    def _build_model(self):
        ''' Seleciona a política de exploração'''

        model = tf.keras.Sequential([
            layers.Dense(64, activation='relu', input_shape=(9,)),  # 9 entradas correspondendo aos seus recursos
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

        # print('Estado atual: ', state)

        # Política de exploração Greedy
        action_probabilities = self.model.predict(state.reshape(1, -1), verbose=0)

        # print('Probabilidades das ações: ', action_probabilities[0])

        return np.argmax(action_probabilities[0])  # Exploração


    def train(self, data):
        ''' Treina o modelo com base nas experiências'''
        # state, action, reward, next_state
        for state, action, reward, next_state in data:
          target_f = self.equacao_bellman(state, action, reward, next_state)

          self.model.fit(state[None, :], target_f, epochs=1, verbose=0)

    def equacao_bellman(self, state, action, reward, next_state):
        ''' Calcula a equação de Bellman com ajustes.'''
        print('-------------------' * 5)
        # print('Estado: ', state)
        # print('Ação: ', action)
        # print('Recompensa: ', reward)
        # print('Próximo estado: ', next_state)

        # Verifique se algum dos estados ou a recompensa contém NaN ou infinito
        if np.any(np.isnan(state)) or np.any(np.isnan(next_state)) or np.isnan(reward):
            print("Existem valores NaN nos estados ou na recompensa.")
            return None

        proximo = next_state[None, :]

        print('none: ', next_state[None, :])
        previsao = self.model.predict(proximo)
        print('Previsão 1: ', previsao)
        next = np.argmax(previsao)

        print('Next: ', next)
        if np.any(np.isnan(next)) or np.any(np.isinf(next)):
            print("Existem valores NaN ou infinitos nos próximos estados.")
            return random.choice([0, 1, 2])

        target = reward + self.explore_rate * np.amax(next)

        print('Target: ', target)
        target_f = self.model.predict(proximo)
        print('Target_f 1: ', target_f)
        # Calcula valor_1 baseado no target, considerando a condição de valores negativos
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

        return target_f


        # Ajuste da taxa de exploração, se necessário
        self.explore_rate *= 0.995

        print('Target_f: ', target_f)

        return target_f

        '''
        resultado:
            Estado:  [1.7080741e+09 1.3022500e+05 1.3023500e+05 1.3022500e+05 6.0000000e+00
            1.7080741e+12 6.0000000e+00 6.0000000e+00 1.0000000e+01]
            Ação:  0
            Recompensa:  35.0
            Próximo estado:  [1.7080741e+09 1.3023000e+05 1.3023500e+05 1.3023500e+05 1.0000000e+00
            1.7080741e+12 2.0000000e+00 1.0000000e+00 5.0000000e+00]
            Target:  nan
            
            1/1 [==============================] - 0s 13ms/step
            1/1 [==============================] - 0s 13ms/step
            Target_f:  [[nan nan nan]]

        '''
    # def equacao_bellman(self, state, action, reward, next_state):
    #     ''' Calcula a equação de Bellman'''
    #
    #     print('Estado: ', state)
    #     print('Ação: ', action)
    #     print('Recompensa: ', reward)
    #     print('Próximo estado: ', next_state)
    #
    #     target = reward  # Se o estado é terminal
    #     # Prever o valor Q futuro para o próximo estado e tomar a ação de maior valor
    #     target = reward + self.explore_rate * np.amax(self.model.predict(next_state[None, :])[0])\
    #
    #     print('Target: ', target)
    #     # Prever os valores Q para o estado atual
    #     target_f = self.model.predict(state[None, :])
    #     # Atualizar o valor alvo para a ação tomada
    #     target_f[0][action] = target
    #
    #     self.explore_rate *= 0.995  # Decaimento da taxa de exploração
    #
    #     print('Target_f: ', target_f)
    #
    #
    #     return target_f





