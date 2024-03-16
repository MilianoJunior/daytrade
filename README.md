# Algoritmo de Trading

Este projeto implementa um algoritmo de trading usando aprendizado por reforço.

## Descrição

Aprendizado por reforço

    1 - Agente: O trader (ou o algoritmo de trading) é o agente.
    2 - Ambiente: O mercado de ações, com todas as suas variações e movimentos, representa o ambiente.
    3 - Ações: Comprar, vender ou manter ações são as ações que o trader pode tomar.
    4 - Estado: O estado atual do mercado, incluindo informações como preço das ações, volume, notícias relevantes, etc.
    5 - Recompensa: O lucro ou prejuízo resultante das ações do trader.

## Objetivo

O algoritmo de trading é construído usando a biblioteca TensorFlow e o ambiente de negociação B3. O algoritmo é treinado para tomar decisões de compra e venda com base em dados históricos.

## Instalação

Para instalar as dependências necessárias, execute o seguinte comando:

```bash
pip install -r requirements.txt
```

## Mapeando Estados e Ações para o Ambiente de Negociação

O ambiente de negociação é mapeado para um espaço de estados e ações. 


## Métricas de Avaliação

A métrica mais comum usada para avaliar uma política é o retorno médio. O retorno é a soma das recompensas obtidas durante a execução de uma política em um ambiente para um episódio, e normalmente fazemos a média disso em alguns episódios. Podemos calcular a métrica de retorno médio da seguinte maneira.


![resultados](https://github.com/MilianoJunior/daytrade/blob/main/resultado.png)

## Referências

- [Tf-Agents](https://www.tensorflow.org/agents/tutorials/6_reinforce_tutorial?hl=pt-br#metrics_and_evaluation)
- [Reinforcement Learning for Trading](https://www.amazon.com/Reinforcement-Learning-Trading-Strategies-Implementing/dp/180107970X)