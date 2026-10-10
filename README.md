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
- **SQLite:** armazenamento local de dados.
- **PostgreSQL:** opção de banco de dados para implantação.
- **HTML e CSS:** estrutura e interface das páginas.
- **CSV:** exportação de dados das inscrições.

## Diferenciais técnicos

O servidor web foi implementado utilizando módulos da biblioteca padrão do Python, sem o uso de frameworks web como Flask ou Django.

A aplicação utiliza o módulo `http.server` para receber e processar requisições HTTP, além de implementar o acesso ao banco de dados, o processamento dos formulários e a geração dos códigos PIX.

## Como executar localmente

1. Instale o Python 3.
2. Baixe ou clone este repositório.
3. Configure as variáveis de ambiente necessárias.
4. Execute o arquivo Python principal.
5. Acesse a aplicação pelo navegador no endereço local e na porta configurada.

## Variáveis de ambiente

A aplicação utiliza variáveis de ambiente para configurar funcionalidades como:

- `PORT`: porta utilizada pelo servidor.
- `DATABASE_URL`: conexão com o banco PostgreSQL, quando utilizado.
- `ADMIN_USER`: usuário de acesso administrativo.
- `ADMIN_PASS`: senha de acesso administrativo.
- `PIX_CHAVE`: chave PIX utilizada na geração do código.
- `PIX_RECEBEDOR`: nome do recebedor do pagamento.
- `PIX_CIDADE`: cidade do recebedor.

Configure essas variáveis antes de executar a aplicação. Não compartilhe senhas ou credenciais reais no repositório.

## Observação sobre os pagamentos

A aplicação gera os dados para pagamento via PIX e registra as inscrições. A geração do código PIX, por si só, não confirma o recebimento do pagamento.

## Objetivo do projeto

Projeto desenvolvido para aplicar conhecimentos de Python, desenvolvimento web, bancos de dados, processamento de requisições HTTP e gerenciamento de dados em uma aplicação prática.
