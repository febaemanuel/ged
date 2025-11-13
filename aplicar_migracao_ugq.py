#!/usr/bin/env python3
"""
Script para aplicar migration do Workflow UGQ
Adiciona tabelas e campos necessários para o workflow oficial EBSERH
"""
import os
import sys
import psycopg2
from psycopg2 import sql

# Adiciona diretório do projeto ao path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config import Config


def aplicar_migration():
    """Aplica migration do workflow UGQ"""

    print("=" * 80)
    print("APLICAÇÃO DA MIGRATION: Workflow UGQ Centralizado")
    print("=" * 80)
    print()

    # Extrai informações da URI do banco
    db_uri = Config.SQLALCHEMY_DATABASE_URI

    # Parse da URI (formato: postgresql://user:password@host:port/database)
    try:
        # Remove prefixo e query string
        uri = db_uri.replace('postgresql://', '').split('?')[0]
        user_pass, host_port_db = uri.split('@')
        user, password = user_pass.split(':')
        host_port, database = host_port_db.rsplit('/', 1)

        if ':' in host_port:
            host, port = host_port.split(':')
        else:
            host = host_port
            port = '5432'

    except Exception as e:
        print(f"❌ Erro ao fazer parse da URI do banco: {e}")
        print(f"   URI: {db_uri}")
        sys.exit(1)

    print(f"📊 Conectando ao banco de dados:")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Database: {database}")
    print(f"   User: {user}")
    print()

    try:
        # Conecta ao banco
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        conn.set_client_encoding('UTF8')
        cursor = conn.cursor()

        print("✅ Conexão estabelecida com sucesso!")
        print()

        # Lê arquivo SQL
        migration_file = os.path.join(
            os.path.dirname(__file__),
            'migrations',
            'add_workflow_ugq.sql'
        )

        print(f"📄 Lendo arquivo de migration: {migration_file}")

        if not os.path.exists(migration_file):
            print(f"❌ Arquivo de migration não encontrado: {migration_file}")
            sys.exit(1)

        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_commands = f.read()

        print("✅ Arquivo lido com sucesso!")
        print()

        # Executa migration
        print("⚙️  Executando migration...")
        print()

        try:
            cursor.execute(sql_commands)
            conn.commit()
            print("✅ Migration aplicada com sucesso!")
            print()

        except psycopg2.Error as e:
            conn.rollback()
            print(f"❌ Erro ao executar migration:")
            print(f"   {e}")
            sys.exit(1)

        # Verifica tabelas criadas
        print("🔍 Verificando tabelas criadas...")
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN (
                'lista_mestra',
                'blocos_assinatura',
                'itens_bloco_assinatura',
                'validacoes_ugq'
            )
            ORDER BY table_name;
        """)

        tabelas = cursor.fetchall()
        print()
        print("📋 Tabelas do Workflow UGQ:")
        for tabela in tabelas:
            print(f"   ✓ {tabela[0]}")

        print()

        # Verifica campos adicionados
        print("🔍 Verificando campos adicionados nas tabelas existentes...")
        cursor.execute("""
            SELECT column_name, table_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND (
                (table_name = 'documentos' AND column_name IN ('arquivo_final', 'codigo_definitivo', 'versao', 'versao_anterior_id'))
                OR
                (table_name = 'tarefas' AND column_name = 'metadata_json')
            )
            ORDER BY table_name, column_name;
        """)

        campos = cursor.fetchall()
        print()
        print("📝 Campos adicionados:")
        for campo, tabela in campos:
            print(f"   ✓ {tabela}.{campo}")

        print()

        # Verifica views criadas
        print("🔍 Verificando views criadas...")
        cursor.execute("""
            SELECT table_name
            FROM information_schema.views
            WHERE table_schema = 'public'
            AND table_name LIKE 'view_%'
            ORDER BY table_name;
        """)

        views = cursor.fetchall()
        if views:
            print()
            print("👁️  Views criadas:")
            for view in views:
                print(f"   ✓ {view[0]}")

        print()

        # Verifica função criada
        print("🔍 Verificando função criada...")
        cursor.execute("""
            SELECT routine_name
            FROM information_schema.routines
            WHERE routine_schema = 'public'
            AND routine_name = 'gerar_proximo_codigo';
        """)

        funcao = cursor.fetchone()
        if funcao:
            print()
            print("⚡ Função criada:")
            print(f"   ✓ {funcao[0]}()")

        print()

        cursor.close()
        conn.close()

        print("=" * 80)
        print("✅ MIGRATION APLICADA COM SUCESSO!")
        print("=" * 80)
        print()
        print("Próximos passos:")
        print("1. Executar: python init_database.py  (para criar usuários UGQ)")
        print("2. Executar: python app.py             (para iniciar o servidor)")
        print()

        return True

    except psycopg2.Error as e:
        print(f"❌ Erro ao conectar ao banco de dados:")
        print(f"   {e}")
        print()
        print("Verifique:")
        print("  - PostgreSQL está rodando?")
        print("  - Credenciais estão corretas no .env?")
        print("  - Banco de dados existe?")
        sys.exit(1)


if __name__ == '__main__':
    aplicar_migration()
