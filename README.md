<div align="center">
  <img width="1112" height="266" alt="Tour4Friends Banner" src="https://github.com/user-attachments/assets/8a1c646f-c801-455b-8448-8c9c8ecc3c90" />
  
  # 🌍 Tour4Friends Analytics - Data Lake

![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![MongoDB](https://img.shields.io/badge/MongoDB-NoSQL-green)
![Kafka](https://img.shields.io/badge/Apache-Kafka-black)
![AWS Glue](https://img.shields.io/badge/AWS-Glue_|_Spark-orange)
![AWS S3](https://img.shields.io/badge/AWS-S3_Lake-orange)
![PowerBI](https://img.shields.io/badge/Power_BI-Analytics-F2C811)

> **Projeto Integrador - Tour4Friends**
> Uma arquitetura moderna de Data Lake para transformar dados brutos de turismo em inteligência de negócios.

---
<details open>
  <summary><h2>👥 Integrantes do Grupo</h2></summary>
  
  <br/>
  
  <table align="center">
    <tr>
      <td align="center">
        <a href="#">
          <img src="https://avatars.githubusercontent.com/u/125063071?v=4" width="100px;" alt="Membro 1"/><br/>
          <sub><b>Pablo Roberto</b></sub>
        </a>
      </td>
      <td align="center">
        <a href="#">
          <img src="https://avatars.githubusercontent.com/u/198763242?v=4" width="100px;" alt="Membro 2"/><br/>
          <sub><b>Lucas Antonio</b></sub>
        </a>
      </td>
      <td align="center">
        <a href="#">
          <img src="https://media.licdn.com/dms/image/v2/D4D03AQHJd1xye5u9Yg/profile-displayphoto-scale_400_400/B4DZzakxA5KEAk-/0/1773193598935?e=1777507200&v=beta&t=dpVaT00VB52N4TqE0klBdeomjQSJJaV9jc5m3eFPOQQ" width="100px;" alt="Membro 3"/><br/>
          <sub><b>Thiago Cardoso</b></sub>
        </a>
      </td>
      <td align="center">
        <a href="#">
          <img src="https://media.licdn.com/dms/image/v2/C4D03AQFgxzNm-DDZUg/profile-displayphoto-shrink_400_400/profile-displayphoto-shrink_400_400/0/1619123196498?e=1777507200&v=beta&t=YEiIZLJ82nBAlGvmmo8mXdWl13yZsxKgTSSBUWT9lvc" width="100px;" alt="Membro 4"/><br/>
          <sub><b>William Nunes</b></sub>
        </a>
      </td>>
      </td>
      <td align="center">
        <a href="#">
          <img src="https://github.com/user-attachments/assets/f101196a-348f-42e8-ba32-e977bec686b0" width="100px;" alt="Membro 4"/><br/>
          <sub><b>Daniel Fernando</b></sub>
        </a>
      </td>
      </tr>
    
  </table>
  
</details>


---

# 🔄 Arquitetura do Fluxo de Dados


Esta documentação detalha a infraestrutura de dados para o projeto **Tour4Friends**. O foco principal é a análise estratégica do comportamento de compra e reservas, utilizando tecnologias de ponta em **Big Data**.

## ✈️ Tour4Friends: Arquitetura de Data Lake e Pipeline de ELT (MVP)

Este repositório documenta a construção de um pipeline escalável para a agência de viagens **Tour4Friends**. A solução visa transformar dados operacionais em insights de negócio de forma ágil.

## 🏗️ Diagrama de Arquitetura em Nuvem

A arquitetura segue o modelo **ELT (Extract, Load, Transform)**, utilizando um barramento de streaming para garantir a agilidade no processamento dos dados.

<img width="1693" height="929" alt="Image" src="https://github.com/user-attachments/assets/8d209603-f56b-40e6-b3aa-ad45a9919794" />

## 🛠️ Matriz de Componentes Tecnológicos

| Camada | Tecnologia | Função na Estrutura |
| --- | --- | --- |
| **Fonte** | MongoDB | Banco de dados NoSQL operacional para registros de viagens. |
| **Ingestão** | Apache Kafka | Barramento de streaming para processamento de eventos em tempo real. |
| **Processamento** | AWS Glue (Spark) | Engine para transformação de dados e conversão de formatos (JSON para Parquet). |
| **Armazenamento** | Amazon S3 | Data Lake escalável organizado em camadas Medallion. |
| **Catálogo** | Glue Data Catalog | Repositório central de metadados para governança e descoberta. |
| **Analytics** | Google Colab + Power BI | Análise exploratória, preparação dos dados e publicação de dashboards. |

---

<details>
  <summary><h2> Entregas por Disciplina</h2></summary>

  <br/>

  > Mapeamento das contribuições do projeto **Tour4Friends** para cada disciplina do semestre, conforme os requisitos mínimos do Projeto Integrador IV.

  <br/>

  ###  AGE017 — Gestão Econômica e Financeira *(Prof. Getúlio Kazue Akabane)*
  **Requisito:** Gestão Financeira — Avaliação da situação econômica e financeira do negócio.

  Levantamento dos custos dos serviços AWS utilizados no projeto (S3, Glue, Athena) e análise básica de viabilidade financeira da solução para a agência Tour4Friends.

  ---

  ###  ILP052 — Programação em Banco de Dados II *(Prof. Samuel Henrique da Rocha)*
  **Requisito:** Programação NO-SQL — Controles + Procedures ETL NO-SQL.

  Modelagem e população do banco de dados **MongoDB** com dados da agência, incluindo operações básicas de consulta, inserção e extração de dados (ETL) utilizando o MongoDB.

  ---

  ###  ILP053 — Laboratório de Programação II *(Prof. Jobel Santos Corrêa)*
  **Requisito:** Laboratório II — Utilização de bibliotecas em Python para tratamento e análise dos dados.

  Scripts em **Python** para leitura, limpeza e tratamento dos dados de reservas, utilizando a biblioteca **Pandas** para manipulação e preparação dos dados para análise.

  ---

  ###  MAQ025 — Aprendizagem de Máquinas *(Prof. Carlos Eduardo Dantas de Menezes)*
  **Requisito:** Aprendizagem Máquina — Aplicação de algum algoritmo de aprendizado para análise dos dados.

  Aplicação de um algoritmo de **clusterização (K-Means)** para agrupar clientes por perfil de compra, identificando padrões de comportamento nos dados de reservas da Tour4Friends.

  ---

  ###  BDN003 — Big Data Analytics I *(Prof. Claudia de Lello Courtouké)*
  **Requisito:** Analytics I — Desenvolvimento e aplicação de modelo estatístico para os dados.

  Análise estatística básica dos dados de reservas: média, mediana, desvio padrão e análise de sazonalidade, com visualizações geradas no **Power BI**.

  ---

  ###  BDN002 — Arquitetura de Big Data e DW/BI *(Prof. Izaias Porfirio Faria)*
  **Requisito:** Arquitetura BI-BigData — Definição e avaliação da arquitetura da aplicação. Integração de fontes de dados.

  Definição e documentação da arquitetura do Data Lake com as camadas **Bronze, Silver e Gold** na AWS, integrando as fontes de dados do MongoDB até o dashboard final no **Power BI**.

</details>

