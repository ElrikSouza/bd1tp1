## Como executar a aplicação

```bash
# a build precisa de internet pois o processo de build vai baixar o dataset no container
docker-compose build
docker-compose run --rm bdtp1

# dentro do bash do container, agora os scripts podem ser rodados utilizando o postgres no outro container
python tp1_3.2.py
python tp1_3.3.py
```

## Observações Importantes

- A build precisa de internet já que precisa baixar o dataset
- O arquivo tp1_3.2.py foi dividido em outros arquivos
  - parser.py contém o parser e a classes DatasetParser e Dataset
  - entities.py contém classes para armazenar dados
  - seeder.py contém a classe que povoa o banco
  - loadenv.py contém uma única função que retorna a connection string do postgresql
