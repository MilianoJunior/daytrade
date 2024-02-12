import os
import time

import pandas as pd
import numpy as np
import tensorflow as tf
# import MetaTrader5 as mt5
# from libs.mt5 import Dados
from tf_agents.environments import py_environment
from tf_agents.trajectories import time_step as ts
from tf_agents.specs import array_spec




class B3(py_environment.PyEnvironment):
    def __init__(self, data, time_frame=1):
        super(B3, self).__init__()

        self.data = data # DataFrame processado
        self.index = 0  # Mantém o índice do DataFrame
        self.time_frame = time_frame  # Time frame para as operações de day trade


        # Especifica o espaço de ação e observação
        self._action_spec = array_spec.BoundedArraySpec(
            shape=(), dtype=np.int32, minimum=0, maximum=2, name='action')
        self._observation_spec = array_spec.ArraySpec(
            shape=(data.shape[1],), dtype=np.float32, name='observation')

        # Define o estado inicial e variáveis auxiliares
        self._episode_ended = False
        self._state = None
        self.position = 0  # Posição do agente (0 = sem posição, 1 = comprado, 2 = vendido)
        self.price_adquire = 0  # Preço de aquisição

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _reset(self):
        self.index = 0
        self._episode_ended = False
        self._state = 0
        numeric_data = self.data.select_dtypes(include=[np.number]).values[self.index]
        return ts.restart(np.array(numeric_data, dtype=np.float32))

    def _step(self, action):
        """
        Aplica uma ação e retorna o novo estado, recompensa e se o episódio terminou.
        """
        if self._episode_ended:
            print('Episódio terminado')
            # O último passo terminou o episódio. Chama reset para iniciar um novo episódio.
            return self.reset()

        # Aplica a ação (0 = manter, 1 = comprar, 2 = vender) e calcula a recompensa
        recompensa = self._calcular_recompensa(action)
        # print('Ação: ', action)
        # print('Recompensa: ', recompensa)


        # Atualiza o estado (aqui pode-se avançar no time frame)
        self._state = (self._state + self.time_frame) % len(self.data)

        if self._state >= len(self.data) - self.time_frame:
            self._episode_ended = True
            print('Episódio terminado')

        numeric_data = self.data.select_dtypes(include=[np.number]).values[self._state]

        # Retorna o novo time_step
        if self._episode_ended:
            return ts.termination(np.array(numeric_data, dtype=np.float32), recompensa)
        else:
            return ts.transition(np.array(numeric_data, dtype=np.float32), recompensa)


    # Método para calcular a recompensa
    def _calcular_recompensa(self, action):
        """
        Calcula a recompensa com base na ação e no estado atual.

        A recompensa é calculada pela variação dos pontos multiplicada pelo valor de cada ponto,
        que é R$0,20. Consideramos que o custo de cada operação é zero.

        :param action: A ação realizada pelo agente (0 = manter, 1 = comprar, 2 = vender).
        :return: A recompensa calculada.
        """
        valor_por_ponto = 0.20  # Valor de cada ponto no mini-índice
        recompensa = 0

        # Obter o preço atual e o próximo preço com base no time frame
        preco_atual = round(self.data.iloc[self._state]['Último'] * 1000)
        proximo_preco = self.data.iloc[(self._state + self.time_frame) % len(self.data)]['Último'] * 1000
        data_atual = self.data.iloc[self._state]['Data']
        proxima_data = self.data.iloc[(self._state + self.time_frame) % len(self.data)]['Data']

        def imprimir(state, posicao, acao, recompensa, price_adquire, preco_atual):
            estados = {0: 'Sem posição', 1: 'Comprado', 2: 'Vendido'}
            acoes = {0: 'Manter', 1: 'Comprar', 2: 'Vender'}

            print('State: ', state, ' - Posição: ', estados.get(posicao), '- Ação: ', acoes.get(action))
            print('Aquisição: ', price_adquire, '- Atual: ', preco_atual, '- recompensa: ', recompensa)
            print('_' * 100)

        # Sem posição: Se a posição for 0, pode comprar, vender ou manter
        if self.position == 0:
            self.position = action
            self.price_adquire = round(preco_atual)
            recompensa = 0
            # imprimir(self._state, self.position, action, recompensa, self.price_adquire, preco_atual)
            return recompensa

        # Comprado: Se a posição for 1, pode manter ou vender
        elif self.position == 1:
            if action == 2: # Se a ação for 2, vende
                self.position = 0
            # Calcular a recompensa para a posição comprada
            recompensa = round(preco_atual - self.price_adquire) # * valor_por_ponto)

        # Vendido: Se a posição for 2, pode manter ou comprar
        elif self.position == 2:
            if action == 1:   # Se a ação for 1, compra
                self.position = 0
            # Calcular a recompensa para a posição vendida
            recompensa = round(self.price_adquire - preco_atual) #* valor_por_ponto)

        # imprimir(self._state, self.position, action, recompensa, self.price_adquire, preco_atual)

        return recompensa



clear = {}


if __name__ == '__main__':
    '''
    Definição da lógica
    
        Agente: Rede neural.
        Ações: (0 = manter, 1 = comprar, 2 = vender).
        Recompensa: Variação do preço multiplicada pelo valor de cada ponto (R$0,20) menos o custo da operação.
        Estado: Posição ( Comprado, vendido ou sem posição).
        Ambiente: Processa os dados e aplica as ações do agente e retorna as observações e recompensa.
        Observação: É um vetor com o Preço de Fechamento, abertura, máxima, mínima, volume e variação.

     O objetivo é aprimorar a política de forma a maximizar a soma das recompensas (retorno).
    '''
    # Logar no MetaTrader 5
    import mt5

    interval_ms = 100
    i = 0
    segundos = 0
    login = clear['Demo']['login']
    password = clear['Demo']['password']
    symbol = 'WING24'
    conexao = mt5.Dados(login, password)
    conexao.get_symbol_info(symbol)
    # conexao.get_terminal_info()
    start_day, end_day, month, year = 20, 31, 1, 2024
    # dias = conexao.get_days_in_month(month, year)
    for dia in range(start_day, end_day):
        print('                                ')
        print('Dia: ', dia)
        print('¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨')
        ticks = conexao.get_ticks(symbol, dia, dia + 1, month, year)
        # print(ticks)
        if not ticks.empty:
            for name in ticks.columns:
                print(' ' * 10, name, ticks[name][0])
                print(' ' * 10, name, ticks[name].values[-1])
                print(' ' * 10, '------------------------')
    # print("Dispositivos disponíveis:", tf.config.list_physical_devices())
    # print("GPUs disponíveis:", tf.config.experimental.list_physical_devices('GPU'))
    # # 1 passo: Importar os dados
    # data = pd.read_csv('win_dia.csv')
    #
    # # 2 passo: Processar o DataFrame
    # data = tratar_dataframe(data)
    #
    # # 3 passo: Criar o ambiente
    # env = B3TradingEnv(data)
    #
    # # 4 passo: Testar o ambiente
    # inicio = time.time()
    # env.reset()
    # soma_recompensas = 0
    # for i in range(100):
    #     action = np.random.randint(3)
    #     next_time_step = env.step(action)
    #     soma_recompensas += next_time_step.reward
    #     # print('Próximo estado:', next_time_step)
    #     print('Soma das recompensas:', round(soma_recompensas))
    #     # print('Índice:', env.index)
    #     print('-' * 50)
    # print('Soma das recompensas:', round(soma_recompensas))
    # print('Tempo de execução:', round(time.time() - inicio),3)



