# Bitcoin-like-Blockhain

Implementação de um sistema distribuído de criptomoeda inspirado no Bitcoin.

# Equipe

* Igor Matthews Paixão Ferreira

# Objetivo

Sistema distribuído onde cada nó mantém uma cópia local da blockchain, comunicando-se via sockets com serialização JSON e utilizando Proof of Work simplificado.

# Estrutura do Projeto

# Instalar dependências
uv sync

# Executar nó
uv run python main.py --port 5000 --bootstrap localhost:5001
