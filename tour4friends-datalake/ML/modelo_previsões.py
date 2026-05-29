import pandas as pd
from sklearn.neighbors import NearestNeighbors
import pickle
import os

print("1. Carregando a matriz KNN...")
# O index_col=0 garante que os IDs dos clientes fiquem no índice correto
caminho_matriz = os.path.join(os.path.dirname(__file__), 'matriz_knn_pronta.csv')
matriz_knn = pd.read_csv(caminho_matriz, index_col=0)

print("2. Treinando o modelo KNN (K=10)...")
modelo_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=10)
modelo_knn.fit(matriz_knn)

print("3. Serializando (salvando) o modelo e a matriz em Pickle...")
caminho_modelo = os.path.join(os.path.dirname(__file__), 'modelo_knn.pkl')
caminho_matriz_pkl = os.path.join(os.path.dirname(__file__), 'matriz_knn.pkl')

# Salvamos o modelo treinado
with open(caminho_modelo, 'wb') as arquivo_modelo:
    pickle.dump(modelo_knn, arquivo_modelo)

# Salvamos a matriz (o Streamlit vai precisar dela)
with open(caminho_matriz_pkl, 'wb') as arquivo_matriz:
    pickle.dump(matriz_knn, arquivo_matriz)

print("✅ Treinamento concluído! Arquivos .pkl gerados com sucesso na pasta ML.")