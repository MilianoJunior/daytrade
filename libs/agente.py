# Importando as bibliotecas
import tensorflow as tf
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers
import numpy as np
import os

class Agente:
    def __init__(self, policy='random'):
        '''
            Classe Agente com rede neural para tomar decisões de trading.
            Política de exploração:
                                    - Rondomico;
                                    - Greedy;
        '''
        # Parâmetros de exploração
        self.policy = policy

        # Inicializa a política de exploração
        if not self.policy == 'random':

            # Inicializa a política de exploração
            self.model = self._build_model()


    def _build_model(self):
        ''' Seleciona a política de exploração'''

        # Política de exploração randômica
        model = tf.keras.Sequential([
            layers.Dense(64, activation='relu', input_shape=(6,)),
            layers.Dense(32, activation='relu'),
            layers.Dense(3, activation='softmax')  # Saída para 3 ações: comprar, vender, manter
        ])
        model.compile(optimizer='adam', loss='categorical_crossentropy')

        return model

    def decide_action(self, state):
        ''' Decide a ação a ser tomada com base no estado atual'''

        if self.policy == 'random':
            return np.random.randint(3)

        # Política de exploração Greedy
        action_probabilities = self.model.predict(state.reshape(1, -1), verbose=0)

        return np.argmax(action_probabilities[0])  # Exploração


    def train(self, states, actions):
          ''' Treina o modelo com base nas experiências'''

          self.model.fit(states, actions, epochs=1, verbose=0)






