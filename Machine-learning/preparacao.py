import pandas as pd

# 1. Carregando as 3 bases de dados
print("Carregando as bases de dados...")
df_clientes = pd.read_csv("clientes_expandido.csv")
df_reservas = pd.read_csv("reservas_viagens_expandido.csv")
df_satisfacao = pd.read_csv("satisfacao_clientes_expandido.csv")

# 2. Mesclando Satisfação com Reservas (para trazer a coluna 'roteiro')
print("Cruzando dados de satisfação e reservas...")
df_completo = pd.merge(
    df_satisfacao,
    df_reservas[['id_reserva', 'roteiro']],
    on='id_reserva',
    how='left'
)

# 3. Mesclando o resultado com Clientes (para trazer a coluna 'nome')
print("Adicionando os nomes dos clientes...")
df_completo = pd.merge(
    df_completo,
    df_clientes[['id_cliente', 'nome']],
    on='id_cliente',
    how='left'
)

# 4. Criando a coluna de identificação amigável (Ex: "CLI001 - Ana Lima")
df_completo['cliente_identificador'] = df_completo['id_cliente'] + " - " + df_completo['nome']

# 5. Transformando na matriz KNN (Pivot Table)
print("Gerando a matriz para o modelo KNN...")
# Usamos 'cliente_identificador' como índice em vez de apenas 'id_cliente'
matriz_knn = df_completo.pivot_table(
    index='cliente_identificador', 
    columns='roteiro',
    values='nota_roteiro',
    fill_value=0 # Preenche com 0 as viagens que o cliente ainda não fez
)

# 6. Salvando a matriz pronta
matriz_knn.to_csv("matriz_knn_pronta.csv")
print("Sucesso! Matriz 'matriz_knn_pronta.csv' gerada com nomes dos clientes.")