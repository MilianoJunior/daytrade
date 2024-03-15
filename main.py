import os, sys
import time

import pandas as pd
import numpy as np
import tensorflow as tf
from tabulate import tabulate
from dotenv import load_dotenv
from libs.venv import B3
from libs.agente import Agente
from libs.avaliacao import TradingDataStore

load_dotenv()

'''
    variáveis de ambiente
'''

SYSTEM_OPERACIONAL = os.name
BASE_DIR = os.getcwd()
os.environ['ROOT'] = BASE_DIR

'''
    configurações dos parâmetros
'''
config = {
        'login': os.getenv('LOGIN'),
        'password': os.getenv('PASSWORD'),
        'symbol': os.getenv('SYMBOL'),
        'policy': 'neural',                      # Modo do Agente (Rondomico, Modelo)
        'num_episodes': 1                      # Defina o número de episódios para treinamento
}
'''
    instanciar classes
'''

env = B3(config)                                # Simula o ambiente de negociação da bolsa de valores
agente = Agente(config)                # Instancia o agente de trading
avaliacao = TradingDataStore()

inicio = time.time()

# print(env.data.columns)
# print(env.data.values[-1])

# raise Exception('Erro ao processar o DataFrame: ')
for episode in range(0,config['num_episodes']):
    state = env.reset()                         # Inicializa o ambiente
    episode_reward = 0
    cont = 0
    cont2 = 0
    while True:
        action = agente.decide_action(state.observation)  # O agente decide a ação
        # action = agente.decide_action()
        next_state = env.step(action)  # Atualiza o ambiente com a ação do agente
        reward = next_state.reward  # Obtem a recompensa
        episode_reward += reward
        # print(action)
        # Armazena e avalia o desempenho
        avaliacao.record_step(state, action, next_state, reward, env.position, env.price_adquire, verbose=False)
        cont += 1

        if cont > 200 or cont2 > 10:
            print('Treinando...')
            cont = 0
            cont2 += 1
            print('Qtd : ',len(avaliacao.data))
            agente.train(avaliacao.data)
            avaliacao.data = []
            print(cont2,' - valor: ', avaliacao.position_data['acumulado'].values[-2])
            print('---'*20)
            avaliacao.plot_trading_results()
            # avaliacao.update_data_and_plot()
        if next_state.step_type == 2: # or cont > 2000:  # Verifica se o episódio terminou
            break
        state = next_state

    print(f'Episódio: {episode}, Recompensa Total: {avaliacao.position_data["resultado"].sum()}')
        # time.sleep(1)
    avaliacao.end_episode()  # Finaliza o episódio no sistema de avaliação
    break

# avaliacao.plot_trading_results()  # Plota os resultados do trading
print('Fim do treinamento')

# Usar tabulate para imprimir o DataFrame
# print(tabulate(avaliacao.position_data, headers='keys', tablefmt='psql'))
print(avaliacao.position_data.shape)
fim = time.time()
print(f'Tempo de execução: {fim - inicio} segundos')

# prin(env.data.values[0:10])
# raise SystemExit




