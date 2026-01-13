#!/bin/bash

echo "========================================"
echo "  DEPLOY - LEMPAY.ONLINE"
echo "========================================"

cd /var/www/lempay.online

echo ""
echo "[1/4] Atualizando codigo do Git..."
git pull origin main

echo ""
echo "[2/4] Instalando dependencias..."
/var/www/lempay.online/venv/bin/pip install -r requirements.txt --quiet

echo ""
echo "[3/4] Ajustando permissoes..."
chown -R www-data:www-data /var/www/lempay.online

echo ""
echo "[4/4] Reiniciando servicos..."
systemctl restart lempay
systemctl reload nginx

echo ""
echo "========================================"
echo "  DEPLOY CONCLUIDO!"
echo "========================================"
systemctl status lempay --no-pager | head -5
echo ""
echo "Acesse: https://lempay.online"
echo "========================================"
