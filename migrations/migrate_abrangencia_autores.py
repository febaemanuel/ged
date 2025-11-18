"""
Migração: Adicionar campos abrangencia e autores
Data: 2025-11-18

Este script adiciona os novos campos:
- abrangencia (VARCHAR(100)) aos modelos Documento e ListaMestra
- autores (TEXT) ao modelo Documento

Uso:
    python migrations/migrate_abrangencia_autores.py
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

def migrate():
    """Executa a migração do banco de dados"""
    app = create_app()

    with app.app_context():
        print("=" * 80)
        print("MIGRAÇÃO: Adicionar campos abrangencia e autores")
        print("=" * 80)

        try:
            # 1. Adicionar campo abrangencia à tabela documentos
            print("\n1. Adicionando campo 'abrangencia' à tabela 'documentos'...")
            db.session.execute(text("""
                ALTER TABLE documentos
                ADD COLUMN IF NOT EXISTS abrangencia VARCHAR(100)
            """))
            print("   ✓ Campo 'abrangencia' adicionado com sucesso!")

            # 2. Adicionar campo autores à tabela documentos
            print("\n2. Adicionando campo 'autores' à tabela 'documentos'...")
            db.session.execute(text("""
                ALTER TABLE documentos
                ADD COLUMN IF NOT EXISTS autores TEXT
            """))
            print("   ✓ Campo 'autores' adicionado com sucesso!")

            # 3. Adicionar campo abrangencia à tabela lista_mestra
            print("\n3. Adicionando campo 'abrangencia' à tabela 'lista_mestra'...")
            db.session.execute(text("""
                ALTER TABLE lista_mestra
                ADD COLUMN IF NOT EXISTS abrangencia VARCHAR(100)
            """))
            print("   ✓ Campo 'abrangencia' adicionado com sucesso!")

            # Commit das alterações
            db.session.commit()

            print("\n" + "=" * 80)
            print("MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("=" * 80)
            print("\nPróximos passos:")
            print("1. Os campos 'abrangencia' e 'autores' foram adicionados ao banco")
            print("2. Documentos existentes terão abrangencia=NULL e autores=NULL")
            print("3. Novos documentos precisarão definir a abrangência na validação")
            print("4. Os autores serão extraídos automaticamente pela IA")
            print("=" * 80)

            return True

        except Exception as e:
            print(f"\n❌ ERRO durante a migração: {str(e)}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
