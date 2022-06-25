# Documentação do esquema do Banco de Dados

O entregável 3.1 encontra-se [neste link](https://docs.google.com/document/d/1bF-TWEEsUA011RTdnttHzJeAWDIMohTXjU50wcl8ExM/edit#heading=h.kcdvtj28kjk1). Podemos versioná-lo diretamente neste repo quando ele ele estiver sem nenhum problema após revisão.

## Como rodar

```bash
docker-compose build
docker-compose run --rm bdtp1

# dentro do bash do container, agora os scripts podem ser rodados utilizando o postgres no outro container
python tp1_3.2.py
python tp1_3.3.py
```

## Diagrama do esquema do Banco de Dados

Para visualizar o diagrama, basta executar o comando:

```bash
sh open-diagram.sh
```

O hash que monta o diagrama está versionado em `docs/diagram-hash.txt`.

Os símbolos que representam as cardinalidades podem ser vistos [aqui](https://plantuml.com/ie-diagram)

## Containers

Iniciar os serviços:
```bash
docker-compose up -d
```

Parar os serviços:
```bash
docker-compose stop
```

Iniciar os serviços:
```bash
docker-compose down
```
