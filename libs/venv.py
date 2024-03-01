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
from reforcing_learning.libs.mt5 import Dados
from reforcing_learning.libs.padroes import Padroes
import time
from dotenv import load_dotenv

load_dotenv()

clear = {
    'Demo': {
        'login': os.getenv('LOGIN'),
        'password': os.getenv('PASSWORD'),
        'server': os.getenv('SERVER'),
        'assinatura': os.getenv('ASSINATURA')
    },
}

cont = 0

interval_ms = 100
login = clear['Demo']['login']
password = clear['Demo']['password']
symbol = 'WINJ24'

def trata_dataframe(data):
    ''' Acrescenta as colunas de frequência e regularidade ao DataFrame '''

    # cria um objeto da classe Padroes
    padrao = Padroes()

    # cria as colunas de frequência e regularidade
    padrao.frequencia_hist(data)

    return data
class B3(py_environment.PyEnvironment):
    def __init__(self, mode = 'demo'):
        super(B3, self).__init__()

        self.mode = mode
        if self.mode == 'demo':
            self.data = Dados(login, password).get_ticks(symbol, 16, 17, 2, 2024)
            # self.data = trata_dataframe(self.data)
        else:
            self.data = Dados(login, password).get_last_tick(symbol)
        self.data.index = pd.to_datetime(self.data['time'], unit='s')
        self.data = self.data.drop(columns=['time'])
        print(self.data.head())
        print(self.data.shape)
        print(self.data.columns)

        # self.data = pd.DataFrame(columns=['time', 'bid', 'ask', 'last', 'volume', 'frequencia', 'regularidade','action', 'recompensa'])
        self.index = 0  # Mantém o índice do DataFrame
        self.time_frame = 1  # Time frame para as operações de day trade


        # Especifica o espaço de ação e observação
        self._action_spec = array_spec.BoundedArraySpec(
            shape=(), dtype=np.int32, minimum=0, maximum=2, name='action')
        self._observation_spec = array_spec.ArraySpec(
            shape=(self.data.shape[1],), dtype=np.float32, name='observation')

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
        print('Ação: ', action)
        # print('Data: ', data)
        print('Recompensa: ', recompensa)



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
        # price_ask = self.data.iloc[self._state]['ask']
        # price_bid = self.data.iloc[self._state]['bid']
        ask = self.data.iloc[self._state]['ask']
        bid = self.data.iloc[self._state]['bid']

        # preco_atual = round(self.data.iloc[self._state]['Último'] * 1000)
        # proximo_preco = self.data.iloc[(self._state + self.time_frame) % len(self.data)]['Último'] * 1000
        # data_atual = self.data.iloc[self._state]['time']
        # proxima_data = self.data.iloc[(self._state + self.time_frame) % len(self.data)]['time']

        def imprimir(state, posicao, acao, recompensa, price_adquire, preco_atual):
            estados = {0: 'Sem posição', 1: 'Comprado', 2: 'Vendido'}
            acoes = {0: 'Manter', 1: 'Comprar', 2: 'Vender'}

            print('State: ', state, ' - Posição: ', estados.get(posicao), '- Ação: ', acoes.get(action))
            print('Aquisição: ', price_adquire, '- Atual: ', preco_atual, '- recompensa: ', recompensa)
            print('_' * 100)
        '''
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
        
        '''
        # Sem posição: Se a posição for 0, pode comprar, vender ou manter
        if self.position == 0:
            if action == 0:
                self.position = action
                recompensa = 0
            elif action == 1:
                self.position = action
                self.price_adquire = round(ask)
                recompensa = 0
            else:
                self.position = action
                self.price_adquire = round(bid)
                recompensa = 0
            # imprimir(self._state, self.position, action, recompensa, self.price_adquire, preco_atual)
            return recompensa
        # Comprado: Se a posição for 1, pode manter ou vender
        elif self.position == 1:
            if action == 0:
                self.position = 1
                recompensa = self.price_adquire - bid
            elif action == 1:
                self.position = action
                recompensa = self.price_adquire - bid
            else:
                self.position = 0
                self.price_adquire = 0
                recompensa = self.price_adquire - bid
            # imprimir(self._state, self.position, action, recompensa, self.price_adquire, preco_atual)
            return recompensa

        # Vendido: Se a posição for 2, pode manter ou comprar
        elif self.position == 2:
            if action == 0:
                self.position = 2
                recompensa = ask - self.price_adquire
            elif action == 1:
                self.position = 0
                recompensa = ask - self.price_adquire
                self.price_adquire = 0
            else:
                self.position = action
                recompensa = ask - self.price_adquire
            # imprimir(self._state, self.position, action, recompensa, self.price_adquire, preco_atual)
            return recompensa

        # imprimir(self._state, self.position, action, recompensa, self.price_adquire, preco_atual)

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
    # Logar no MetaTrader 5
    clear = {
        'Demo': {
            'name': 'Metatrader 5 clear demo',
            'login': 1193393312,
            'password': '2718lej#JR4199',
            'server': 'ClearInvestimentos-DEMO',
            'assinatura': '35719726'
        },
        'Real': {
            'name': 'Metatrader 5 clear real',
            'login': '1000649229',
            'password': None,
            'server': 'ClearInvestimentos-CLEAR',
            'assinatura': '35719726'
        }

    }
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

    # O governo só age quando é pressionado. Temos que parar as empresas
    # Corte de gastos?
    # Santa Catarina tem apenas 1.6% de servidores públicos em relação à população ativa, paises desenvolvidos tem em média valores acima de 10%.
    #
    # Vamos questionar o governo sobre os gastos com servidores públicos em relação a arrecadação. Perdas salariais acima de 20% em relação a inflação.
    # # import mt5, MinhaThread
    # import os
    # print(os.getcwd())
    # from reforcing_learning.libs.mt5 import Dados
    # from reforcing_learning.libs.padroes import Padroes
    # import time
    #
    #
    # cont = 0
    #
    # interval_ms = 100
    # i = 0
    # segundos = 0
    # login = clear['Demo']['login']
    # password = clear['Demo']['password']
    # symbol = 'WINJ24'
    # conexao = Dados(login, password)
    # # amb = B3(conexao.get_ticks(symbol, 16, 17, 2, 2024))
    # # historico
    # historico = False
    # entrada = {
    #     'time': 0,
    #     'bid': 0,
    #     'ask': 0,
    #     'last': 0,
    #     'volume': 0,
    #     'frequencia': 0,
    #     'regularidade': 0,
    #
    # }
    #
    # if historico:
    #     conexao.get_symbol_info(symbol)
    #     # conexao.get_terminal_info()
    #     start_day, end_day, month, year = 16, 17 , 2, 2024
    #     # dias = conexao.get_days_in_month(month, year)
    #     for dia in range(start_day, end_day):
    #         print('                                ')
    #         print('Dia: ', dia)
    #         print('¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨')
    #         ticks = conexao.get_ticks(symbol, dia, dia + 1, month, year)
    #         padroes = Padroes()
    #         # padroes.frequencia(ticks)
    #         print(ticks)
    #         print(type(ticks))
    #         cont = 0
    #         print('                                ')
    #         while cont < 1:
    #             # print_progress(cont, ticks)  # Replace 'ticks' with your actual data
    #             freq, regularidade = padroes.frequencia(ticks.values[cont])
    #             print('Tick: ', cont, ' Falta: ', ticks.shape[0] - cont)
    #             print(' Time: ', ticks['time'][cont])
    #             print(' Bid: ', ticks['bid'][cont])
    #             print(' Ask: ', ticks['ask'][cont])
    #             print(' Last: ', ticks['last'][cont])
    #             print(' Volume: ', ticks['volume'][cont])
    #             print(' Frequência: ', freq[0])
    #             print(' Regularidade: ', regularidade[0])
    #             print('                               ')
    #             # print('                               ', flush=True)
    #             entrada['time'] = ticks['time'][cont]
    #             entrada['bid'] = ticks['bid'][cont]
    #             entrada['ask'] = ticks['ask'][cont]
    #             entrada['last'] = ticks['last'][cont]
    #             entrada['volume'] = ticks['volume'][cont]
    #             entrada['frequencia'] = freq[0]
    #             entrada['regularidade'] = regularidade[0]
    #
    #
    #             cont += 1
    #             time.sleep(0.5)
    #             os.system('cls' if os.name == 'nt' else 'clear')
    # else:
    #     padroes = Padroes()
    #     aux = {
    #         'bid': 0,
    #         'ask': 0,
    #         'last': 0,
    #         'volume': 0,
    #     }
    #     while cont < 100:
    #         last_tick = conexao.get_last_tick(symbol)
    #         if last_tick is None:
    #             continue
    #
    #         if last_tick['ask'] != aux['ask'] and last_tick['bid'] != aux['bid'] and last_tick['last'] != aux['last'] and last_tick['volume'] != aux['volume']:
    #             aux = last_tick
    #             cont += 1
    #             print('Novo tick', cont)
    #             freq, regularidade = padroes.frequencia(last_tick)
    #             print('                                ')
    #             print(cont)
    #             print('Último tick: ', last_tick)
    #             print('Time: ', last_tick['time'])
    #             print('Bid: ', last_tick['bid'])
    #             print('Ask: ', last_tick['ask'])
    #             print('Last: ', last_tick['last'])
    #             print('Volume: ', last_tick['volume'])
    #             print('Frequência: ', freq[0])
    #             print('Regularidade: ', regularidade[0])
    #             print('                               ')
    #             entrada['time'] = last_tick['time']
    #             entrada['bid'] = last_tick['bid']
    #             entrada['ask'] = last_tick['ask']
    #             entrada['last'] = last_tick['last']
    #             entrada['volume'] = last_tick['volume']
    #             entrada['frequencia'] = freq[0]
    #             entrada['regularidade'] = regularidade[0]
    #
    #
    #         # else:
    #         #     cont += 1
    #         #     print('Tick repetido', cont)
    #         time.sleep(0.1)
        # while cont < 100: # (ticks.shape[0] - 1):
        #     print('                                ', end='')
        #     print('Tick: ', cont, ' Falta: ', ticks.shape[0] - cont, end='')
        #     print(' Time: ', ticks['time'][cont], end='')
        #     print(' Bid: ', ticks['bid'][cont], end='')
        #     print(' Ask: ', ticks['ask'][cont], end='')
        #     print(' Last: ', ticks['last'][cont], end='')
        #     print(' Volume: ', ticks['volume'][cont], end='')
        #     print('                               ', end='')
        #     # texto = ' '
        #     # texto = 'Tick: ' + str(cont) + ' Falta: ' + str(ticks.shape[0] - cont)
        #     # texto +=
        #     # for name in ticks.columns:
        #     #     texto += ' ' * 10 + name + ' ' + str(ticks[name][cont])
        #     # print(texto, end='')
        #     print('\b'*100, end='', flush=True)
        #         # print(' ' * 10, name, ticks[name].values[-1])
        #     # print(' ' * 10, '------------------------', end='', flush=True)
        #     cont += 1
        #     time.sleep(0.1)
        # print(' ' * 10, '------------------------', end='', flush=True)
            # time.sleep(1)
            # cont += 1
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


'''

'''
'''
Prompt: 
De acordo com a documentação do MetaTrader 5, como obtenho o ultimo tick de um ativo que não seja repetido?
https://www.mql5.com/pt/docs/python_metatrader5

se puder fazer uma função que retorne o último tick de um ativo, eu agradeço.

'''
'''
class B3(py_environment.PyEnvironment):
    def __init__(self,data, time_frame=1):
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
'''
'''
tenho os seguintes dados:

# ug01_nivel_agua, data_hora
'1138940000', '2024-02-19 14:22:45'
'1138940000', '2024-02-19 14:21:45'
'1138950000', '2024-02-19 14:20:45'
'1138950000', '2024-02-19 14:19:45'
'1138950000', '2024-02-19 14:18:45'
'1138950000', '2024-02-19 14:17:45'
'1138950000', '2024-02-19 14:16:45'
'1138950000', '2024-02-19 14:15:44'
'1138950000', '2024-02-19 14:14:44'
'1138960000', '2024-02-19 14:13:44'

E preciso converter os dados da coluna ug01_nivel_agua para float por que eles vieram de um supervisorio como 32 bit signed, 
agora eu ajustei para 32 bit float, mas preciso converter os dados para float, como faço isso?

os dados salvos agora estão assim, no formato correto:

# ug01_nivel_agua, data_hora
'453.157', '2024-02-19 14:28:46'
'453.138', '2024-02-19 14:27:46'
'453.345', '2024-02-19 14:26:46'

Tem que ser por comando do mysql

'''
'''
entendeu errado, os dados salvos no banco de dados estavam como 32 bit signed, agora eu ajustei para 32 bit float,
mas para não perder os dados, preciso converter os dados da coluna ug01_nivel_agua para 32 bit float, como faço isso?

'''

'''

O Governo de Santa Catarina lançou recentemente o "Recupera Mais",que gera descontos de até 95% no ICMS de empresas

'''
'''
Com inflação acumulada de 20% nos últimos 3 anos, 
dá para gastar $ 4.000,00 por mês com uniformes.

'''
'''


'''