"""
Script de exemplo para testar a API do Sistema GED

Execute:
    python test_api.py
"""

import requests
import json

BASE_URL = 'http://localhost:5000'
session = requests.Session()


def print_response(response, title="Response"):
    """Imprime resposta de forma formatada"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)
    print(f"{'='*60}\n")


def test_login():
    """Testa login"""
    print("\n>>> Testando Login...")

    response = session.post(
        f"{BASE_URL}/auth/login",
        json={
            'email': 'admin@example.com',
            'senha': 'admin123'
        }
    )

    print_response(response, "Login")

    if response.status_code == 200:
        print("✅ Login bem-sucedido!")
        return True
    else:
        print("❌ Falha no login")
        return False


def test_get_me():
    """Testa endpoint /auth/me"""
    print("\n>>> Testando GET /auth/me...")

    response = session.get(f"{BASE_URL}/auth/me")
    print_response(response, "Informações do Usuário")


def test_listar_usuarios():
    """Lista usuários"""
    print("\n>>> Testando GET /auth/usuarios...")

    response = session.get(f"{BASE_URL}/auth/usuarios")
    print_response(response, "Lista de Usuários")


def test_criar_documento():
    """Testa criação de documento"""
    print("\n>>> Testando POST /documento/criar...")

    # Cria um arquivo de exemplo
    files = {
        'arquivo': ('exemplo.txt', b'Conteudo do documento de exemplo', 'text/plain')
    }

    data = {
        'titulo': 'Documento de Teste via API',
        'tipo_documento': 'POP',
        'descricao': 'Documento criado automaticamente via script de teste',
        'setor': 'TI',
        'validade_anos': 5
    }

    response = session.post(
        f"{BASE_URL}/documento/criar",
        data=data,
        files=files
    )

    print_response(response, "Criar Documento")

    if response.status_code == 201:
        doc_id = response.json().get('documento', {}).get('id')
        print(f"✅ Documento criado! ID: {doc_id}")
        return doc_id
    else:
        print("❌ Falha ao criar documento")
        return None


def test_listar_documentos():
    """Lista documentos"""
    print("\n>>> Testando GET /documento/lista...")

    response = session.get(f"{BASE_URL}/documento/lista")
    print_response(response, "Lista de Documentos")


def test_visualizar_documento(doc_id):
    """Visualiza documento específico"""
    print(f"\n>>> Testando GET /documento/{doc_id}...")

    response = session.get(f"{BASE_URL}/documento/{doc_id}")
    print_response(response, f"Documento {doc_id}")


def test_criar_tarefa(doc_id):
    """Cria tarefa para documento"""
    print(f"\n>>> Testando POST /tarefa/criar para documento {doc_id}...")

    from datetime import datetime, timedelta

    prazo = (datetime.utcnow() + timedelta(days=7)).isoformat()

    response = session.post(
        f"{BASE_URL}/tarefa/criar",
        json={
            'documento_id': doc_id,
            'responsavel_id': 2,  # Gerente
            'tipo_tarefa': 'Analisar',
            'descricao': 'Analisar documento de teste',
            'prioridade': 'normal',
            'prazo': prazo
        }
    )

    print_response(response, "Criar Tarefa")

    if response.status_code == 201:
        tarefa_id = response.json().get('tarefa', {}).get('id')
        print(f"✅ Tarefa criada! ID: {tarefa_id}")
        return tarefa_id
    else:
        print("❌ Falha ao criar tarefa")
        return None


def test_minhas_tarefas():
    """Lista minhas tarefas"""
    print("\n>>> Testando GET /tarefa/minhas...")

    response = session.get(f"{BASE_URL}/tarefa/minhas")
    print_response(response, "Minhas Tarefas")


def test_dashboard():
    """Testa dashboard"""
    print("\n>>> Testando GET /...")

    response = session.get(f"{BASE_URL}/")
    print_response(response, "Dashboard")


def test_stats():
    """Testa estatísticas"""
    print("\n>>> Testando GET /dashboard/stats...")

    response = session.get(f"{BASE_URL}/dashboard/stats")
    print_response(response, "Estatísticas")


def test_busca():
    """Testa busca"""
    print("\n>>> Testando GET /search?q=teste...")

    response = session.get(f"{BASE_URL}/search?q=teste")
    print_response(response, "Busca")


def main():
    """Executa todos os testes"""
    print("\n" + "="*60)
    print("TESTE DA API DO SISTEMA GED")
    print("="*60)

    # 1. Login
    if not test_login():
        print("\n❌ Não foi possível fazer login. Verifique se o servidor está rodando e os dados de acesso estão corretos.")
        return

    # 2. Informações do usuário
    test_get_me()

    # 3. Listar usuários
    test_listar_usuarios()

    # 4. Dashboard
    test_dashboard()

    # 5. Estatísticas
    test_stats()

    # 6. Listar documentos
    test_listar_documentos()

    # 7. Criar documento
    doc_id = test_criar_documento()

    if doc_id:
        # 8. Visualizar documento criado
        test_visualizar_documento(doc_id)

        # 9. Criar tarefa para documento
        tarefa_id = test_criar_tarefa(doc_id)

    # 10. Minhas tarefas
    test_minhas_tarefas()

    # 11. Busca
    test_busca()

    print("\n" + "="*60)
    print("TESTES CONCLUÍDOS!")
    print("="*60)
    print("\n✅ Script de teste executado com sucesso!")
    print("\nPara mais testes, use ferramentas como Postman ou Insomnia")
    print("Documentação completa em: http://localhost:5000/home")


if __name__ == '__main__':
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO: Não foi possível conectar ao servidor.")
        print("Certifique-se de que o servidor Flask está rodando:")
        print("    python app.py")
        print("ou")
        print("    flask run")
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
