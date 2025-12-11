# 🏠 Dashboard Personal - Ivan Tintore

Tu centro de control personal para todas tus herramientas de trabajo.

## 🚀 Quick Start

```bash
# Iniciar todo
./scripts/start-all.sh

# O manualmente:
docker-compose up -d

# Acceder a: http://localhost
# Login: admin / demo123
```

## 📱 Aplicaciones Incluidas

| App | Ruta | Tecnología | Estado |
|-----|------|------------|--------|
| Dashboard | `/` | Astro | ✅ |
| Conversor HEIF | `/conversor/` | FastAPI + Python | ✅ |
| AEAT Notificaciones | `/aeat/` | FastAPI + Streamlit + Celery | 🔧 |
| Intrastat Manager | `/intrastat/` | Node.js | 🔧 |
| Taxi Management | `/taxi/` | Node.js + SQLite | 🔧 |
| Adela Finanzas | `/adela/` | Node.js + SQLite | 🔧 |
| Toroidal Propellers | `/toroidal/` | Flask | 🔧 |

✅ = Funcionando en PoC
🔧 = Configurado, listo para activar

## 🛠️ Scripts de Gestión

```bash
./scripts/start-all.sh   # Iniciar todos los servicios
./scripts/stop-all.sh    # Detener todos los servicios
./scripts/status.sh      # Ver estado de servicios
./scripts/backup.sh      # Crear backup de datos
```

## 📁 Estructura

```
poc-dashboard/
├── docker-compose.yml      # Stack básico (PoC)
├── docker-compose.full.yml # Stack completo (todas las apps)
├── Caddyfile               # Configuración reverse proxy
├── dashboard-web/          # Frontend Astro
├── apps/                   # Aplicaciones (symlinks)
│   ├── conversor-heif/
│   ├── aeat-notificaciones/
│   ├── intrastat-manager/
│   ├── taxi-management/
│   ├── adela-finanzas/
│   └── toroidal-project/
├── scripts/                # Scripts de gestión
└── LOGS/                   # Logs de operaciones
```

## 🔐 Seguridad

- HTTP Basic Auth en todas las rutas
- Credenciales por defecto: `admin` / `demo123`
- Cambiar en producción via Caddyfile

## 🌍 Deploy en Producción

Ver `docker-compose.full.yml` y descomentar sección de producción en `Caddyfile`.

Opciones recomendadas:
- Hetzner + Coolify
- DigitalOcean Droplet
- VPS con Docker

---
© 2025 MAITSA - Ivan Tintore

