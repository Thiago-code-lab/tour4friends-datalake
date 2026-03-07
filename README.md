<div align="center">
  <img width="1112" height="266" alt="Tour4Friends Banner" src="https://github.com/user-attachments/assets/8a1c646f-c801-455b-8448-8c9c8ecc3c90" />
  
  # 🌍 Tour4Friends Analytics - Data Lake

![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
![AWS](https://img.shields.io/badge/AWS-S3-orange)
![Kafka](https://img.shields.io/badge/Apache-Kafka-black)
![Airflow](https://img.shields.io/badge/Apache-Airflow-017CEE)
![MongoDB](https://img.shields.io/badge/MongoDB-NoSQL-green)

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
          <img src="https://github.com/user-attachments/assets/24b362a2-ee92-46aa-8d93-94d119dafabe" width="100px;" alt="Membro 3"/><br/>
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

## 🔄 Arquitetura do Fluxo de Dados
```mermaid
%%{init: {'theme':'neutral', 'themeVariables': { 'primaryColor':'#6366f1','primaryTextColor':'#ffffff','primaryBorderColor':'#4f46e5','lineColor':'#9ca3af','fontSize':'15px'}}}%%
graph LR
    A[Simulator] -->|stream| B((Kafka))
    B -->|batch| C[(S3)]
    C -.->|schedule| D{Airflow}
    D --> E[Pandas]
    E -->|refined| F[(MongoDB)]
    F -->|query| G[BI Tools]
    
    classDef source fill:#6366f1,stroke:#4f46e5,stroke-width:2px,color:#fff
    classDef stream fill:#f59e0b,stroke:#d97706,stroke-width:2px,color:#fff
    classDef storage fill:#0ea5e9,stroke:#0284c7,stroke-width:2px,color:#fff
    classDef process fill:#8b5cf6,stroke:#7c3aed,stroke-width:2px,color:#fff
    classDef db fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    classDef viz fill:#ef4444,stroke:#dc2626,stroke-width:2px,color:#fff
    
    class A source
    class B stream
    class C,F storage
    class D,E process
    class G viz
```



