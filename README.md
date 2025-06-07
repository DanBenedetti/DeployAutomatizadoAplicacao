Projeto Flask CRUD com MySQL, Docker e SonarQube

> Pipeline CI/CD automatizado com análise de qualidade
📖 Descrição

Este projeto é uma aplicação CRUD desenvolvida em Python Flask com banco de dados MySQL, totalmente orquestrada via Docker e com pipeline de integração contínua (CI/CD) via GitHub Actions. O pipeline executa uma análise automática de qualidade de código utilizando o SonarQube em container temporário na VM, e o deploy é realizado diretamente no servidor remoto.
🛠 Tecnologias Utilizadas

    Python 3.11
    Flask
    Flask-MySQLdb
    MySQL 8
    Docker & Docker Compose
    GitHub Actions
    SonarQube
    appleboy/ssh-action
    appleboy/scp-action

⚙️ Estrutura dos Principais Arquivos
├── app.py

├── requirements.txt

├── Dockerfile

├── docker-compose.yml

├── .env

├── deploy.yml

└── README.md

app.py: Código principal do Flask.

    requirements.txt: Dependências Python.

    Dockerfile: Construção da imagem da aplicação.

    docker-compose.yml: Orquestração de app e banco.

    .env: Variáveis sensíveis (não versionar em repositório público).

    deploy.yml: Pipeline CI/CD.

    README.md: Este guia.

🚀 Como Executar Localmente

Clone o repositório
bash
Copiar

git clone https://github.com/seuusuario/nome-repo.git
cd nome-repo

Configure variáveis de ambiente

Crie um arquivo .env:
env
Copiar

MYSQL_ROOT_PASSWORD=suasenha
MYSQL_DATABASE=crud_flask
MYSQL_USER=SeuUsuario
MYSQL_PASSWORD=suasenha

Suba via Docker Compose
bash
Copiar

docker-compose up -d --build

    O app Flask estará acessível em http://localhost:8086

    O MySQL estará na porta 8087

🧪 Pipeline CI/CD (GitHub Actions)

O pipeline realiza:

Build de imagem Docker

Push para Docker Hub

Acesso via SSH ao servidor remoto (201.23.3.86)

Subida temporária do SonarQube em container

    Análise de código via SonarScanner

Falha automática da pipeline caso o Quality Gate não seja aprovado

Remoção do container SonarQube

Deploy: envio do docker-compose.yml e reload das imagens
🔒 Segurança

    Variáveis sensíveis (senhas, chaves SSH) são fornecidas via GitHub Secrets

    O arquivo .env NÃO deve ser versionado em repositório público

🎯 Restrições Especiais

    SOMENTE as portas 8086–8091 são utilizadas externamente:
        App Flask: 8086
        MySQL: 8087
        SonarQube temporário (pipeline): 8088

🖥️ Acesso no Servidor

    App Flask: acessível via http://<IP_serv>:8086

    MySQL: acesso no host/server via porta 8087

    SonarQube: só é iniciado temporariamente pela pipeline (não roda permanentemente)

⚡ Exemplo de Uso dos Principais Comandos

    Build manual:

bash
Copiar

    docker build -t danilobenedetti/app_crud_flask:latest .

    Subir serviço:

bash
Copiar

    docker-compose up -d --build

    Acompanhar logs:

bash
Copiar

    docker-compose logs -f

📄 Notas Finais

    Implementação alinhada a boas práticas de CI/CD e segurança de credenciais.

    O pipeline está preparado para falhar automaticamente em caso de reprovação no SonarQube, garantindo código sempre auditado.

🙋‍♂️ Dúvidas/Fale comigo

Em caso de dúvidas, sugestões ou problemas, abra uma issue ou entre em contato!

2025 © Danilo Benedetti

Se quiser personalizar ainda mais esse modelo, adicionar prints, fluxogramas ou exemplos completos de env/config conforme ambiente, só avisar!
