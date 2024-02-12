# Importando as bibliotecas
import tensorflow as tf
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers
import numpy as np
import os
import MetaTrader5 as mt5
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

class Agente:
    def __init__(self):
        # Inicializa a rede neural
        self.model = self._build_model()
        self.eplison = 1.0  # Probabilidade de explorar
        self.gamma = 0.95  # Fator de desconto
        self.epsilon_min = 0.01  # Probabilidade mínima de explorar

        # Histórico de trading
        self.history = {
            'actions': [],
            'gained_points': [],
            'lost_points': [],
            'cumulative_gained': 0,
            'cumulative_lost': 0
        }

    def _build_model(self):
        # Cria uma rede neural simples
        model = tf.keras.Sequential([
            layers.Dense(64, activation='relu', input_shape=(6,)),  # Exemplo de entrada com 6 características
            layers.Dense(32, activation='relu'),
            layers.Dense(3, activation='softmax')  # Saída para 3 ações: comprar, vender, manter
        ])
        model.compile(optimizer='adam', loss='categorical_crossentropy')
        return model

    def decide_action(self, state):
        if np.random.rand() <= self.eplison:
            return np.random.randint(3)  # Exploração
        action_probabilities = self.model.predict(state.reshape(1, -1), verbose=0)
        return np.argmax(action_probabilities[0])  # Exploração

    def _update_history(self, action, gained_points, lost_points):
        self.history['actions'].append(action)
        self.history['gained_points'].append(gained_points)
        self.history['lost_points'].append(lost_points)
        self.history['cumulative_gained'] += gained_points
        self.history['cumulative_lost'] += lost_points
    # def decide_action(self, state):
    #     # Faz a previsão da ação baseada no estado atual
    #     action_probabilities = self.model.predict(state.reshape(1, -1), verbose=0)
    #     action = np.argmax(action_probabilities[0])
    #
    #     # Atualiza o histórico
    #     # self._update_history(action)
    #
    #     return action

    def train(self, states, actions):
        # Convert actions to one-hot encoding
        actions_one_hot = tf.keras.utils.to_categorical(actions, num_classes=3)

        # Train the model
        self.model.fit(states, actions_one_hot, epochs=10, verbose=0)

    # def _update_history(self, action):
    #     # Atualizar o histórico com a ação e resultados (exemplo simplificado)
    #     self.history['actions'].append(action)
    #     # Aqui você adicionaria a lógica para calcular os pontos ganhos/perdidos

    def print_history(self):
        # Imprime o histórico de trading
        print("Histórico de Trading:")
        for key, value in self.history.items():
            print(f"{key}: {value}")






if __name__ == '__main__':



    # # Criando o modelo
    model = AgenteSimples(3)
    # Número de ações possíveis (por exemplo, comprar, vender, manter)
    # num_actions = 3
    #
    # # Criar uma instância do agente
    # agente = AgenteSimples(num_actions)
    #
    # # Criar algumas observações fictícias (por exemplo, um vetor de 10 elementos)
    # observacoes_ficticias = np.random.rand(1, 10)  # 1 lote de observações com 10 elementos
    #
    # # Passar as observações para o agente e obter a saída
    # saida = agente(observacoes_ficticias)
    #
    # print("Saída do Agente:", saida.numpy())

    # # Definindo a função de perda
    # loss_object = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
    #
    # # Definindo o otimizador
    # optimizer = tf.keras.optimizers.Adam(learning_rate=1e-3)
    #
    # # Definindo as métricas
    # train_loss = tf.keras.metrics.Mean(name='train_loss')
    # train_accuracy = tf.keras.metrics.SparseCategoricalAccuracy(name='train_accuracy')
    #
    # states = tf.random.uniform((1, 10))
    # labels = tf.random.uniform((1,), minval=0, maxval=3, dtype=tf.int32)
    #
    # # Definindo a função de treinamento
    # @tf.function
    # def train_step(states, labels):
    #     with tf.GradientTape() as tape:
    #         predictions = model(states)
    #         loss = loss_object(labels, predictions)
    #     gradients = tape.gradient(loss, model.trainable_variables)
    #     optimizer.apply_gradients(zip(gradients, model.trainable_variables))
    #
    #     train_loss(loss)
    #     train_accuracy(labels, predictions)
    #
    # # Treinando o modelo
    # train_step(states, labels)




