import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os

# --- 1. Configuração da Página ---
st.set_page_config(
    page_title="Tour4Friends - Recomendador AI",
    page_icon="✈️",
    layout="centered"
)

# --- 2. Função para carregar os modelos ---
@st.cache_resource
def carregar_modelos():
    diretorio_atual = os.path.dirname(__file__)
    
    with open(os.path.join(diretorio_atual, 'modelo_knn.pkl'), 'rb') as f:
        modelo = pickle.load(f)
        
    with open(os.path.join(diretorio_atual, 'matriz_knn.pkl'), 'rb') as f:
        matriz = pickle.load(f)
        
    return modelo, matriz

modelo_knn, matriz_knn = carregar_modelos()

# --- 3. Cabeçalho do App ---
st.title("✈️ Motor de Recomendação Inteligente")
st.markdown("""
**Bem-vindo ao sistema preditivo da Tour4Friends!** Este módulo utiliza Inteligência Artificial (Algoritmo KNN) para analisar o comportamento da base de clientes e sugerir viagens altamente personalizadas baseadas em similaridade de perfis.
""")
st.divider()

# --- 4. Interface de Seleção ---
st.subheader("👤 Seleção de Cliente")
lista_clientes = matriz_knn.index.tolist()

cliente_alvo = st.selectbox("Escolha o cliente para gerar a previsão:", lista_clientes)

if st.button("Gerar Recomendação Mágica ✨", type="primary"):
    
    with st.spinner('A IA está analisando milhões de combinações...'):
        # --- 5. Lógica de Machine Learning ---
        # 1. Pegar dados do cliente
        dados_cliente = matriz_knn.loc[[cliente_alvo]]
        
        # 2. Achar vizinhos
        distancias, indices = modelo_knn.kneighbors(dados_cliente)
        ids_vizinhos = matriz_knn.index[indices[0][1:]] # Pula ele mesmo
        
        # 3. Histórico de viagens do cliente alvo
        roteiros_feitos = matriz_knn.columns[matriz_knn.loc[cliente_alvo] > 0].tolist()
        
        # 4. Média dos vizinhos (AQUI ESTÁ A CORREÇÃO DO PROFESSOR)
        notas_vizinhos = matriz_knn.loc[ids_vizinhos]
        
        # Substituímos os 0 por 'NaN' (nulo). O Pandas ignora 'NaN' ao fazer a média!
        # Depois de fazer a média, preenchemos os vazios que restaram de volta com 0.
        media_vizinhos = notas_vizinhos.replace(0, np.nan).mean(axis=0).fillna(0)
        
        # 5. Separar Inéditos vs Repetidos
        recomendacoes_ineditas = media_vizinhos.drop(roteiros_feitos, errors='ignore').sort_values(ascending=False)
        top_ineditas = recomendacoes_ineditas[recomendacoes_ineditas > 0].head(2)
        
        # --- 6. Exibição dos Resultados ---
        st.success("Análise concluída com sucesso!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎒 Histórico do Cliente")
            st.caption("Destinos que já conhece:")
            if roteiros_feitos:
                for roteiro in roteiros_feitos:
                    st.write(f"- {roteiro}")
            else:
                st.write("- Cliente sem viagens registradas.")

        with col2:
            st.markdown("### 🎯 Sugestão da I.A.")
            st.caption("Próximo destino ideal:")
            
            if not top_ineditas.empty:
                for roteiro, score in top_ineditas.items():
                    st.info(f"**{roteiro}**\n\n*(Score de Afinidade: {score:.1f}/10)*")
            else:
                st.warning("Sem destinos inéditos disponíveis. Sugestão de Repetição (Up-sell):")
                top_repetidos = media_vizinhos.sort_values(ascending=False).head(2)
                for roteiro, score in top_repetidos.items():
                    if score > 0:
                        st.info(f"**{roteiro}**\n\n*(Score de Afinidade: {score:.1f}/10)*")

st.divider()
st.caption("Desenvolvido para o Projeto Integrador | Motor: Scikit-Learn")