user = 'postgres'
password = 'Dragonicknight10145!'
host = 'localhost'
port = '5432'
database = 'test'

connection_str = f'postgresql:// {user}:{password}@{host}:{port}/{database}'

print(connection_str)