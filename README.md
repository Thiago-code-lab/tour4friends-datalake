<div align="center">
  <img width="1112" height="266" alt="Tour4Friends Banner" src="https://github.com/user-attachments/assets/8a1c646f-c801-455b-8448-8c9c8ecc3c90" />
  
  # 🌍 Tour4Friends Analytics - Data Lake

![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![MongoDB](https://img.shields.io/badge/MongoDB-NoSQL-green)
![Kafka](https://img.shields.io/badge/Apache-Kafka-black)
![AWS Glue](https://img.shields.io/badge/AWS-Glue_|_Spark-orange)
![AWS S3](https://img.shields.io/badge/AWS-S3_Lake-orange)
![AWS Athena](https://img.shields.io/badge/AWS-Athena_SQL-orange)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
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
          <img src="https://media.licdn.com/dms/image/v2/D4D03AQHJd1xye5u9Yg/profile-displayphoto-scale_400_400/B4DZzakxA5KEAk-/0/1773193598935?e=1775088000&v=beta&t=yB0D7ALws6vPfVz1fiadNPohfxuBDF3OLI66jyp2KR4" width="100px;" alt="Membro 3"/><br/>
          <sub><b>Thiago Cardoso</b></sub>
        </a>
      </td>
      <td align="center">
        <a href="#">
          <img src="https://media.licdn.com/dms/image/v2/C4D03AQFgxzNm-DDZUg/profile-displayphoto-shrink_200_200/profile-displayphoto-shrink_200_200/0/1619123196498?e=1774483200&v=beta&t=2e1mPIFrfhDSjsOC8In234xJ_rkyJ5cRLbjxfDiZhUo" width="100px;" alt="Membro 4"/><br/>
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

<img width="2816" height="1536" alt="Arquitetura de software" src="https://github.com/user-attachments/assets/fad4f7f8-db08-4c82-915d-fe46e51db278" />


## 📋 Descrição do Pipeline

Para garantir a entrega de um MVP funcional e focado, o pipeline foi desenhado para processar especificamente os dados de interação e reservas dos usuários:

* **Ingestão (Extract & Load):** Os dados são extraídos do **MongoDB** em tempo real via **Change Data Capture (CDC)** e enviados ao **Apache Kafka**. O **Kafka Connect** realiza a carga direta (**Load**) dos dados brutos no **Amazon S3**.
* **Camadas do Data Lake (Medallion Architecture):**
* **Raw Zone (Bronze):** Armazena os eventos originais em formato **JSON**.
* **Processed Zone (Silver):** Dados limpos, tipados e convertidos para formato colunar (**Parquet**) via **AWS Glue (Spark)**.
* **Curated Zone (Gold):** Tabelas agregadas com regras de negócio prontas para análise estratégica.


* **Catálogo e Analytics (Transform & Consumption):** O **Glue Data Catalog** gerencia os metadados, permitindo que o **Amazon Athena** execute consultas SQL diretamente no S3 para alimentar os dashboards no **Power BI**.

## 🛠️ Matriz de Componentes Tecnológicos

| Camada | Tecnologia | Função na Estrutura |
| --- | --- | --- |
| **Fonte** | MongoDB | Banco de dados NoSQL operacional para registros de viagens. |
| **Ingestão** | Apache Kafka | Barramento de streaming para processamento de eventos em tempo real. |
| **Processamento** | AWS Glue (Spark) | Engine para transformação de dados e conversão de formatos (JSON para Parquet). |
| **Armazenamento** | Amazon S3 | Data Lake escalável organizado em camadas Medallion. |
| **Catálogo** | Glue Data Catalog | Repositório central de metadados para governança e descoberta. |
| **Analytics** | Amazon Athena | Motor de consultas SQL serverless para análise de dados no S3. |

---



