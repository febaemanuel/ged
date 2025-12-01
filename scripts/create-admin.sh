#!/bin/bash
echo "👤 Criar Admin"
read -p "Nome: " NOME
read -p "Email: " EMAIL
read -sp "Senha: " SENHA
echo ""

docker compose exec -T web python3 << PYTHON
from app import create_app
from app.models import db, Usuario
app = create_app('production')
with app.app_context():
    admin = Usuario(nome='$NOME', email='$EMAIL', perfil='administrador', ativo=True)
    admin.set_password('$SENHA')
    db.session.add(admin)
    db.session.commit()
    print('✅ Admin criado:', admin.email)
PYTHON
