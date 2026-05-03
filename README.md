<div align="center">
  <img width="1112" height="266" alt="Tour4Friends Banner" src="https://github.com/user-attachments/assets/8a1c646f-c801-455b-8448-8c9c8ecc3c90" />

  # Tour4Friends Analytics — Data Lake

  ![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow)
  ![Python](https://img.shields.io/badge/Python-3.10-blue)
  ![MongoDB](https://img.shields.io/badge/MongoDB-NoSQL-green)
  ![Kafka](https://img.shields.io/badge/Apache-Kafka-black)
  ![AWS Glue](https://img.shields.io/badge/AWS-Glue_|_Spark-orange)
  ![AWS S3](https://img.shields.io/badge/AWS-S3_Lake-orange)
  ![PowerBI](https://img.shields.io/badge/Power_BI-Analytics-F2C811)

  > Projeto Integrador — Tour4Friends  
  > Arquitetura moderna de Data Lake para transformar dados brutos de turismo em inteligência de negócios.
</div>

---

<details open>
  <summary><strong>Integrantes do Grupo</strong></summary>
  <br/>
  <table align="center">
    <tr>
        <td align="center">
        <a href="#"><img src="Pablo.jpeg" width="80px;" alt="Pablo Roberto"/><br/><sub>Pablo Roberto</sub></a>
      </td>
      <td align="center">
        <a href="#"><img src="Lucas.jpeg" width="80px;" alt="Lucas Antonio"/><br/><sub>Lucas Antonio</sub></a>
      </td>
      <td align="center">
        <a href="#"><img src="Thiago.jpg" width="80px;" alt="Thiago Cardoso"/><br/><sub>Thiago Cardoso</sub></a>
      </td>
      <td align="center">
        <a href="#"><img src="willian.jpeg" width="80px;" alt="William Nunes"/><br/><sub>William Nunes</sub></a>
      </td>
      <td align="center">
        <a href="#"><img src="Daniel.png" width="80px;" alt="Daniel Fernando"/><br/><sub>Daniel Fernando</sub></a>
      </td>
    </tr>
  </table>
</details>

---

## Arquitetura do Fluxo de Dados

Esta documentação detalha a infraestrutura de dados para o projeto **Tour4Friends**. O foco principal é a análise estratégica do comportamento de compra e reservas, utilizando tecnologias de Big Data.

A solução visa transformar dados operacionais em insights de negócio de forma ágil, seguindo o modelo **ELT (Extract, Load, Transform)** com um barramento de streaming para garantir agilidade no processamento.

<img width="1691" height="930" alt="Diagrama de Arquitetura" src="https://github.com/user-attachments/assets/71666f6f-cd8a-4658-99d2-618eda92c848" />

## Componentes Tecnológicos

| Camada | Tecnologia | Função |
|---|---|---|
| Fonte | MongoDB | Banco de dados NoSQL operacional para registros de viagens. |
| Ingestão | Apache Kafka | Barramento de streaming para processamento de eventos em tempo real. |
| Processamento | AWS Glue (Spark) | Engine para transformação de dados e conversão de formatos (JSON para Parquet). |
| Armazenamento | Amazon S3 | Data Lake escalável organizado em camadas Medallion. |
| Catálogo | Glue Data Catalog | Repositório central de metadados para governança e descoberta. |
| Analytics | Google Colab + Power BI | Análise exploratória, preparação dos dados e publicação de dashboards. |

---

<details>
  <summary><strong>Entregas por Disciplina</strong></summary>
  <br/>

  > Mapeamento das contribuições do projeto Tour4Friends para cada disciplina do semestre, conforme os requisitos mínimos do Projeto Integrador IV.

  ---

  **AGE017 — Gestão Econômica e Financeira** *(Prof. Getúlio Kazue Akabane)*  
  Requisito: Avaliação da situação econômica e financeira do negócio.  
  Levantamento dos custos dos serviços AWS utilizados (S3, Glue, Athena) e análise básica de viabilidade financeira da solução para a agência Tour4Friends.

  ---

  **ILP052 — Programação em Banco de Dados II** *(Prof. Samuel Henrique da Rocha)*  
  Requisito: Programação NO-SQL — Controles + Procedures ETL NO-SQL.  
  Modelagem e população do banco de dados MongoDB com dados da agência, incluindo operações básicas de consulta, inserção e extração de dados.

  ---

  **ILP053 — Laboratório de Programação II** *(Prof. Jobel Santos Corrêa)*  
  Requisito: Utilização de bibliotecas em Python para tratamento e análise dos dados.  
  Scripts em Python para leitura, limpeza e tratamento dos dados de reservas, utilizando Pandas para manipulação e preparação dos dados para análise.

  ---

  **MAQ025 — Aprendizagem de Máquinas** *(Prof. Carlos Eduardo Dantas de Menezes)*  
  Requisito: Aplicação de algum algoritmo de aprendizado para análise dos dados.  
  Aplicação de clusterização (K-Means) para agrupar clientes por perfil de compra, identificando padrões de comportamento nos dados de reservas.

  ---

  **BDN003 — Big Data Analytics I** *(Prof. Claudia de Lello Courtouké)*  
  Requisito: Desenvolvimento e aplicação de modelo estatístico para os dados.  
  Análise estatística dos dados de reservas: média, mediana, desvio padrão e análise de sazonalidade, com visualizações geradas no Power BI.

  ---

  **BDN002 — Arquitetura de Big Data e DW/BI** *(Prof. Izaias Porfirio Faria)*  
  Requisito: Definição e avaliação da arquitetura da aplicação. Integração de fontes de dados.  
  Definição e documentação da arquitetura do Data Lake com as camadas Bronze, Silver e Gold na AWS, integrando as fontes de dados do MongoDB até o dashboard final no Power BI.

</details>
