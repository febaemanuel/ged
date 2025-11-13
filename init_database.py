"""
Script para inicializar o banco de dados do Sistema GED
Cria todas as tabelas e usuarios padrao
"""

import sys
import os

# Força UTF-8 no Windows
if sys.platform == 'win32':
    import codecs
    # Verifica se tem o atributo buffer antes de tentar modificar
    if hasattr(sys.stdout, 'buffer') and not hasattr(sys.stdout, 'write_through'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if hasattr(sys.stderr, 'buffer') and not hasattr(sys.stderr, 'write_through'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Carrega .env com encoding UTF-8
from dotenv import load_dotenv
load_dotenv(encoding='utf-8')

from app import create_app, db
from app.models import Usuario

print('========================================')
print('Inicializando Banco de Dados GED')
print('========================================')
print()

# Cria a aplicacao
app = create_app()

with app.app_context():
    # Cria todas as tabelas
    print('Criando tabelas...')
    db.create_all()
    print('[OK] Tabelas criadas com sucesso!')
    print()

    # Verifica se ja existem usuarios
    if Usuario.query.count() > 0:
        print('[AVISO] Banco ja possui usuarios. Pulando criacao.')
        print()
    else:
        print('Criando usuarios padrao para WORKFLOW COMPLETO...')
        print()

        # ============================================
        # ADMINISTRADOR (Gestão Documental)
        # ============================================
        admin = Usuario(
            nome='Administrador GED',
            email='admin@example.com',
            perfil='administrador',
            setor='Gestão Documental',
            ativo=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        print('  ✓ Admin criado: admin@example.com')

        # ============================================
        # GERENTES (Chefia Imediata + Aprovador)
        # ============================================
        gerente_producao = Usuario(
            nome='Maria Silva',
            email='maria.silva@example.com',
            perfil='gerente',
            setor='Producao',
            ativo=True
        )
        gerente_producao.set_password('gerente123')
        db.session.add(gerente_producao)
        print('  ✓ Gerente Produção criado: maria.silva@example.com')

        gerente_qualidade = Usuario(
            nome='João Santos',
            email='joao.santos@example.com',
            perfil='gerente',
            setor='Qualidade',
            ativo=True
        )
        gerente_qualidade.set_password('gerente123')
        db.session.add(gerente_qualidade)
        print('  ✓ Gerente Qualidade criado: joao.santos@example.com')

        gerente_operacoes = Usuario(
            nome='Carlos Mendes',
            email='carlos.mendes@example.com',
            perfil='gerente',
            setor='Operacoes',
            ativo=True
        )
        gerente_operacoes.set_password('gerente123')
        db.session.add(gerente_operacoes)
        print('  ✓ Gerente Operações criado: carlos.mendes@example.com')

        # ============================================
        # WORKFLOW UGQ (EBSERH Oficial)
        # ============================================
        # Triador UGQ - ETAPA 1 (Recebimento e Triagem)
        triador_ugq = Usuario(
            nome='Triador UGQ',
            email='triador.ugq@example.com',
            perfil='qualidade_triador',
            setor='UGQ',
            ativo=True
        )
        triador_ugq.set_password('ugq123')
        db.session.add(triador_ugq)
        print('  ✓ Triador UGQ criado: triador.ugq@example.com')

        # Validador UGQ - ETAPAS 2, 3, 4 (Codificação, Bloco Assinatura, Publicação)
        validador_ugq = Usuario(
            nome='Validador UGQ',
            email='validador.ugq@example.com',
            perfil='qualidade_validador',
            setor='UGQ',
            ativo=True
        )
        validador_ugq.set_password('ugq123')
        db.session.add(validador_ugq)
        print('  ✓ Validador UGQ criado: validador.ugq@example.com')

        # ============================================
        # USUÁRIOS COMUNS (Autores)
        # ============================================
        usuario1 = Usuario(
            nome='Rafael Alves',
            email='rafael.alves@example.com',
            perfil='comum',
            setor='Producao',
            ativo=True
        )
        usuario1.set_password('usuario123')
        db.session.add(usuario1)
        print('  ✓ Usuário Produção criado: rafael.alves@example.com')

        usuario2 = Usuario(
            nome='Fernanda Lima',
            email='fernanda.lima@example.com',
            perfil='comum',
            setor='Operacoes',
            ativo=True
        )
        usuario2.set_password('usuario123')
        db.session.add(usuario2)
        print('  ✓ Usuário Operações criado: fernanda.lima@example.com')

        # Mantém usuario@example.com para compatibilidade
        usuario_padrao = Usuario(
            nome='Usuario Exemplo',
            email='usuario@example.com',
            perfil='comum',
            setor='Operacoes',
            ativo=True
        )
        usuario_padrao.set_password('usuario123')
        db.session.add(usuario_padrao)
        print('  ✓ Usuário Padrão criado: usuario@example.com')

        db.session.commit()
        print()
        print('[OK] Todos os usuarios criados com sucesso!')
        print()

    print('========================================')
    print('Banco de dados inicializado!')
    print('========================================')
    print()
    print('✅ USUÁRIOS DO WORKFLOW UGQ (EBSERH Oficial):')
    print()
    print('🔴 ADMINISTRADOR:')
    print('   admin@example.com / admin123')
    print()
    print('🟡 EQUIPE UGQ:')
    print('   triador.ugq@example.com / ugq123 (ETAPA 1: Triagem)')
    print('   validador.ugq@example.com / ugq123 (ETAPAS 2-4: Validação)')
    print()
    print('🔵 APROVADORES (Gerentes):')
    print('   maria.silva@example.com / gerente123 (Produção)')
    print('   joao.santos@example.com / gerente123 (Qualidade)')
    print('   carlos.mendes@example.com / gerente123 (Operações)')
    print()
    print('⚪ AUTORES (Usuários Comuns):')
    print('   rafael.alves@example.com / usuario123 (Produção)')
    print('   fernanda.lima@example.com / usuario123 (Operações)')
    print('   usuario@example.com / usuario123 (Padrão)')
    print()
    print('TOTAL: 9 usuários (Workflow UGQ Oficial)')
    print()
    print('Acesse: http://localhost:5000')
    print('========================================')
    print()
    print('PRÓXIMOS PASSOS:')
    print('  1. Execute: python app.py')
    print('  2. Acesse: http://localhost:5000')
    print('  3. Teste o Workflow UGQ completo!')
    print('========================================')
