"""
Migration: Adiciona tabela de Notificações e campo codigo_unico aos Documentos

Execute este script para atualizar o banco de dados:
    python migration_add_notificacoes_codigo_unico.py

IMPORTANTE: Este script é IDEMPOTENTE - pode ser executado múltiplas vezes sem problema
"""

from app import create_app, db
from datetime import datetime
import random

def run_migration():
    """Executa a migration"""
    app = create_app()

    with app.app_context():
        print("=" * 80)
        print("MIGRATION: Adiciona Notificações e Código Único")
        print("=" * 80)

        # 1. Cria tabela de notificações
        print("\n1. Criando tabela de notificações...")
        try:
            db.session.execute("""
                CREATE TABLE IF NOT EXISTS notificacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL,
                    documento_id INTEGER,
                    tipo VARCHAR(50) NOT NULL,
                    titulo VARCHAR(200) NOT NULL,
                    mensagem TEXT NOT NULL,
                    lida BOOLEAN DEFAULT 0,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data_leitura DATETIME,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                    FOREIGN KEY (documento_id) REFERENCES documentos(id)
                )
            """)

            # Cria índices
            db.session.execute("CREATE INDEX IF NOT EXISTS idx_notificacoes_usuario ON notificacoes(usuario_id)")
            db.session.execute("CREATE INDEX IF NOT EXISTS idx_notificacoes_documento ON notificacoes(documento_id)")
            db.session.execute("CREATE INDEX IF NOT EXISTS idx_notificacoes_lida ON notificacoes(lida)")
            db.session.execute("CREATE INDEX IF NOT EXISTS idx_notificacoes_data ON notificacoes(data_criacao)")

            db.session.commit()
            print("   ✅ Tabela 'notificacoes' criada com sucesso!")
        except Exception as e:
            print(f"   ⚠️  Tabela 'notificacoes' já existe ou erro: {e}")
            db.session.rollback()

        # 2. Adiciona campo codigo_unico aos documentos
        print("\n2. Adicionando campo 'codigo_unico' à tabela documentos...")
        try:
            # Verifica se a coluna já existe
            result = db.session.execute(
                "SELECT COUNT(*) as cnt FROM pragma_table_info('documentos') WHERE name='codigo_unico'"
            ).fetchone()

            if result[0] == 0:
                # Coluna não existe, adiciona
                db.session.execute("""
                    ALTER TABLE documentos
                    ADD COLUMN codigo_unico VARCHAR(50) UNIQUE
                """)
                db.session.commit()
                print("   ✅ Campo 'codigo_unico' adicionado!")

                # 3. Gera códigos únicos para documentos existentes
                print("\n3. Gerando códigos únicos para documentos existentes...")
                from app.models import Documento

                documentos = Documento.query.all()
                for doc in documentos:
                    if not doc.codigo_unico:
                        timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
                        random_suffix = f"{random.randint(0, 999):03d}"
                        doc.codigo_unico = f"DOC-{timestamp}-{random_suffix}"
                        print(f"   📝 Documento #{doc.id}: {doc.codigo_unico}")

                db.session.commit()
                print(f"   ✅ {len(documentos)} documentos atualizados com código único!")

                # Cria índice
                db.session.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_documentos_codigo_unico ON documentos(codigo_unico)")
                db.session.commit()
                print("   ✅ Índice criado para 'codigo_unico'")
            else:
                print("   ⚠️  Campo 'codigo_unico' já existe!")

        except Exception as e:
            print(f"   ❌ Erro ao adicionar campo 'codigo_unico': {e}")
            db.session.rollback()

        print("\n" + "=" * 80)
        print("MIGRATION CONCLUÍDA!")
        print("=" * 80)
        print("\nPróximos passos:")
        print("1. Reinicie o servidor Flask")
        print("2. As notificações agora serão usadas ao invés de tarefas")
        print("3. Todos os documentos terão um código único permanente")
        print("=" * 80)


if __name__ == '__main__':
    run_migration()
