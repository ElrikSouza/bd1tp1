## Como executar a aplicação

```bash
docker-compose build
docker-compose run --rm bdtp1

# dentro do bash do container, agora os scripts podem ser rodados utilizando o postgres no outro container
python tp1_3.2.py
python tp1_3.3.py
```