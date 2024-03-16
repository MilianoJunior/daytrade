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
        'login': os.getenv('LOGIN'),              # Login da corretora
        'password': os.getenv('PASSWORD'),        # Senha da corretora
        'symbol': os.getenv('SYMBOL'),            # Ativo a ser negociado
        'policy': 'neural',                       #  Modo do Agente (Rondomico, Modelo)
        'num_episodes': 1,                        # Defina o número de episódios para treinamento
        'batch_size': 32,                         # Tamanho do lote
}
'''
    instanciar classes
'''

# Instancia o ambiente de trading
env = B3(config)

# Instancia o agente de trading
agente = Agente(config)

# Instancia o sistema de avaliação
avaliacao = TradingDataStore()

inicio = time.time()

# Treinamento do agente
for episode in range(0,config['num_episodes']):

    # Inicializa o ambiente
    state = env.reset()

    # variáveis de controle
    counter = 0

    while True:

        # agente decide a ação {0: 'Manter', 1: 'Comprar', 2:'Vender'} a ser tomada com base no estado atual
        action = agente.decide_action(state.observation)

        # Atualiza o ambiente com a ação do agente
        next_state = env.step(action)

        # Obtem a recompensa
        reward = next_state.reward

        # Armazena as experiências do agente
        avaliacao.record_step(state, action, next_state, reward, env.position, env.price_adquire, verbose=False)

        # Treina o modelo com base nas experiências
        if config['batch_size'] < len(avaliacao.data):
            print('Treinando...')
            percentual = (env._state / len(env.data)) * 100
            print('index: ',env._state, 'faltante: ', env.data.shape[0] - env._state, 'percentual: ', percentual, '%')
            agente.train(avaliacao.data)
            avaliacao.data = []

            avaliacao.plot_trading_results(agente.explore_rate)
            # avaliacao.update_data_and_plot()
        if next_state.step_type == 2:
            break
        state = next_state

    counter += 1
    print(f'Episódio: {episode}, Recompensa Total: {avaliacao.position_data["resultado"].sum()}')

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




