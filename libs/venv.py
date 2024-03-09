import os
import time
import pandas as pd
import numpy as np
import tensorflow as tf
from tf_agents.environments import py_environment
from tf_agents.trajectories import time_step as ts
from tf_agents.specs import array_spec
from libs.mt5 import Dados
from libs.padroes import Padroes
from libs.utils import excluir_zeros, excluir_valores
from dotenv import load_dotenv

load_dotenv()


class B3(py_environment.PyEnvironment):
    def __init__(self, config: dict):
        '''
            Classe B3, que herda de py_environment.PyEnvironment. Já está pronta, com as seguintes características:
                # Especifica o espaço de ação e observação
                    self._action_spec = array_spec.BoundedArraySpec(
                        shape=(), dtype=np.int32, minimum=0, maximum=2, name='action') Posição do agente (0 = sem posição, 1 = comprado, 2 = vendido)
        '''
        super(B3, self).__init__()

        # aplicar configurações para o ambiente
        self.mode = config.get('mode', 'random')
        self.conti = 0
        print(config)
        if self.mode == 'random':
            try:
                self.data = Dados(config.get('login',False), config.get('password',False)).get_ticks(config.get('symbol',False), 16, 17, 2, 2024)
                self.data = excluir_zeros(self.data)
                self.data = excluir_valores(self.data)

            except Exception as e:
                print(e)
                # gerar dados aleatórios
                print('Erro ao buscar dados da B3. Gerando dados aleatórios.')
                self.data = Padroes().get_ticks()
        else:
            self.data = Dados(login, password).get_last_tick(config.get('symbol',False))
        # self.data.index = pd.to_datetime(self.data['time'], unit='s')
        # self.data = self.data.drop(columns=['time'])
        print(self.data.head(10))
        print('-' * 50)
        self.index = 0
        self.time_frame = 1

        # Especifica o espaço de ação e observação
        self._action_spec = array_spec.BoundedArraySpec(
            shape=(), dtype=np.int32, minimum=0, maximum=2, name='action')
        self._observation_spec = array_spec.ArraySpec(
            shape=(self.data.shape[1],), dtype=np.float32, name='observation')

        # Define o estado inicial e variáveis auxiliares
        self._episode_ended = False
        self._state = None
        self.position = 0
        self.price_adquire = 0
        self.price_despach = 0
        self.price_bid =  self.data.iloc[0]['ask']
        self.price_ask = self.data.iloc[0]['bid']
        self.volume = 0

    def action_spec(self):
        '''Retorna o espaço de ação'''

        return self._action_spec

    def observation_spec(self):
        '''Retorna o espaço de observação'''

        return self._observation_spec

    def _reset(self):
        '''Reseta o ambiente e retorna o estado inicial'''

        self.index = 0
        self._episode_ended = False
        self._state = 0
        self.position = 0
        numeric_data = self.data.select_dtypes(include=[np.number]).values[self.index]
        return ts.restart(np.array(numeric_data, dtype=np.float32))

    def _step(self, action):
        '''Aplica uma ação e retorna o novo estado, recompensa e se o episódio terminou. '''

        # Faz um filtro de ticks para o ambiente, dando o próximo _state caso o tick mude de valor ou o volume atinja um valor == 10 no mesmo tick
        while True:
            self._state = (self._state + self.time_frame) % len(self.data)
            ask = self.data.iloc[self._state]['ask']  # Preço que um vendedor está disposto a aceitar
            bid = self.data.iloc[self._state]['bid']  # Preço que um comprador está disposto a pagar
            self.conti += 1
            self.volume += self.data.iloc[self._state]['volume']
            if bid != self.price_bid or ask != self.price_ask: # or self.volume > 10:
                self.price_bid = bid
                self.price_ask = ask
                print(' '*20,'...'*20)
                print(' '*40,'conti: ',self.conti,'state: ',self._state, 'ask:', ask, ' bid:', bid, ' volume:', self.volume)
                print(' '*20,'...' * 20)
                self.conti = 0
                self.volume = 0
                break

            if self._state + self.time_frame >= len(self.data):
                self._episode_ended = True
                print('Episódio terminado')
                break

            # Atualiza o estado (aqui pode-se avançar no time frame)


            # if self._state % 10000 == 0:
            # print('...'*20, self._state, 'ask:', ask, ' bid:', bid)
            # print('...'*20, self._state, 'ask:', ask, ' bid:', bid) 1 - 119445 2 -

        # O último passo terminou o episódio. Chama reset para iniciar um novo episódio.
        if self._episode_ended:
            return self.reset()

        # calcula a recompensa
        recompensa = self._calcular_recompensa(action)



        # print('Índice:', self._state)
        # atualiza o estado do ambiente
        if self._state >= len(self.data) - self.time_frame:
            self._episode_ended = True
            print('Episódio terminado')

        # novo time_step com os dados do ambiente
        # numeric_data = self.data.select_dtypes(include=[np.number]).values[self._state]
        numeric_data = self.data.iloc[self._state]
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

                Tabela de ações
        position | action | recompensa      | price_adquire | preco_atual | position_next
        0        | 0      | 0               | 0             | 0           | 0
        0        | 1      | 0               | price_ask     | ask         | 1
        0        | 2      | 0               | price_bid     | bid         | 2
        1        | 0      | price_ask - bid | price_ask     | bid         | 1
        1        | 1      | price_ask - bid | 0             | bid         | 0
        1        | 2      | price_ask - bid | 0             | bid         | 0
        2        | 0      | ask - price_bid | price_bid     | ask         | 2
        2        | 1      | ask - price_bid | 0             | ask         | 0
        """

        recompensa = 0

        ask = self.data.iloc[self._state]['ask'] # Preço que um vendedor está disposto a aceitar
        bid = self.data.iloc[self._state]['bid'] # Preço que um comprador está disposto a pagar
        # print('...'*20, 'ask:', ask, ' bid:', bid)
        # Sem posição: Se a posição for 0, pode comprar, vender ou manter
        '''
        Considere as operações de compra e venda de ações. O agente pode comprar, vender ou manter a posição.

        ask: Preço que um vendedor está disposto a aceitar
        bid: Preço que um comprador está disposto a pagar
        last: Último preço negociado

        Se estou comprado, a recompensa é a diferença entre o preço de aquisição e o preço de venda.
        Se estou vendido, a recompensa é a diferença entre o preço de aquisição e o preço de compra.

        formulas para calcular a recompensa:
        
        comprar
            preco_adquire = ask
            recompensa = bid - preco_adquire
            
        vender
            preco_adquire = bid
            recompensa =  preco_adquire - ask

        comprado: recompensa = preço de venda - preço de aquisição
        vendido: recompensa = preço de aquisição - preço de compra
        '''
        if self.position == 0:
            if action == 0:
                self.position = action
                recompensa = 0
            elif action == 1:
                # se estiver comprando, o preço de aquisição é o ask
                self.position = action
                self.price_adquire = round(ask)
                recompensa = 0
            else:
                # se estiver vendendo, o preço de aquisição é o bid
                self.position = action
                self.price_adquire = round(bid)
                recompensa = 0
            return recompensa

        # Comprado: Se a posição for 1, pode manter ou vender
        elif self.position == 1:
            recompensa = bid - self.price_adquire
            if action == 0:
                self.position = 1
                # recompensa = self.price_adquire - ask

            elif action == 1:
                self.position = action
                # recompensa = self.price_adquire - ask
            else:
                self.position = 0
                # recompensa = self.price_adquire - ask
                self.price_adquire = 0
            return recompensa

        # Vendido: Se a posição for 2, pode manter ou comprar
        else:
            recompensa = self.price_adquire - ask
            if action == 0:
                self.position = 2
                # recompensa = bid - self.price_adquire
            elif action == 1:
                self.position = 0
                # recompensa = bid - self.price_adquire
                self.price_adquire = 0
            else:
                self.position = action
                # recompensa = bid - self.price_adquire
            return recompensa



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
    posicao_label = {0: 'Sem posição', 1: 'Comprado', 2: 'Vendido'}
    amb = B3()
    time_step = amb.reset()
    print('Time step:', time_step)
    for s in range(10):

        action = np.random.randint(3)
        next_time_step = amb.step(action)
        print('Índice:', amb._state)
        print('Posição:', posicao_label.get(amb.position))
        print('Ação:', action)
        print('Next time step:', next_time_step.observation)
        print('Soma das recompensas:', next_time_step.reward)
        print('valores: ', amb.data.iloc[amb._state])

        print('-' * 50)

'''
Considere as operações de compra e venda de ações. O agente pode comprar, vender ou manter a posição.

ask: Preço que um vendedor está disposto a aceitar
bid: Preço que um comprador está disposto a pagar
last: Último preço negociado

Se estou comprado, a recompensa é a diferença entre o preço de aquisição e o preço de venda.
Se estou vendido, a recompensa é a diferença entre o preço de aquisição e o preço de compra.

formulas para calcular a recompensa:

comprado: recompensa = preço de venda - preço de aquisição
vendido: recompensa = preço de aquisição - preço de compra
'''