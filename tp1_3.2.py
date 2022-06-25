# Parser

from parser import DatasetParser
from seeder import DatabaseSeeder


conn_string = 'user=postgres password=db host=localhost port=1999 dbname=bdtp1'

print('[AVISO] Lendo dados')
dataset = DatasetParser().load_dataset()
print('[AVISO] Dados lidos')

seeder = DatabaseSeeder(conn_string)
seeder.populate_database(dataset)
seeder.close()

print('Os dados foram armazenados com sucesso')
