#!/usr/bin/env python
"""
Script de Teste Rápido - Verifica se todos os imports estão funcionando
"""

import sys

def test_imports():
    """Testa imports básicos do sistema"""
    print("🧪 Testando imports do sistema GED...\n")

    errors = []

    # Teste 1: Config
    try:
        print("✓ Importando config...")
        from config import Config
        print("  ✅ Config OK")
    except Exception as e:
        errors.append(f"❌ Config falhou: {e}")
        print(f"  ❌ Erro: {e}")

    # Teste 2: Models
    try:
        print("✓ Importando models...")
        from app.models import (
            db, Usuario, Documento, Tarefa, LogAI,
            ListaMestra, BlocoAssinatura, ItemBlocoAssinatura,
            ValidacaoUGQ, Notificacao, TemplateDocumento, Comentario
        )
        print("  ✅ Todos os modelos importados com sucesso")
        print(f"    - TemplateDocumento: {TemplateDocumento}")
        print(f"    - Comentario: {Comentario}")
    except Exception as e:
        errors.append(f"❌ Models falhou: {e}")
        print(f"  ❌ Erro: {e}")

    # Teste 3: Routes
    try:
        print("✓ Importando routes...")
        from app.routes import (
            auth_bp, documento_bp, documentos_api_bp,
            tarefa_bp, ia_bp, dashboard_bp, view_bp,
            busca_bp, template_bp, comentario_bp,
            dashboard_executivo_bp
        )
        print("  ✅ Todos os blueprints importados")
        print(f"    - template_bp: {template_bp}")
        print(f"    - comentario_bp: {comentario_bp}")
        print(f"    - dashboard_executivo_bp: {dashboard_executivo_bp}")
    except Exception as e:
        errors.append(f"❌ Routes falhou: {e}")
        print(f"  ❌ Erro: {e}")

    # Teste 4: App
    try:
        print("✓ Criando app...")
        from app import create_app
        app = create_app('testing')
        print("  ✅ App criado com sucesso")

        # Lista blueprints registrados
        print("\n  📋 Blueprints registrados:")
        for blueprint in app.blueprints:
            print(f"    - {blueprint}")

    except Exception as e:
        errors.append(f"❌ App falhou: {e}")
        print(f"  ❌ Erro: {e}")

    # Resultado final
    print("\n" + "="*60)
    if errors:
        print("❌ TESTES FALHARAM!\n")
        for error in errors:
            print(f"  {error}")
        print("\n⚠️  Corrija os erros antes de iniciar o servidor.")
        return False
    else:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("\n🎉 Sistema pronto para iniciar!")
        print("\nPara iniciar o servidor:")
        print("  python app.py")
        return True

if __name__ == '__main__':
    success = test_imports()
    sys.exit(0 if success else 1)
