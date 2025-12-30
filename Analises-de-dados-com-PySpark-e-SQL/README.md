# ETL e manipulação de dados com PySpark no Databricks

Aqui apresentarei 4 cases onde eu utilizarei PySpark, SparkSQL e SQL para a manipulação de dados e consultas simples. Esse projeto apresenta algumas das minhas qualificações datadriving com big data.

## 1o. caso: Realização de ETL e manipulação de dados - scripts de consulta e tratamento simples de dados em PySpark, no Databricks com processamento computacional distribuído utilizando uma base de dados pública da RAIS - Relação Anual de Informações Sociais.

## 2o. caso: Dados consolidados da RAIS Estabelecimento — contagem de estabelecimentos por classificações de porte, localizaçso e classificação de atividade econômica (CNAE).

## 3o. e 4o. casos: Realização de consultas simples em SQL com a utilização de PySpark para a leitura do nosso Dataset. Para tal, nas células do notebook eu utilizarei a magic command %%sql. A utilização do sql no notebook permite que possamos formar o racional de querys para storytelling, o que não é possível utilizando o SQL Editor. Para tal, devemos alterar o tipo da célula para SQL ao invés de Python geralmente utilizada. Para as consultas diretamente sem a utilização de PySpark devemos criar uma session temporária - temp view. Um ponto de destaque é que devemos sempre atentar-nos ao fato de que a temp view funciona porquanto a sessão estiver on line. 
