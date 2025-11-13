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
        # RESPONSÁVEIS INTERNOS (Validadores)
        # ============================================
        # Responsável Interno - Qualidade (Valida Padronização)
        resp_qualidade = Usuario(
            nome='Ana Costa',
            email='ana.costa@example.com',
            perfil='responsavel_interno',
            setor='Qualidade',
            ativo=True
        )
        resp_qualidade.set_password('resp123')
        db.session.add(resp_qualidade)
        print('  ✓ Resp. Interno Qualidade criado: ana.costa@example.com')

        # Responsável Interno - Produção (Valida Conteúdo Técnico)
        resp_producao = Usuario(
            nome='Pedro Oliveira',
            email='pedro.oliveira@example.com',
            perfil='responsavel_interno',
            setor='Producao',
            ativo=True
        )
        resp_producao.set_password('resp123')
        db.session.add(resp_producao)
        print('  ✓ Resp. Interno Produção criado: pedro.oliveira@example.com')

        # Responsável Interno - Operações (Valida Conteúdo Técnico)
        resp_operacoes = Usuario(
            nome='Lucia Ferreira',
            email='lucia.ferreira@example.com',
            perfil='responsavel_interno',
            setor='Operacoes',
            ativo=True
        )
        resp_operacoes.set_password('resp123')
        db.session.add(resp_operacoes)
        print('  ✓ Resp. Interno Operações criado: lucia.ferreira@example.com')

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
    print('Usuarios criados para WORKFLOW COMPLETO:')
    print()
    print('🔴 ADMINISTRADOR (Publica documentos):')
    print('   admin@example.com / admin123')
    print()
    print('🔵 GERENTES (Chefia + Aprovador):')
    print('   maria.silva@example.com / gerente123 (Produção)')
    print('   joao.santos@example.com / gerente123 (Qualidade)')
    print('   carlos.mendes@example.com / gerente123 (Operações)')
    print()
    print('🟢 RESPONSÁVEIS INTERNOS (Validadores):')
    print('   ana.costa@example.com / resp123 (Qualidade - Padronização)')
    print('   pedro.oliveira@example.com / resp123 (Produção - Conteúdo)')
    print('   lucia.ferreira@example.com / resp123 (Operações - Conteúdo)')
    print()
    print('⚪ USUÁRIOS COMUNS (Autores):')
    print('   rafael.alves@example.com / usuario123 (Produção)')
    print('   fernanda.lima@example.com / usuario123 (Operações)')
    print('   usuario@example.com / usuario123 (Operações - Padrão)')
    print()
    print('TOTAL: 10 usuários para testar workflow completo!')
    print()
    print('Acesse: http://localhost:5000')
    print('========================================')
    print()
    print('PRÓXIMOS PASSOS:')
    print('  1. Execute: python aplicar_migracao.py')
    print('  2. Reinicie o servidor Flask')
    print('  3. Teste o fluxo completo!')
    print('========================================')
