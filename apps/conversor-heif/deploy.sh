#!/bin/bash

# Script de Deploy para Railway
# Conversor HEIC + PDF a JPG

echo "🚀 Iniciando deploy en Railway..."

# Verificar que estamos en el directorio correcto
if [ ! -f "Dockerfile" ]; then
    echo "❌ Error: No se encontró Dockerfile. Asegúrate de estar en el directorio raíz del proyecto."
    exit 1
fi

# Verificar que git esté configurado
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Este directorio no es un repositorio git."
    exit 1
fi

# Verificar estado de git
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 Hay cambios sin commitear. Haciendo commit automático..."
    git add .
    git commit -m "Deploy automático - $(date)"
fi

# Push a GitHub
echo "📤 Haciendo push a GitHub..."
git push origin main

echo "✅ Deploy iniciado exitosamente!"
echo ""
echo "📋 Pasos para completar el deploy en Railway:"
echo "1. Ve a https://railway.app"
echo "2. Crea una nueva cuenta o inicia sesión"
echo "3. Haz clic en 'New Project'"
echo "4. Selecciona 'Deploy from GitHub repo'"
echo "5. Selecciona tu repositorio: conversor-heif-jpg"
echo "6. Railway detectará automáticamente el Dockerfile"
echo "7. Configura las variables de entorno si es necesario"
echo "8. ¡Listo! Tu aplicación se desplegará automáticamente"
echo ""
echo "🌐 Una vez desplegada, Railway te dará una URL pública"
echo "🔧 Puedes configurar un dominio personalizado en Railway"
echo ""
echo "📚 Para más información, consulta el README.md"

