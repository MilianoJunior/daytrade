import os, sys
import pandas as pd
import numpy as np
import tensorflow as tf
from dotenv import load_dotenv
from libs.venv import B3
# from libs.agente import Agente
# from libs.avaliacao import TradingDataStore
# from libs.utils import tratar_dataframe

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

mode = 'rondom'

'''
instanciar classes
'''

env = B3()

raise Exception

agente = Agente()
avaliacao_agente = TradingDataStore()



def random_policy(obs):
    ''' Retorna uma ação aleatória '''
    return np.random.randint(obs)

def agente_policy(obs):
    ''' Retorna a ação do agente '''
    return agente.decide_action(obs)

num_episodes = 1  # Defina o número de episódios para treinamento

for episode in range(num_episodes):
    state = env.reset()  # Inicializa o ambiente
    episode_reward = 0
    cont = 0
    while True:
        # action = agente.decide_action(state.observation)  # O agente decide a ação
        action = np.random.randint(3)
        next_state = env.step(action)  # Atualiza o ambiente com a ação do agente
        reward = next_state.reward  # Obtem a recompensa
        episode_reward += reward

        # Armazena e avalia o desempenho
        avaliacao.record_step(state, action, next_state.observation, reward, env.position, verbose=False)
        cont += 1
        if next_state.step_type == 'TERMINAL' or cont > 20:  # Verifica se o episódio terminou
            break
        state = next_state
        print(cont, ' State: ', state.observation,' Preco Adq.: ',env.price_adquire, ' Ação: ', action, ' Recompensa: ', reward, ' Posição: ', env.position)

    print(f'Episódio: {episode}, Recompensa Total: {episode_reward}')
    avaliacao.end_episode()  # Finaliza o episódio no sistema de avaliação

avaliacao.plot_trading_results()  # Plota os resultados do trading

'''
Num GPUs Available:  1
[PhysicalDevice(name='/physical_device:GPU:0', device_type='GPU')]
2024-01-31 13:11:21.025131: I tensorflow/core/platform/cpu_feature_guard.cc:193] This TensorFlow binary is optimized with oneAPI Deep Neural Network Library (oneDNN) to use the following CPU instructions in performance-critical operations:  AVX AVX2
To enable them in other operations, rebuild TensorFlow with the appropriate compiler flags.
2024-01-31 13:11:21.532225: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1616] Created device /job:localhost/replica:0/task:0/device:GPU:0 with 3472 MB memory:  -> device: 0, name: NVIDIA GeForce RTX 3060 Laptop GPU, pci bus id: 0000:01:00.0, compute capability: 8.6
Verificando se o ambiente está funcionando corretamente...
Observação inicial: TimeStep(
{'discount': array(1., dtype=float32),
 'observation': array([6.2154e+01, 6.2200e+01, 6.2590e+01, 6.1925e+01, 1.3375e+07,
       1.1000e-01], dtype=float32),
 'reward': array(0., dtype=float32),
 'step_type': array(0)})
Ação aleatória: TimeStep(
{'discount': array(1., dtype=float32),
 'observation': array([6.2688e+01, 6.1900e+01, 6.2745e+01, 6.1900e+01, 1.0959e+07,
       8.6000e-01], dtype=float32),
 'reward': array(0., dtype=float32),
 'step_type': array(1)})

'''

# print('Entrada da rede neural:', agente.get_input(env.reset()))




'''
# definir hiperparâmetros
num_episodes = 1
batch_size = 32


# Continuando a partir da sua definição de hiperparâmetros
for episode in range(num_episodes):
    # Resetar o ambiente no início de cada episódio
    time_step = env.reset()
    avaliacao.start_episode()
    cont = 0

    while not time_step.is_last():
        cont += 1
        # Selecionar uma ação aleatória
        action = random_policy(3) # Considerando 3 ações: 0, 1, 2

        # Aplicar a ação ao ambiente e obter o próximo estado
        next_time_step = env.step(action)


        # Registrar a ação e o resultado no Avaliacao
        avaliacao.record_step(env._state,
                              action,
                              time_step.observation[0],
                              time_step.reward,
                              env.position)  # Assumindo que `current_position` está definido no seu ambiente

        # Atualizar o passo de tempo
        time_step = next_time_step

    # Finalizar o episódio
    avaliacao.end_episode()

    # Opcional: Exibir informações do episódio
    if episode % 100 == 0:
        print(f'Episódio {episode}: Recompensa Total = {avaliacao.get_total_reward()}')

# Após todos os episódios, mostrar os resultados
avaliacao.plot_trading_results()
avaliacao.print_summary()

'''









# def create_q_net(observation_spec, action_spec, fc_layer_params=(100,)):
#     # 1 Passo: Criando a rede Q
#     q_net = q_network.QNetwork(
#         observation_spec,
#         action_spec,
#         fc_layer_params=fc_layer_params)
#
#     return q_net
#
# def create_agent(env, q_net, action_spec):
#     # 2 Passo: Criando o agente
#     train_env = tf_py_environment.TFPyEnvironment(env)
#
#     optimizer = tf.compat.v1.train.AdamOptimizer(learning_rate=1e-3)
#
#     agent = dqn_agent.DqnAgent(
#                 env.time_step_spec(),
#                 env.action_spec(),
#                 q_network=q_net,
#                 optimizer=optimizer,
#                 td_errors_loss_fn=common.element_wise_squared_loss)
#
#     return agent
#
# def create_replay_buffer(agent, train_env, batch_size):
#     # 3 Passo: Criando o replay buffer
#     replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(
#         data_spec=agent.collect_data_spec,
#         batch_size=batch_size,
#         max_length=100000)
#
#     return replay_buffer


# def collect_data(environment, policy, buffer):
#     # 4 Passo: Criando o coletor de dados
#     time_step = environment.current_time_step()
#     action_step = policy.action(time_step)
#     next_time_step = environment.step(action_step.action)
#     traj = trajectory.from_transition(time_step, action_step, next_time_step)
#     buffer.add_batch(traj)

# Verifique se B3TradingEnv herda de py_environment.PyEnvironment
# assert issubclass(B3TradingEnv, py_environment.PyEnvironment)

# # Criação da instância do ambiente
# env_instance = B3TradingEnv(data)
#
# # Conversão para TFPyEnvironment
# train_env = tf_py_environment.TFPyEnvironment(env_instance)
#
#
# # 1. Converter o ambiente para TFPyEnvironment
# train_env = tf_py_environment.TFPyEnvironment(B3TradingEnv(data))
#
# # 2. Criar a rede Q, o agente e o replay buffer
# q_net = create_q_net(train_env.observation_spec(), train_env.action_spec())
# agent = create_agent(train_env, q_net, train_env.action_spec())
# replay_buffer = create_replay_buffer(agent, train_env, batch_size)
#
# # 3. Criar uma política aleatória
# random_policy = random_tf_policy.RandomTFPolicy(train_env.time_step_spec(), train_env.action_spec())
#
# # 4. Coletar dados usando a política aleatória
# def collect_data(environment, policy, buffer):
#     time_step = environment.current_time_step()
#     action_step = policy.action(time_step)
#     next_time_step = environment.step(action_step.action)
#     traj = trajectory.from_transition(time_step, action_step, next_time_step)
#     buffer.add_batch(traj)
#
# for episode in range(num_episodes):
#     while not train_env.current_time_step().is_last():
#         collect_data(train_env, random_policy, replay_buffer)
#     print('Episódio: ', episode)



# # 1 Passo: Criando a rede Q
# q_net = create_q_net(env.observation_spec(), env.action_spec())
#
# # 2 Passo: Criando o agente
# agent = create_agent(env, q_net, env.action_spec())
#
# # 3 Passo: Criando o replay buffer
# replay_buffer = create_replay_buffer(agent, env)
#
# # 4 Passo: Criando o coletor de dados
# random_policy = random_tf_policy.RandomTFPolicy(train_env.time_step_spec(), train_env.action_spec())
#
# for episode in range(10):  # Alterar para o número desejado de passos
#     # Coletar um episódio usando a política aleatória
#     collect_step(env, random_policy, replay_buffer)
#     print('Episódio: ', episode)

# for episode in range(num_episodes):
#     # Resetar o ambiente no início de cada episódio
#     train_agent(env, policy, buffer)



