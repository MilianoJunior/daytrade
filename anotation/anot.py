'''
Preciso que implemente um algoritmo de trading usando aprendizado por reforço. Com as seguintes características:

Resumo:

     A implementação de um algoritmo de trading usando aprendizado por reforço, com as seguintes características:
        - O agente (trader) deve tomar ações de compra, venda ou manutenção de ações.
        - O ambiente é o mercado de ações, com todas as suas variações e movimentos.
        - O estado atual do mercado, incluindo informações como preço das ações, volume, notícias relevantes, etc.
        - O objetivo do trader é maximizar a recompensa total ao longo do tempo.
     Libs usadas:
        - TensorFlow
        - Pandas
        - Numpy
        - Matplotlib
        - TF-Agents
        - MetaTrader 5

Aprendizado por reforço

    1 - Agente: O trader (ou o algoritmo de trading) é o agente.
    2 - Ambiente: O mercado de ações, com todas as suas variações e movimentos, representa o ambiente.
    3 - Ações: Comprar, vender ou manter ações são as ações que o trader pode tomar.
    4 - Estado: O estado atual do mercado, incluindo informações como preço das ações, volume, notícias relevantes, etc.
    5 - Recompensa: O lucro ou prejuízo resultante das ações do trader.

    O objetivo do trader é maximizar a recompensa total ao longo do tempo.

    Solução:
        1 - Criar um ambiente de trading.
            Classe B3, que herda de py_environment.PyEnvironment. Já está pronta, com as seguintes características:
             # Especifica o espaço de ação e observação
                self._action_spec = array_spec.BoundedArraySpec(
                    shape=(), dtype=np.int32, minimum=0, maximum=2, name='action') Posição do agente (0 = sem posição, 1 = comprado, 2 = vendido)
                self._observation_spec = array_spec.ArraySpec(
                    shape=(data.shape[1],), dtype=np.float32, name='observation')
                    # _observation_spec:  dados que serão passados para a rede neural (neste caso, o preço de abertura, fechamento, máxima e mínima, volume e variação)
                    "Data","Último","Abertura","Máxima","Mínima","Vol.","Var%"
                    "19.01.2024","128.250","128.690","128.855","127.320","15,15M","0,16%"
         # metodos: _reset, _step, action_spec, observation_spec, _calcular_recompensa

        2 - Criar um agente de trading.
            Classe Agente, rede neural simples para tomar decisões. Precisa de implementacao, com os requisitos:
                - A cada interacao, e retornado e imprimido os valores: Acao, Pontos ganhos, pontos perdidos, soma dos pontos ganhos e soma dos pontos perdidos.

        3 - Classe Avaliacao.
            Classe Avaliacao, para armazenar as experiências do agente e plotar os resultados. Já está pronta, com as seguintes características:
                - metodos: record_step, start_episode, end_episode, plot_trading_results, print_summary, get_total_reward
                - record_step(self, state, action, price, reward, position, verbose=False):
                self.data = {
                            'actions': [],
                            'prices': [],
                            'rewards': [],
                            'positions': [],
                            'cumulative_rewards_const': 0,
                            'cumulative_rewards': []
                        }
                        self.cumulative_rewards = 0

    libs/
        ├── agente.py      # Classe Agente com rede neural
        ├── venv.py        # Classe B3, herda de py_environment.PyEnvironment
        ├── avaliacao.py   # Classe Avaliacão, para armazenar as experiências do agente e plotar os resultados
        └── utils.py       # Funções auxiliares, como processamento de dados
    ├── main.py            # Script principal para rodar o sistema

    Pode me fazer perguntas a qualquer momento, para confirmar se está no caminho certo.


'''