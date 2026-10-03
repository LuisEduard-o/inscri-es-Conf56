from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import sqlite3
import csv
import io
import os

DB_NAME = "database.db"

# CONFIGURAÇÕES DO PIX
PIX_CHAVE = "41998694346"
PIX_RECEBEDOR = "Igreja Evento"
PIX_CIDADE = "CURITIBA"

# VALORES DAS INSCRIÇÕES
VALOR_GERAL = 50.00
VALOR_KIDS = 15.00

def calcular_crc16(payload: str) -> str:
    crc = 0xFFFF
    for char in payload:
        crc ^= ord(char) << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = ((crc << 1) & 0xFFFF)
    return f"{crc:04X}"

def format_tlv(tag: str, value: str) -> str:
    length = len(value)
    return f"{tag}{length:02d}{value}"

def gerar_payload_pix(chave: str, nome: str, cidade: str, valor: float, txid: str = "INSCRICAO") -> str:
    chave_limpa = "".join(filter(str.isdigit, chave))
    if len(chave_limpa) in [10, 11]:  
        chave_formatada = f"+55{chave_limpa}"
    else:
        chave_formatada = chave

    payload = format_tlv("00", "01")
    payload += format_tlv("01", "11")
    
    gui = format_tlv("00", "br.gov.bcb.pix")
    chave_field = format_tlv("01", chave_formatada)
    payload += format_tlv("26", gui + chave_field)
    
    payload += format_tlv("52", "0000")
    payload += format_tlv("53", "986")
    payload += format_tlv("54", f"{valor:.2f}")
    payload += format_tlv("58", "BR")
    payload += format_tlv("59", nome[:25].upper())
    payload += format_tlv("60", cidade[:15].upper())
    
    txid_field = format_tlv("05", txid[:25])
    payload += format_tlv("62", txid_field)
    
    payload += "6304"
    crc = calcular_crc16(payload)
    return payload + crc

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inscricoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT NOT NULL,
            tipo TEXT NOT NULL,
            nome TEXT NOT NULL,
            idade INTEGER NOT NULL,
            telefone TEXT NOT NULL,
            igreja TEXT NOT NULL,
            responsavel_nome TEXT,
            responsavel_tel TEXT,
            status TEXT DEFAULT 'Pendente',
            data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# HTML DO FORMULÁRIO GERAL (10+ anos)
HTML_FORM = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&display=swap" rel="stylesheet">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>INSCRIÇÃO CONF56</title>
    <style>
        :root { --primary: #ff7926; --primary-hover: #4c0082; --bg-color: #6500a4; --card-bg: #ffffff; --text-main: #3e005b; --text-muted: #3e005b; --border: #110064; --error: #dc2626; }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Montserrat', sans-serif, "Segoe UI", Roboto, sans-serif; }
        body {background-color: var(--bg-color);background: linear-gradient(-135deg, #00d5ff 0%, #ff3700 30%, #4f0099 100%); background-size: 100% 100%;background-repeat: no-repeat;color: var(--text-main);padding: 16px;display: flex;justify-content: center;align-items: center;min-height: 100vh;margin: 0;overflow-y: auto;}
        img{width: 100%; max-width: 250px; height: auto; border-radius: 8px; object-fit: cover;}
        .Info{flex: 1.2;display: flex; flex-direction: column; text-align: center;}
        .container { width: 100%; max-width: 600px; background: var(--card-bg); padding: 14px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); display: flex;justify-content: space-between;gap: 14px}
        .Logo{flex: 1; display: flex;justify-content: center;align-items: center;}
        .Info{flex: 1; min-width: none;}
        h2 { text-align: center; margin-bottom: 4px; font-size: 1.5rem;font-family: 'Montserrat', sans-serif; font-weight: 800;}
        .subtitle { text-align: center; color: var(--text-muted); font-size: 0.7rem; margin-bottom: 10px; }
        .form-group { margin-bottom: 8px; }
        label { display: block; margin-bottom: 2px; font-weight: 600; font-size: 0.75rem;}
        option {background: #460072;color: #c7c7c7;}
        option:hover {background: #00d5ff;}
        input, select { color: #3e005b;width: 100%; padding: 6px 8px; border: 1px solid var(--border); border-radius: 6px; font-size: 0.8rem; background-color: #fff; }
        input:focus, select:focus { outline: none; border-color: #4c0082; box-shadow: 0 0 0 1px rgb(255, 123, 0); }
        .error-msg { color: var(--error); font-size: 0.65rem; margin-top: 2px; display: none; }
        .form-group.error input, .form-group.error select { border-color: var(--error); }
        .form-group.error .error-msg { display: block; }
        button { width: 100%; padding: 8px; background-color: var(--primary); color: white; border: none; border-radius: 6px; font-size: 0.85rem; font-weight: 600; cursor: pointer; margin-top: 4px; }
        button:active { background-color: var(--primary-hover); }
        .alert { padding: 14px; border-radius: 8px; margin-bottom: 20px; text-align: center; font-weight: 500; }
        .alert-error { background-color: #fee2e2; color: var(--error); border: 1px solid #fecaca; }
        .switch-link { text-align: center; margin-top: 8px; font-size: 0.75rem; }
        .switch-link a { color: var(--primary); text-decoration: none; font-weight: 600; }
        .switch-link a:hover { text-decoration: underline; }
        @media (max-width: 768px) {
            .container {
                flex-direction: column;
                max-width: 350px;
            }

            .Logo{
                width: 100%;
                display: flex;
                justify-content: center;
            }

            img {
                width: 100%;
                max-width: 80%;
                height: 100%;
                object-fit: cover;
            }
        }
    </style>
</head>
<body>

    <div class="container">
        <div class="Logo">
            <img src="Banner.jpeg">
        </div>
        <div class="Info">
            <h2>CONF56</h2>
            <p class="subtitle">Taxa de Inscrição: <b>R$ 50,00</b> (A partir de 10 anos)</p>
            {{ALERT}}
            <form action="/pagamento" method="POST" onsubmit="return validarFormulario(event)">
                <input type="hidden" name="categoria" value="Geral">
                <div class="form-group" id="group-tipo">
                    <label for="tipo">Tipo de Inscrição</label>
                    <select id="tipo" name="tipo" required>
                        <option value="" disabled selected>Selecione...</option>
                        <option value="Participante">Participante</option>
                        <option value="Staff / Voluntario">Staff / Voluntário</option>
                    </select>
                    <div class="error-msg">Selecione o tipo de inscrição.</div>
                </div>
                <div class="form-group" id="group-nome">
                    <label for="nome">Nome Completo</label>
                    <input type="text" id="nome" name="nome" placeholder="Digite seu nome completo" required>
                    <div class="error-msg">Insira seu nome completo.</div>
                </div>
                <div class="form-group" id="group-idade">
                    <label for="idade">Idade</label>
                    <input type="number" id="idade" name="idade" placeholder="Ex: 25" min="10" max="120" inputmode="numeric" required>
                    <div class="error-msg">A idade mínima para esta aba é 10 anos.</div>
                </div>
                <div class="form-group" id="group-telefone">
                    <label for="telefone">Telefone / WhatsApp</label>
                    <input type="tel" id="telefone" name="telefone" placeholder="Somente números com DDD" inputmode="numeric" oninput="this.value = this.value.replace(/\\D/g, '')" required>
                    <div class="error-msg">Insira um número válido (mínimo 10 dígitos).</div>
                </div>
                <div class="form-group" id="group-igreja">
                    <label for="igreja">Qual Igreja é?</label>
                    <input type="text" id="igreja" name="igreja" placeholder="Nome da sua igreja" required>
                    <div class="error-msg">Informe o nome da sua igreja.</div>
                </div>
                <button type="submit">Ir para o Pagamento (R$ 50,00)</button>
            </form>
            <div class="switch-link">
                Procurando a inscrição infantil? <a href="/kids">Ir para o Evento Kids (5 a 9 anos)</a>
            </div>
        </div>
    </div>
    <script>
        function validarFormulario(event) {
            let isValid = true;
            let tipo = document.getElementById('tipo');
            let groupTipo = document.getElementById('group-tipo');
            if (!tipo.value) { groupTipo.classList.add('error'); isValid = false; } else { groupTipo.classList.remove('error'); }

            let nome = document.getElementById('nome');
            let groupNome = document.getElementById('group-nome');
            if (nome.value.trim().length < 3) { groupNome.classList.add('error'); isValid = false; } else { groupNome.classList.remove('error'); }

            let idade = document.getElementById('idade');
            let groupIdade = document.getElementById('group-idade');
            let val = parseInt(idade.value);
            if (isNaN(val) || val < 10 || val > 120) { groupIdade.classList.add('error'); isValid = false; } else { groupIdade.classList.remove('error'); }

            let telefone = document.getElementById('telefone');
            let groupTelefone = document.getElementById('group-telefone');
            let telClean = telefone.value.replace(/\\D/g, '');
            if (telClean.length < 10 || telClean.length > 11) { groupTelefone.classList.add('error'); isValid = false; } else { groupTelefone.classList.remove('error'); }

            let igreja = document.getElementById('igreja');
            let groupIgreja = document.getElementById('group-igreja');
            if (igreja.value.trim().length < 2) { groupIgreja.classList.add('error'); isValid = false; } else { groupIgreja.classList.remove('error'); }

            if (!isValid) event.preventDefault();
            return isValid;
        }
    </script>
</body>
</html>
"""

# HTML DO FORMULÁRIO KIDS (5 a 9 anos)
HTML_FORM_KIDS = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inscrição CONF Kids</title>
    <style>
        :root { --primary: #ff7926; --primary-hover: #4c0082; --bg-color: #6500a4; --card-bg: #ffffff; --text-main: #3e005b; --text-muted: #3e005b; --border: #110064; --error: #dc2626; }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Montserrat', sans-serif, "Segoe UI", Roboto, sans-serif; }
        body {background-color: var(--bg-color);background: linear-gradient(-135deg, #00d5ff 0%, #ff3700 30%, #4f0099 100%); background-size: 100% 100%;background-repeat: no-repeat;color: var(--text-main);padding: 16px;display: flex;justify-content: center;align-items: center;min-height: 100vh;margin: 0;overflow-y: auto;}
        img{width: 100%; max-width: 250px; height: auto; border-radius: 8px; object-fit: cover;}
        .Info{flex: 1.2;display: flex; flex-direction: column; text-align: center;}
        .container { width: 100%; max-width: 600px; background: var(--card-bg); padding: 14px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); display: flex;justify-content: space-between;gap: 14px}
        .Logo{flex: 1; display: flex;justify-content: center;align-items: center;}
        .Info{flex: 1; min-width: none;}
        h2 { text-align: center; margin-bottom: 4px; font-size: 1.5rem;font-family: 'Montserrat', sans-serif; font-weight: 800;}
        .subtitle { text-align: center; color: var(--text-muted); font-size: 0.7rem; margin-bottom: 10px; }
        .form-group { margin-bottom: 8px; }
        label { display: block; margin-bottom: 2px; font-weight: 600; font-size: 0.75rem;}
        option {background: #460072;color: #c7c7c7;}
        option:hover {background: #00d5ff;}
        input, select { color: #3e005b;width: 100%; padding: 6px 8px; border: 1px solid var(--border); border-radius: 6px; font-size: 0.8rem; background-color: #fff; }
        input:focus, select:focus { outline: none; border-color: #4c0082; box-shadow: 0 0 0 1px rgb(255, 123, 0); }
        .error-msg { color: var(--error); font-size: 0.65rem; margin-top: 2px; display: none; }
        .form-group.error input, .form-group.error select { border-color: var(--error); }
        .form-group.error .error-msg { display: block; }
        button { width: 100%; padding: 8px; background-color: var(--primary); color: white; border: none; border-radius: 6px; font-size: 0.85rem; font-weight: 600; cursor: pointer; margin-top: 4px; }
        button:active { background-color: var(--primary-hover); }
        .alert { padding: 14px; border-radius: 8px; margin-bottom: 20px; text-align: center; font-weight: 500; }
        .alert-error { background-color: #fee2e2; color: var(--error); border: 1px solid #fecaca; }
        .switch-link { text-align: center; margin-top: 8px; font-size: 0.75rem; }
        .switch-link a { color: var(--primary); text-decoration: none; font-weight: 600; }
        .switch-link a:hover { text-decoration: underline; }
        @media (max-width: 768px) {
            .container {
                flex-direction: column;
                max-width: 350px;
            }

            .Logo{
                width: 100%;
                display: flex;
                justify-content: center;
            }

            img {
                width: 100%;
                max-width: 80%;
                height: 100%;
                object-fit: cover;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="Logo">
            <img src="Banner.jpeg">
        </div>
        <div class="Info">
            <h2>🎨 CONF Kids 🎈</h2>
            <p class="subtitle">Inscrição Infantil (De 5 a 9 anos) - <b>R$ 15,00</b></p>
            {{ALERT}}
            <form action="/pagamento" method="POST" onsubmit="return validarFormulario(event)">
                <input type="hidden" name="categoria" value="Kids">
                <input type="hidden" name="tipo" value="Participante Kids">
                <div class="form-group" id="group-nome">
                    <label for="nome">Nome da Criança</label>
                    <input type="text" id="nome" name="nome" placeholder="Nome completo da criança" required>
                    <div class="error-msg">Insira o nome da criança.</div>
                </div>
                <div class="form-group" id="group-idade">
                    <label for="idade">Idade da Criança</label>
                    <input type="number" id="idade" name="idade" placeholder="Ex: 7" min="5" max="9" inputmode="numeric" required>
                    <div class="error-msg">A idade para o Kids deve ser entre 5 e 9 anos.</div>
                </div>
                <div class="form-group" id="group-igreja">
                    <label for="igreja">Qual Igreja é?</label>
                    <input type="text" id="igreja" name="igreja" placeholder="Nome da igreja" required>
                    <div class="error-msg">Informe o nome da igreja.</div>
                </div>
                <div class="form-group" id="group-resp-nome">
                    <label for="resp_nome">Nome do Responsável</label>
                    <input type="text" id="resp_nome" name="resp_nome" placeholder="Nome do pai, mãe ou responsável" required>
                    <div class="error-msg">Informe o nome do responsável.</div>
                </div>
                <div class="form-group" id="group-resp-tel">
                    <label for="resp_tel">Telefone / WhatsApp do Responsável</label>
                    <input type="tel" id="resp_tel" name="resp_tel" placeholder="Somente números com DDD" inputmode="numeric" oninput="this.value = this.value.replace(/\\D/g, '')" required>
                    <div class="error-msg">Insira um telefone válido com DDD.</div>
                </div>
                <button type="submit">Ir para o Pagamento (R$ 15,00)</button>
            </form>
            <div class="switch-link">
                Inscrição CONF56 (acima de 10 anos)? <a href="/">Ir para o formulário Geral</a>
            </div>
        
    </div>
    <script>
        function validarFormulario(event) {
            let isValid = true;

            let nome = document.getElementById('nome');
            let groupNome = document.getElementById('group-nome');
            if (nome.value.trim().length < 3) { groupNome.classList.add('error'); isValid = false; } else { groupNome.classList.remove('error'); }

            let idade = document.getElementById('idade');
            let groupIdade = document.getElementById('group-idade');
            let val = parseInt(idade.value);
            if (isNaN(val) || val < 5 || val > 9) { groupIdade.classList.add('error'); isValid = false; } else { groupIdade.classList.remove('error'); }

            let igreja = document.getElementById('igreja');
            let groupIgreja = document.getElementById('group-igreja');
            if (igreja.value.trim().length < 2) { groupIgreja.classList.add('error'); isValid = false; } else { groupIgreja.classList.remove('error'); }

            let respNome = document.getElementById('resp_nome');
            let groupRespNome = document.getElementById('group-resp-nome');
            if (respNome.value.trim().length < 3) { groupRespNome.classList.add('error'); isValid = false; } else { groupRespNome.classList.remove('error'); }

            let respTel = document.getElementById('resp_tel');
            let groupRespTel = document.getElementById('group-resp-tel');
            let telClean = respTel.value.replace(/\\D/g, '');
            if (telClean.length < 10 || telClean.length > 11) { groupRespTel.classList.add('error'); isValid = false; } else { groupRespTel.classList.remove('error'); }

            if (!isValid) event.preventDefault();
            return isValid;
        }
    </script>
</body>
</html>
"""

HTML_PAGAMENTO = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pagamento PIX - R$ {{VALOR_STR}}</title>
    <style>
        :root { --primary: #ff7926; --success: #00d315; --bg-color: #6500a4; --card-bg: #ffffff; --text-main: #3e005b; --text-muted: #3e005b; --border: #110064; }
        * { text-align: center;box-sizing: border-box; margin: 0; padding: 0; font-family: 'Montserrat', sans-serif; }
        body {background-color: var(--bg-color);background: linear-gradient(-135deg, #00d5ff 0%, #ff3700 30%, #4f0099 100%); background-size: 100% 100%;background-repeat: no-repeat;color: var(--text-main);padding: 16px;display: flex;justify-content: center;align-items: center;min-height: 100vh;margin: 0;overflow-y: auto;}
        .container {width: 100%; max-width: 600px; background: var(--card-bg); padding: 14px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); display: flex;flex-direction: column;justify-content: space-between;gap: 14px}
        h2 { margin-bottom: 4px; font-size: 1.5rem;font-family: 'Montserrat', sans-serif; font-weight: 800;}
        .valor-destaque { font-size: 1.2rem; color: var(--primary); font-weight: bold; margin-bottom: 14px; }
        .pix-box { background: #f1f5f9; padding: 14px; border-radius: 10px; margin-bottom: 12px; word-break: break-all; font-family: monospace; font-size: 0.85rem; border: 1px dashed var(--border); text-align: left; max-height: 90px; overflow-y: auto; }
        .instruction { font-size: 0.88rem; color: var(--text-main); margin-bottom: 16px; line-height: 1.4; text-align: left; background: #fffbeb; border: 1px solid #fef3c7; padding: 12px; border-radius: 8px; }
        button { width: 100%; padding: 14px; background-color: var(--success); color: white; border: none; border-radius: 8px; font-size: 1.05rem; font-weight: 600; cursor: pointer; transition: background 0.2s; }
        button:active { background-color: #06f25c; }
        .btn-voltar { background-color: var(--text-muted); margin-top: 10px; }
        @media (max-width: 768px) {
            .container {
                flex-direction: column;
                max-width: 350px;
            }

            .Logo{
                width: 100%;
                display: flex;
                justify-content: center;
            }

            img {
                width: 100%;
                max-width: 80%;
                height: 100%;
                object-fit: cover;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Quase lá, {{NOME}}!</h2>
        <div class="valor-destaque">Valor: R$ {{VALOR_STR}}</div>

        <div class="instruction">
            <strong>Instruções de Pagamento:</strong><br>
            1. Copie o código PIX abaixo.<br>
            2. Pague o valor exato de <b>R$ {{VALOR_STR}}</b> no app do seu banco.<br>
            3. Após o pagamento, clique no botão abaixo para concluir sua inscrição.
        </div>

        <p style="font-size: 0.85rem; font-weight: 600; margin-bottom: 4px; text-align: left;">PIX Copia e Cola:</p>
        <div class="pix-box" id="pixKey">{{PIX_PAYLOAD}}</div>
        
        <button onclick="copiarChave()" style="background-color: var(--primary); margin-bottom: 16px;">Copiar Código PIX</button>

        <form action="/finalizar" method="POST">
            <input type="hidden" name="categoria" value="{{CATEGORIA}}">
            <input type="hidden" name="tipo" value="{{TIPO}}">
            <input type="hidden" name="nome" value="{{NOME}}">
            <input type="hidden" name="idade" value="{{IDADE}}">
            <input type="hidden" name="telefone" value="{{TELEFONE}}">
            <input type="hidden" name="igreja" value="{{IGREJA}}">
            <input type="hidden" name="resp_nome" value="{{RESP_NOME}}">
            <input type="hidden" name="resp_tel" value="{{RESP_TEL}}">
            
            <button type="submit">Já Paguei / Concluir Inscrição</button>
        </form>

        <form action="{{VOLTAR_URL}}" method="GET">
            <button type="submit" class="btn-voltar">Voltar / Corrigir Dados</button>
        </form>
    </div>

    <script>
        function copiarChave() {
            let chave = document.getElementById('pixKey').innerText;
            navigator.clipboard.writeText(chave).then(() => {
                alert('Código PIX copiado!');
            });
        }
    </script>
</body>
</html>
"""

HTML_SUCESSO = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inscrição Registrada</title>
    <style>
        :root { --success: #ffae00; --bg-color: #6500a4; --card-bg: #ffffff; --text-main: #3e005b; --text-muted: #3e005b; }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: var(--bg-color);background: linear-gradient(-135deg, #00d5ff 0%, #ff3700 30%, #4f0099 100%); background-size: 100% 100%;background-repeat: no-repeat;color: var(--text-main);padding: 16px;display: flex;justify-content: center;align-items: center;min-height: 100vh;margin: 0;overflow-y: auto;}
        .container { width: 100%; max-width: 480px; background: var(--card-bg); padding: 32px 24px; border-radius: 16px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); text-align: center; }
        h2 { color: var(--success); margin-bottom: 12px; font-size: 1.6rem; }
        p { color: var(--text-muted); font-size: 1rem; line-height: 1.5; margin-bottom: 24px; }
        button { width: 100%; padding: 14px; background-color: var(--success); color: white; border: none; border-radius: 8px; font-size: 1.05rem; font-weight: 600; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Inscrição Registrada!</h2>
        <p>Sua inscrição foi salva com sucesso. A liderança fará a conferência rápida do recebimento na conta e sua vaga estará garantida. Deus te abençoe!</p>
        <form action="/" method="GET">
            <button type="submit">Fazer Outra Inscrição</button>
        </form>
    </div>
</body>
</html>
"""

class SimpleServer(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        if path == '/kids':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            page = HTML_FORM_KIDS.replace("{{ALERT}}", "")
            self.wfile.write(page.encode("utf-8"))
            return

        elif path == '/admin':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            
            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, categoria, tipo, nome, idade, telefone, igreja, responsavel_nome, responsavel_tel, status, data_registro 
                    FROM inscricoes ORDER BY id DESC
                """)
                rows = cursor.fetchall()
                conn.close()
            except Exception as e:
                rows = []

            html_tabela = """<!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8"><title>Painel da Liderança - Inscrições</title>
                <style>
                    body { font-family: sans-serif; background: #f8fafc; padding: 20px; color: #1e293b; max-width: 1300px; margin: 0 auto; }
                    .header-flex { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px; }
                    h2 { margin: 0; }
                    .actions-bar { display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }
                    input[type="text"] { padding: 10px 14px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 0.95rem; width: 300px; }
                    .btn { padding: 10px 16px; background: #2563eb; color: #fff; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; text-decoration: none; font-size: 0.9rem; display: inline-block; }
                    .btn-success { background: #16a34a; }
                    .btn:hover { opacity: 0.9; }
                    table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
                    th, td { padding: 12px 14px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 0.85rem; }
                    th { background: #2563eb; color: #fff; }
                    tr:hover { background: #f1f5f9; }
                    select.status-select { padding: 6px 10px; border-radius: 6px; border: 1px solid #cbd5e1; font-weight: 600; font-size: 0.85rem; cursor: pointer; }
                    .status-pendente { background: #fef3c7; color: #d97706; }
                    .status-concluido { background: #dcfce7; color: #15803d; }
                    .status-invalido { background: #fee2e2; color: #dc2626; }
                    .tag-geral { background: #dbeafe; color: #1e40af; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
                    .tag-kids { background: #fef3c7; color: #b45309; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
                    .btn-excluir { background: #dc2626; color: #fff; border: none; padding: 6px 10px; border-radius: 6px; cursor: pointer; font-size: 0.85rem; font-weight: bold; }
                    .btn-excluir:hover { background: #b91c1c; }
                </style>
            </head>
            <body>
                <div class="header-flex">
                    <h2>Painel de Controle - Inscrições Geral & Kids</h2>
                    <a href="/admin/exportar" class="btn btn-success">📥 Exportar para CSV / Excel</a>
                </div>

                <div class="actions-bar">
                    <input type="text" id="searchInput" placeholder="Pesquisar por nome, igreja, responsável..." onkeyup="filtrarTabela()">
                </div>

                <table id="tabelaInscricoes">
                    <thead>
                        <tr>
                            <th>ID</th><th>Categoria</th><th>Tipo</th><th>Nome</th><th>Idade</th><th>Contato / Resp.</th><th>Igreja</th><th>Status</th><th>Data</th><th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>"""
            
            if not rows:
                html_tabela += "<tr id='vazioRow'><td colspan='10' style='text-align: center; color: #64748b;'>Nenhuma inscrição cadastrada ainda.</td></tr>"
            else:
                for row in rows:
                    r_id, categoria, tipo, nome, idade, telefone, igreja, resp_nome, resp_tel, status, data_reg = row
                    
                    status_class = "status-pendente"
                    if status == "Concluído": status_class = "status-concluido"
                    elif status == "Inválido": status_class = "status-invalido"

                    cat_badge = f'<span class="tag-geral">Geral</span>' if categoria == 'Geral' else f'<span class="tag-kids">Kids</span>'
                    
                    if categoria == 'Kids':
                        contato_info = f"<b>Resp:</b> {resp_nome}<br><b>Tel:</b> {resp_tel}"
                    else:
                        contato_info = f"<b>Tel:</b> {telefone}"

                    html_tabela += f"""
                    <tr>
                        <td>{r_id}</td>
                        <td>{cat_badge}</td>
                        <td>{tipo}</td>
                        <td><b>{nome}</b></td>
                        <td>{idade} anos</td>
                        <td>{contato_info}</td>
                        <td>{igreja}</td>
                        <td>
                            <select class="status-select {status_class}" onchange="atualizarStatus({r_id}, this)">
                                <option value="Pendente" {'selected' if status == 'Pendente' else ''}>Pendente</option>
                                <option value="Concluído" {'selected' if status == 'Concluído' else ''}>Concluído</option>
                                <option value="Inválido" {'selected' if status == 'Inválido' else ''}>Inválido</option>
                            </select>
                        </td>
                        <td>{data_reg}</td>
                        <td>
                            <button class="btn-excluir" onclick="excluirInscricao({r_id})">Excluir</button>
                        </td>
                    </tr>"""
            
            html_tabela += """
                    </tbody>
                </table>

                <script>
                    function filtrarTabela() {
                        let input = document.getElementById("searchInput").value.toLowerCase();
                        let table = document.getElementById("tabelaInscricoes");
                        let tr = table.getElementsByTagName("tr");

                        for (let i = 1; i < tr.length; i++) {
                            let row = tr[i];
                            if (row.id === "vazioRow") continue;
                            let text = row.innerText.toLowerCase();
                            if (text.includes(input)) {
                                row.style.display = "";
                            } else {
                                row.style.display = "none";
                            }
                        }
                    }

                    function atualizarStatus(id, selectElement) {
                        let novoStatus = selectElement.value;
                        selectElement.className = "status-select";
                        if (novoStatus === "Concluído") selectElement.classList.add("status-concluido");
                        else if (novoStatus === "Inválido") selectElement.classList.add("status-invalido");
                        else selectElement.classList.add("status-pendente");

                        fetch('/admin/status', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                            body: 'id=' + id + '&status=' + encodeURIComponent(novoStatus)
                        }).then(res => {
                            if (!res.ok) alert('Erro ao atualizar status');
                        });
                    }

                    function excluirInscricao(id) {
                        if (confirm('Tem certeza que deseja excluir esta inscrição?')) {
                            fetch('/admin/excluir', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                                body: 'id=' + id
                            }).then(res => {
                                if (res.ok) {
                                    location.reload();
                                } else {
                                    alert('Erro ao excluir');
                                }
                            });
                        }
                    }
                </script>
            </body>
            </html>"""
            
            self.wfile.write(html_tabela.encode("utf-8"))
            return

        elif path == '/admin/exportar':
            self.send_response(200)
            self.send_header("Content-type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", "attachment; filename=inscricoes_evento_completo.csv")
            self.end_headers()

            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, categoria, tipo, nome, idade, telefone, igreja, responsavel_nome, responsavel_tel, status, data_registro 
                FROM inscricoes ORDER BY id DESC
            """)
            rows = cursor.fetchall()
            conn.close()

            output = io.StringIO()
            writer = csv.writer(output, delimiter=';')
            writer.writerow(["ID", "Categoria", "Tipo", "Nome", "Idade", "Telefone", "Igreja", "Responsável Nome", "Responsável Tel", "Status", "Data de Registro"])
            for row in rows:
                writer.writerow(row)
            
            self.wfile.write(output.getvalue().encode("utf-8-sig"))
            return

        # Rota padrão '/' (Geral)
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        page = HTML_FORM.replace("{{ALERT}}", "")
        self.wfile.write(page.encode("utf-8"))

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = urllib.parse.parse_qs(post_data)

        if self.path == '/pagamento':
            categoria = params.get('categoria', ['Geral'])[0].strip()
            tipo = params.get('tipo', ['Participante'])[0].strip()
            nome = params.get('nome', [''])[0].strip()
            idade = params.get('idade', [''])[0].strip()
            igreja = params.get('igreja', [''])[0].strip()
            
            if categoria == 'Kids':
                valor = VALOR_KIDS
                valor_str = f"{VALOR_KIDS:.2f}".replace('.', ',')
                telefone = params.get('resp_tel', [''])[0].strip()
                resp_nome = params.get('resp_nome', [''])[0].strip()
                resp_tel = params.get('resp_tel', [''])[0].strip()
                voltar_url = "/kids"
            else:
                valor = VALOR_GERAL
                valor_str = f"{VALOR_GERAL:.2f}".replace('.', ',')
                telefone = params.get('telefone', [''])[0].strip()
                resp_nome = ""
                resp_tel = ""
                voltar_url = "/"

            if not nome or not idade or not igreja:
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                alert = '<div class="alert alert-error">Preencha todos os campos corretamente.</div>'
                target_form = HTML_FORM_KIDS if categoria == 'Kids' else HTML_FORM
                page = target_form.replace("{{ALERT}}", alert)
                self.wfile.write(page.encode("utf-8"))
                return

            pix_payload = gerar_payload_pix(
                chave=PIX_CHAVE,
                nome=PIX_RECEBEDOR,
                cidade=PIX_CIDADE,
                valor=valor,
                txid=f"EVT{telefone[-4:] if len(telefone)>=4 else '0000'}"
            )

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            
            page = HTML_PAGAMENTO.replace("{{NOME}}", nome)\
                                   .replace("{{CATEGORIA}}", categoria)\
                                   .replace("{{TIPO}}", tipo)\
                                   .replace("{{IDADE}}", idade)\
                                   .replace("{{TELEFONE}}", telefone)\
                                   .replace("{{IGREJA}}", igreja)\
                                   .replace("{{RESP_NOME}}", resp_nome)\
                                   .replace("{{RESP_TEL}}", resp_tel)\
                                   .replace("{{VALOR_STR}}", valor_str)\
                                   .replace("{{PIX_PAYLOAD}}", pix_payload)\
                                   .replace("{{VOLTAR_URL}}", voltar_url)
            self.wfile.write(page.encode("utf-8"))

        elif self.path == '/finalizar':
            categoria = params.get('categoria', ['Geral'])[0].strip()
            tipo = params.get('tipo', ['Participante'])[0].strip()
            nome = params.get('nome', [''])[0].strip()
            idade_str = params.get('idade', [''])[0].strip()
            telefone = params.get('telefone', [''])[0].strip()
            igreja = params.get('igreja', [''])[0].strip()
            resp_nome = params.get('resp_nome', [''])[0].strip()
            resp_tel = params.get('resp_tel', [''])[0].strip()

            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO inscricoes (categoria, tipo, nome, idade, telefone, igreja, responsavel_nome, responsavel_tel, status) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (categoria, tipo, nome, int(idade_str), telefone, igreja, resp_nome, resp_tel, 'Pendente')
                )
                conn.commit()
                conn.close()
            except Exception as e:
                print("Erro ao salvar:", e)

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_SUCESSO.encode("utf-8"))

        elif self.path == '/admin/status':
            r_id = params.get('id', [''])[0].strip()
            novo_status = params.get('status', [''])[0].strip()
            
            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()        
                cursor.execute("UPDATE inscricoes SET status = ? WHERE id = ?", (novo_status, r_id))
                conn.commit()
                conn.close()
                self.send_response(200)
            except Exception:
                self.send_response(500)
            self.end_headers()

        elif self.path == '/admin/excluir':
            r_id = params.get('id', [''])[0].strip()
            
            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM inscricoes WHERE id = ?", (r_id,))
                conn.commit()
                conn.close()
                self.send_response(200)
            except Exception:
                self.send_response(500)
            self.end_headers()

if __name__ == '__main__':
    init_db()
    #server_address = ('', 8080)
    #httpd = HTTPServer(server_address, SimpleServer)
    #print("Servidor rodando em http://localhost:8080 ... Pressione Ctrl+C para parar.")
    #httpd.serve_forever()



    port = int(os.environ.get("PORT", 8080))
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleServer)
    print(f"Servidor rodando na porta {port}...")
    httpd.serve_forever()
