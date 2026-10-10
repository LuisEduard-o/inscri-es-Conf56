# Inscrições Conf56

Aplicação web desenvolvida em Python para gerenciamento de inscrições em eventos, com formulários para diferentes categorias de participantes, geração de código PIX e painel administrativo.

## Funcionalidades

- Cadastro de participantes em diferentes categorias.
- Formulários específicos para inscrições gerais e infantis.
- Geração de código PIX para pagamento das inscrições.
- Armazenamento de dados em banco de dados.
- Painel administrativo para consulta, pesquisa, atualização de status e exclusão de inscrições.
- Exportação de inscrições em CSV.
- Autenticação para acesso à área administrativa.
- Processamento de múltiplas requisições por meio de um servidor HTTP multithread.

## Tecnologias utilizadas

- **Python:** lógica da aplicação e servidor HTTP.
- **PostgreSQL (Neon):** banco de dados relacional hospedado na nuvem.
- **HTML e CSS:** estrutura e interface das páginas.
- **CSV:** exportação dos dados das inscrições.

## Diferenciais técnicos

O servidor web foi desenvolvido utilizando módulos da biblioteca padrão do Python, sem frameworks web como Flask ou Django.

A aplicação utiliza o módulo `http.server` para processar requisições HTTP, além de implementar o processamento dos formulários, o acesso ao banco de dados e a geração de códigos PIX.

## Como executar localmente

1. Instale o Python 3.
2. Clone este repositório.
3. Configure as variáveis de ambiente necessárias.
4. Instale as dependências externas exigidas pelo ambiente, caso necessário.
5. Execute o arquivo Python principal.
6. Acesse a aplicação pelo navegador utilizando o endereço local e a porta configurada.

## Configuração

A aplicação utiliza variáveis de ambiente para configurar o servidor, o banco de dados, o acesso administrativo e os dados necessários para gerar códigos PIX.

- `PORT`: porta utilizada pelo servidor.
- `DATABASE_URL`: URL de conexão com o banco PostgreSQL hospedado no Neon.
- `ADMIN_USER`: usuário administrativo.
- `ADMIN_PASS`: senha administrativa.
- `PIX_CHAVE`: chave PIX utilizada na geração do código.
- `PIX_RECEBEDOR`: nome do recebedor.
- `PIX_CIDADE`: cidade do recebedor.

Configure as variáveis de ambiente antes de executar a aplicação. Não publique credenciais reais no repositório.

## Implantação

A aplicação está hospedada no Render, com o banco de dados PostgreSQL gerenciado pelo Neon.

A conexão com o banco de dados é configurada por meio da variável de ambiente `DATABASE_URL`.

## Observação sobre os pagamentos

A aplicação gera os dados para pagamento via PIX e registra as inscrições. A geração do código PIX, por si só, não confirma o recebimento do pagamento.

## Objetivo do projeto

Projeto desenvolvido para aplicar conhecimentos de Python, desenvolvimento web, bancos de dados, processamento de requisições HTTP e gerenciamento de dados em uma aplicação prática.
