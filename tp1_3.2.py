# Parser

from parser import DatasetParser
from seeder import DatabaseSeeder
from loadenv import load_connection_string_from_env

conn_string = load_connection_string_from_env()

print('[AVISO] Lendo dados')
dataset = DatasetParser().load_dataset()
print('[AVISO] Dados lidos')

seeder = DatabaseSeeder(conn_string)
seeder.populate_database(dataset)
seeder.close()

print('Os dados foram armazenados com sucesso')
