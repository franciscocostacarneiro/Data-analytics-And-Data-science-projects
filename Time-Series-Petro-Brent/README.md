# Projeto de simulação de preço de petróleo - trabalho apresentado na formação do curso superior em Big Data

## Guia de Instalação e Execução

#### 1. Coleta do projeto
Será necessário adiquirir os arquivos, para isso, basta baixar o projeto como .zip ou clonar este repositório.


#### 2. Configuração do ambiente
Em seguida, será necessário configurar o ambiente de execução. Nesse exemplo será usado VS Code, mas o processo 
também pode ser feito em outro interpretador Python.

Após executar o VSCode, abra um novo projeto e selecione o projeto baixado no "Passo 1". Ao abrir o repositório, será
necessario definir o interpretador python que será utilizado nesse projeto para que possa ser executado de forma correta.

No canto inferior direito, clique na aba onde definimos o interpretador do projeto.
![image](https://github.com/MatheusP1/tech_challenge4/assets/43751101/3952bd1b-fbef-4502-84f8-465119ca7637)

(Nesse caso o interpretador está indefinido)
E em seguida, clique em "Configurações do Interpretador" ou "Interpreter Settings"

Será aberta uma nova janela exibindo a lista de interpretadores python instalados no computador. Para este 
projeto é extremamente necessário utilizar o **Python ver. 3.11** por conta da utilização de modulos da biblioteca
TensorFlow que somente oferece suporte até essa versão especifica.

![image](https://github.com/MatheusP1/tech_challenge4/assets/43751101/7bcb32b2-d12c-4dfa-9354-45bd92584474)

Para download da versão mencionada do python, acesse o seguinte link:
https://www.python.org/downloads/release/python-3110/

#### 3. Instalação de requerimentos

Após selecionar o interpretador, é necessario instalar todos as bibliotecas necessárias para a execução do projeto.
Para isso, basta abrir um novo terminal e executar o arquivo "requirements.txt" como seguinte comando:
> pip install -r requirements.txt

#### 4. Execução do projeto

Por fim, para executar o processo basta utilizar o terminal para inicializar a aplicação streamlit com o seguinte comando:
> streamlit run .\Home.py

#### 5. Acesso Web
Também é possivel acessar o projeto diretamente na web através do link:
> https://techchallenge4-g50.streamlit.app/

