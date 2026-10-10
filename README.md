# inscri-es-Conf56

# Inscrições Conf56

Aplicação web desenvolvida em Python para gerenciamento de inscrições em eventos, com formulários para diferentes categorias de participantes, geração de código PIX e painel administrativo.

## Funcionalidades

- Cadastro de participantes em diferentes categorias.
- Formulários específicos para inscrições gerais e infantis.
- Geração de código PIX para pagamento das inscrições.
- Armazenamento de dados em SQLite ou PostgreSQL.
- Painel administrativo para consulta, pesquisa, atualização de status e exclusão de inscrições.
- Exportação de inscrições em CSV.
- Autenticação para acesso à área administrativa.
- Execução de múltiplas requisições utilizando um servidor HTTP multithread.

## Tecnologias utilizadas

- **Python:** lógica da aplicação e servidor HTTP.
- **PostgreSQL (Neon):** banco de dados relacional hospedado na nuvem.
- **HTML e CSS:** estrutura e interface das páginas.
- **CSV:** exportação dos dados das inscrições.

## Diferenciais técnicos

O servidor web foi desenvolvido utilizando módulos da biblioteca padrão do Python, sem frameworks web como Flask ou Django.

A aplicação utiliza o módulo `http.server` para processar requisições HTTP, além de implementar o processamento dos formulários, o acesso ao banco de dados e a geração de códigos PIX.

O banco de dados PostgreSQL é hospedado no Neon, permitindo armazenar os dados das inscrições em um ambiente remoto.

## Como executar localmente

1. Instale o Python 3.
2. Baixe ou clone este repositório.
3. Configure as variáveis de ambiente necessárias.
4. Execute o arquivo Python principal.
5. Acesse a aplicação pelo navegador no endereço local e na porta configurada.

Configuração

A aplicação utiliza variáveis de ambiente para configurar o servidor, o banco de dados, o acesso administrativo e os dados necessários para gerar códigos PIX.

PORT: porta utilizada pelo servidor.

DATABASE_URL: URL de conexão com o banco PostgreSQL hospedado no Neon.

ADMIN_USER: usuário administrativo.

ADMIN_PASS: senha administrativa.

PIX_CHAVE: chave PIX utilizada na geração do código.

PIX_RECEBEDOR: nome do recebedor.

PIX_CIDADE: cidade do recebedor.

Configure as variáveis de ambiente antes de executar a aplicação. Não publique credenciais reais no repositório.

Configure essas variáveis antes de executar a aplicação. Não compartilhe senhas ou credenciais reais no repositório.

## Observação sobre os pagamentos

A aplicação gera os dados para pagamento via PIX e registra as inscrições. A geração do código PIX, por si só, não confirma o recebimento do pagamento.

## Objetivo do projeto

Projeto desenvolvido para aplicar conhecimentos de Python, desenvolvimento web, bancos de dados, processamento de requisições HTTP e gerenciamento de dados em uma aplicação prática.
