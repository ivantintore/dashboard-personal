# 🎯 PROYECTO: Dashboard Personal de Herramientas - Ivan Tintore

## 📌 CONTEXTO EJECUTIVO

Soy Ivan, CEO de MAITSA. Necesito centralizar TODAS mis herramientas de trabajo en un dashboard personal accesible desde cualquier lugar (oficina, casa, avión, móvil).

**Problema actual:**
- Proyectos dispersos en mi Mac que solo funcionan en local
- No puedo acceder cuando viajo
- Pierdo tiempo levantándolos manualmente cada vez

**Solución objetivo:**
- Dashboard personal con autenticación (SOLO yo accedo)
- Todas mis herramientas funcionando 24/7
- Accesible desde cualquier dispositivo/ubicación
- Backup automático y seguro

---

## 📊 INVENTARIO COMPLETO DE PROYECTOS

### GRUPO A: Públicos (sin autenticación)

| Proyecto | Stack | Estado | Acción |
|----------|-------|--------|--------|
| `sexyfly-reservas` | HTML/JS | ✅ Funcionando en Vercel | ✅ Mantener, solo referenciar |
| `juegos-clasicos` | Python/HTML | 🔄 Necesita optimización | 🎯 FASE 1 |
| `De-Pascal-a-IA-Moderna` | HTML | 🔄 Necesita optimización | 🎯 FASE 1 |

**GitHub:** https://github.com/ivantintore

---

### GRUPO B: Privados (CON autenticación - solo yo)

| # | Proyecto | Stack | Ubicación Local | Datos |
|---|----------|-------|-----------------|-------|
| 1 | Conversor HEIF | FastAPI/Python | `/Users/ivantintore/conversor-heif-jpg/conversor-heif-jpg` | 🟡 Herramienta |
| 2 | Toroidal Propellers | Flask/Python | `/Users/ivantintore/Toroidal_Propellers/toroidal_project` | 🟡 Herramienta |
| 3 | Intrastat Manager | JavaScript | `/Users/ivantintore/Alstom/intrastat-manager-alstom` | 🔴 Empresa |
| 4 | Taxi Management | Node.js/SQLite | `/Users/ivantintore/taxi-management-barcelona` | 🔴 Clientes |
| 5 | Adela Finanzas | Node.js/SQLite | `/Users/ivantintore/Adela-Subirana` | 🔴 Personales |
| 6 | AEAT Notificaciones | FastAPI/Streamlit/Celery | `/Users/ivantintore/AEAT Notificaciones v2` | 🔴 Sensibles |

**Nota:** Tengo acceso local a todos estos proyectos en mi Mac.

---

## 🎯 ARQUITECTURA OBJETIVO

```
┌─────────────────────────────────────────────────┐
│      https://dashboard.ivantintore.com          │
│              (Astro + Caddy)                    │
│                                                 │
│  🔐 Login (HTTP Basic Auth via Caddy)          │
│       ↓                                         │
│  📱 Dashboard Grid:                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │   AEAT   │ │ Intrastat│ │   Taxi   │       │
│  └──────────┘ └──────────┘ └──────────┘       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │  Adela   │ │ Conversor│ │ Toroidal │       │
│  └──────────┘ └──────────┘ └──────────┘       │
└─────────────────────────────────────────────────┘
              ↓
       Caddy (Reverse Proxy)
              ↓
┌─────────────────────────────────────────────────┐
│    Backend Services (Docker Compose)            │
│  ├─ dashboard-web:3000 (Astro)                  │
│  ├─ aeat-api:3001                               │
│  ├─ aeat-streamlit:8501                         │
│  ├─ intrastat:3002                              │
│  ├─ taxi:3003                                   │
│  ├─ adela:3004                                  │
│  ├─ conversor:8000                              │
│  ├─ toroidal:5000                               │
│  ├─ postgres:5432                               │
│  └─ redis:6379                                  │
└─────────────────────────────────────────────────┘
```

---

## 🏗️ STACK TECNOLÓGICO APROBADO

| Componente | Tecnología | Justificación |
|------------|------------|---------------|
| **Dashboard Frontend** | Astro | Estático, rápido, perfecto para landing |
| **Reverse Proxy** | Caddy | SSL automático, config simple, auth integrado |
| **Orquestación** | Docker Compose | Manejo de múltiples servicios |
| **Hosting** | Hetzner + Coolify | €5-10/mes, Docker nativo, backups |

**Alternativa hosting:** DigitalOcean + Dokku (~$12/mes)

---

## 📋 PLAN DE EJECUCIÓN - 5 FASES

### ⚡ FASE 0: Proof of Concept (2-3 horas) - PRIORIDAD MÁXIMA

**Objetivo:** Validar que el stack completo funciona ANTES de invertir tiempo en el resto.

**Proyecto piloto:** Conversor HEIF/JPG
- Razón: FastAPI simple, upload de archivos, sin BD, un solo servicio

**Qué vamos a crear:**

```
poc-dashboard/
├── apps/
│   └── conversor-heif/
│       ├── Dockerfile
│       ├── app/
│       └── requirements.txt
├── dashboard-web/          ← Astro minimalista
│   ├── src/
│   │   └── pages/
│   │       ├── index.astro        (login page)
│   │       └── dashboard.astro    (1 card: Conversor)
│   ├── astro.config.mjs
│   └── package.json
├── Caddyfile               ← Config mínima
├── docker-compose.yml      ← 2 servicios: dashboard-web + conversor
├── .env.example
└── README.md
```

**Pasos específicos:**

1. **Dockerizar Conversor HEIF:**
   ```dockerfile
   # Usar Python 3.11 slim
   # Instalar dependencias (Pillow, FastAPI, etc)
   # Health check en /health
   # Puerto 8000
   ```

2. **Dashboard Astro minimalista:**
   ```astro
   // index.astro → Formulario login básico
   // dashboard.astro → 1 card "Conversor HEIF"
   // Diseño: Dark theme, responsive
   ```

3. **Caddyfile mínimo:**
   ```caddy
   localhost {
       basicauth {
           admin JDJhJDE0JGhhc2hlZF9wYXNzd29yZA==
       }
       
       reverse_proxy /conversor* conversor:8000
       reverse_proxy /* dashboard-web:3000
   }
   ```

4. **docker-compose.yml:**
   ```yaml
   services:
     caddy:
       image: caddy:2-alpine
       ports: ["80:80", "443:443"]
       volumes: 
         - ./Caddyfile:/etc/caddy/Caddyfile
     
     dashboard-web:
       build: ./dashboard-web
       ports: ["3000:3000"]
     
     conversor:
       build: ./apps/conversor-heif
       ports: ["8000:8000"]
       volumes:
         - uploads:/app/uploads
   ```

**Criterio de éxito FASE 0:**
- ✅ `docker-compose up` funciona sin errores
- ✅ http://localhost muestra login
- ✅ Tras login → veo dashboard con card "Conversor"
- ✅ Click en card → `/conversor` abre la app
- ✅ Puedo subir una imagen HEIF y convertirla
- ✅ Caddy auth funciona (sin user/pass no accedo)

**Si FASE 0 falla:** Detenemos y replanteamos el stack
**Si FASE 0 funciona:** ✅ Stack validado, continuamos con confianza

---

### 📦 FASE 1: Optimizar Proyectos Públicos (1-2 días)

**Proyectos:**
1. `De-Pascal-a-IA-Moderna` (más simple, HTML estático)
2. `juegos-clasicos` (Python, más complejo)

**Para cada proyecto público:**

1. **Analizar repo en GitHub:**
   - Estructura actual
   - Dependencias
   - Problemas potenciales

2. **Crear Dockerfile optimizado:**
   ```dockerfile
   # Multi-stage si aplica
   # Minimizar capas
   # Health check
   # Non-root user
   # Labels con metadata
   ```

3. **docker-compose.yml funcional:**
   ```yaml
   # Puerto expuesto
   # Volúmenes si necesita
   # Variables de entorno
   # Health check
   ```

4. **README.md profesional (inglés):**
   ```markdown
   # Project Name
   
   ## 🎯 Description
   ## 🚀 Quick Start
   ### With Docker (Recommended)
   ### Without Docker
   ## 📋 Requirements
   ## ⚙️ Configuration
   ## 🏗️ Project Structure
   ## 🐛 Troubleshooting
   ## 📄 License
   ```

5. **Scripts automatizados:**
   - `setup.sh` - Setup inicial
   - `start.sh` - Levantar proyecto
   - `test.sh` - Tests (si aplica)

6. **.env.example:**
   ```bash
   # Todas las variables documentadas
   # Sin valores reales/sensibles
   ```

7. **Validación:**
   ```bash
   # Desde cero en un Mac nuevo:
   git clone <repo>
   cd <repo>
   docker-compose up
   # → Debe funcionar
   ```

**Output esperado FASE 1:**
- ✅ 2 repos públicos listos para clonar y ejecutar
- ✅ Documentación completa
- ✅ Badges en README (tecnologías, Docker, etc)
- ✅ GitHub Actions básico (opcional)

---

### 🔐 FASE 2: Preparar Proyectos Privados (3-5 días)

**Orden de ejecución (complejidad creciente):**

#### FASE 2a: Los más simples (1 día)
1. **Toroidal Propellers** (Flask básico)
2. **Intrastat Manager** (archivos estáticos + JS)

#### FASE 2b: Complejidad media (2 días)
3. **Taxi Management** (Node.js + SQLite)
4. **Adela Finanzas** (Node.js + SQLite)

#### FASE 2c: El complejo (1-2 días)
5. **AEAT Notificaciones** (FastAPI + Streamlit + Celery + PostgreSQL + Redis)

**Para cada proyecto privado:**

1. **Análisis profundo:**
   ```bash
   # Pídeme que te muestre:
   - Estructura de archivos
   - package.json / requirements.txt
   - Configuración actual
   - .env actual (SIN valores sensibles)
   ```

2. **Dockerización:**
   ```dockerfile
   # Dockerfile optimizado
   # Multi-stage builds
   # Gestión de secretos vía .env
   # Volúmenes para datos persistentes
   # Health checks robustos
   ```

3. **docker-compose.yml individual:**
   ```yaml
   # Servicios necesarios
   # Redes internas
   # Volúmenes nombrados
   # Variables de entorno
   # Dependencias entre servicios
   ```

4. **Manejo especial por tipo:**

   **Para proyectos con SQLite (Taxi, Adela):**
   ```yaml
   volumes:
     - ./data/sqlite:/app/data
   # Persistir BD fuera del container
   ```

   **Para proyectos con uploads (Intrastat):**
   ```yaml
   volumes:
     - ./uploads:/app/uploads
   ```

   **Para AEAT (multi-servicio):**
   ```yaml
   services:
     aeat-api:
       # FastAPI
     aeat-streamlit:
       # Streamlit UI
     aeat-worker:
       # Celery worker
     aeat-flower:
       # Celery monitoring
     postgres:
       # Base datos
     redis:
       # Cola de tareas
   ```

5. **README.md (español para uso personal):**
   ```markdown
   # Nombre Proyecto
   
   ## Para qué sirve
   ## Cómo levantar localmente
   ## Variables de entorno importantes
   ## Dónde están los datos
   ## Troubleshooting
   ```

6. **Validación local:**
   ```bash
   cd apps/[proyecto]
   docker-compose up
   # Verificar que funciona standalone
   ```

**Output esperado FASE 2:**
- ✅ 5 proyectos privados dockerizados
- ✅ Cada uno probado standalone
- ✅ Volúmenes de datos configurados
- ✅ Variables de entorno documentadas
- ✅ Health checks funcionando

---

### 🎨 FASE 3: Dashboard Completo (2-3 días)

**Crear repo: `dashboard-personal`**

```
dashboard-personal/
├── apps/
│   ├── aeat-notificaciones/
│   ├── intrastat-manager/
│   ├── taxi-management/
│   ├── adela-finanzas/
│   ├── conversor-heif/
│   └── toroidal-project/
├── dashboard-web/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AppCard.astro
│   │   │   ├── Header.astro
│   │   │   └── Layout.astro
│   │   ├── pages/
│   │   │   ├── index.astro          (login)
│   │   │   └── dashboard.astro      (main grid)
│   │   └── styles/
│   │       └── global.css
│   ├── public/
│   │   └── icons/                   (iconos de cada app)
│   ├── astro.config.mjs
│   └── package.json
├── Caddyfile
├── docker-compose.yml               (orquesta TODO)
├── scripts/
│   ├── start-all.sh
│   ├── stop-all.sh
│   ├── status.sh
│   ├── logs.sh
│   ├── backup.sh
│   └── change-password.sh
├── .env
├── .env.example
├── README.md
├── DEPLOYMENT.md
└── .gitignore
```

#### 3.1 Dashboard Web (Astro)

**Design system:**
```css
/* Variables globales */
:root {
  --bg-dark: #0a0a0a;
  --bg-card: #1a1a1a;
  --accent: #0070f3;
  --text-primary: #ffffff;
  --text-secondary: #888888;
}
```

**Layout responsive:**
```astro
---
// dashboard.astro
const apps = [
  {
    id: 'aeat',
    name: 'AEAT Notificaciones',
    description: 'Automatización notificaciones AEAT',
    icon: '📊',
    url: '/aeat',
    tech: 'FastAPI + Streamlit',
    status: 'running'
  },
  {
    id: 'intrastat',
    name: 'Intrastat Manager',
    description: 'Gestión declaraciones Alstom',
    icon: '📦',
    url: '/intrastat',
    tech: 'JavaScript',
    status: 'running'
  },
  // ... resto de apps
];
---

<Layout title="Dashboard - Ivan Tintore">
  <div class="dashboard-grid">
    {apps.map(app => (
      <AppCard {...app} />
    ))}
  </div>
</Layout>
```

**AppCard.astro:**
```astro
---
const { name, description, icon, url, tech, status } = Astro.props;
---

<a href={url} class="app-card">
  <div class="icon">{icon}</div>
  <h3>{name}</h3>
  <p class="description">{description}</p>
  <div class="footer">
    <span class="tech">{tech}</span>
    <span class={`status ${status}`}>
      {status === 'running' ? '🟢' : '🔴'}
    </span>
  </div>
</a>

<style>
  .app-card {
    background: var(--bg-card);
    border-radius: 12px;
    padding: 24px;
    transition: transform 0.2s;
    cursor: pointer;
  }
  
  .app-card:hover {
    transform: translateY(-4px);
  }
  
  /* Responsive grid */
  @media (max-width: 768px) {
    .dashboard-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
```

#### 3.2 Caddyfile completo

```caddy
# Caddyfile
{
    # Configuración global
    email ivan@example.com
}

# Para desarrollo local
localhost {
    # HTTP Basic Auth
    basicauth {
        admin JDJhJDE0JHRlc3RfaGFzaGVk
    }
    
    # Dashboard principal
    reverse_proxy /* dashboard-web:3000
    
    # Apps individuales
    reverse_proxy /aeat/* aeat-api:3001
    reverse_proxy /aeat-ui/* aeat-streamlit:8501
    reverse_proxy /intrastat/* intrastat:3002
    reverse_proxy /taxi/* taxi:3003
    reverse_proxy /adela/* adela:3004
    reverse_proxy /conversor/* conversor:8000
    reverse_proxy /toroidal/* toroidal:5000
}

# Para producción (comentado hasta FASE 4)
# dashboard.ivantintore.com {
#     # Mismo config pero con dominio real
#     # SSL automático de Caddy
# }
```

#### 3.3 docker-compose.yml maestro

```yaml
version: '3.8'

services:
  # Gateway
  caddy:
    image: caddy:2-alpine
    container_name: caddy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
      - caddy_config:/config
    networks:
      - frontend
      - backend

  # Dashboard Web
  dashboard-web:
    build: ./dashboard-web
    container_name: dashboard-web
    restart: unless-stopped
    environment:
      - NODE_ENV=production
    networks:
      - frontend

  # Apps privadas
  aeat-api:
    build: ./apps/aeat-notificaciones
    container_name: aeat-api
    restart: unless-stopped
    environment:
      - DATABASE_URL=${POSTGRES_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - postgres
      - redis
    networks:
      - backend
    volumes:
      - aeat_data:/app/data

  aeat-streamlit:
    build: 
      context: ./apps/aeat-notificaciones
      dockerfile: Dockerfile.streamlit
    container_name: aeat-streamlit
    restart: unless-stopped
    environment:
      - API_URL=http://aeat-api:3001
    depends_on:
      - aeat-api
    networks:
      - backend

  intrastat:
    build: ./apps/intrastat-manager
    container_name: intrastat
    restart: unless-stopped
    volumes:
      - intrastat_uploads:/app/uploads
    networks:
      - backend

  taxi:
    build: ./apps/taxi-management
    container_name: taxi
    restart: unless-stopped
    volumes:
      - taxi_data:/app/data
    networks:
      - backend

  adela:
    build: ./apps/adela-finanzas
    container_name: adela
    restart: unless-stopped
    volumes:
      - adela_data:/app/data
    networks:
      - backend

  conversor:
    build: ./apps/conversor-heif
    container_name: conversor
    restart: unless-stopped
    volumes:
      - conversor_uploads:/app/uploads
    networks:
      - backend

  toroidal:
    build: ./apps/toroidal-project
    container_name: toroidal
    restart: unless-stopped
    networks:
      - backend

  # Infraestructura
  postgres:
    image: postgres:15-alpine
    container_name: postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: redis
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - backend
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge

volumes:
  caddy_data:
  caddy_config:
  postgres_data:
  redis_data:
  aeat_data:
  intrastat_uploads:
  taxi_data:
  adela_data:
  conversor_uploads:
```

#### 3.4 Scripts de gestión

**start-all.sh:**
```bash
#!/bin/bash
echo "🚀 Iniciando Dashboard Personal..."
docker-compose up -d
echo "✅ Dashboard iniciado en http://localhost"
echo "👤 Usuario: admin"
echo "🔑 Contraseña: [ver .env]"
```

**stop-all.sh:**
```bash
#!/bin/bash
echo "🛑 Deteniendo Dashboard..."
docker-compose down
echo "✅ Dashboard detenido"
```

**status.sh:**
```bash
#!/bin/bash
docker-compose ps
```

**backup.sh:**
```bash
#!/bin/bash
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

echo "💾 Backup de PostgreSQL..."
docker-compose exec -T postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB > $BACKUP_DIR/postgres.sql

echo "💾 Backup de SQLite (Taxi)..."
docker cp taxi:/app/data/taxi.db $BACKUP_DIR/taxi.db

echo "💾 Backup de SQLite (Adela)..."
docker cp adela:/app/data/adela.db $BACKUP_DIR/adela.db

echo "✅ Backup completado en $BACKUP_DIR"
```

**change-password.sh:**
```bash
#!/bin/bash
echo "🔑 Cambiar contraseña del dashboard"
read -p "Nuevo usuario: " username
read -sp "Nueva contraseña: " password
echo

# Generar hash bcrypt
docker run --rm caddy:2-alpine caddy hash-password --plaintext "$password"

echo "✅ Copia el hash generado y actualiza el Caddyfile"
```

#### 3.5 Documentación

**README.md:**
```markdown
# 🏠 Dashboard Personal - Ivan Tintore

Dashboard unificado para acceder a todas mis herramientas desde cualquier lugar.

## 🚀 Quick Start

```bash
# Clonar repo
git clone https://github.com/ivantintore/dashboard-personal.git
cd dashboard-personal

# Configurar variables
cp .env.example .env
# Editar .env con tus valores

# Iniciar todo
./scripts/start-all.sh

# Abrir en navegador
http://localhost
```

## 📦 Apps Incluidas

- 📊 **AEAT Notificaciones** - Automatización AEAT
- 📦 **Intrastat Manager** - Declaraciones Alstom
- 🚕 **Taxi Management** - Gestión de taxis
- 💰 **Adela Finanzas** - Finanzas personales
- 🖼️ **Conversor HEIF** - Conversión de imágenes
- 🔧 **Toroidal Propellers** - Calculadora hélices

## 🛠️ Scripts Disponibles

- `./scripts/start-all.sh` - Iniciar dashboard
- `./scripts/stop-all.sh` - Detener dashboard
- `./scripts/status.sh` - Ver estado servicios
- `./scripts/backup.sh` - Backup de datos
- `./scripts/change-password.sh` - Cambiar contraseña

## 🏗️ Estructura

Ver ARCHITECTURE.md para detalles técnicos.

## 🔒 Seguridad

- HTTP Basic Auth via Caddy
- SSL automático en producción
- Datos persistentes en volúmenes Docker
- Backups automáticos

## 📄 License

Privado - Uso personal
```

**DEPLOYMENT.md:**
```markdown
# 🚀 Guía de Deployment

## Opción 1: Hetzner + Coolify (Recomendado)

### Paso 1: Crear servidor
1. Ir a https://hetzner.cloud
2. Crear servidor Ubuntu 22.04 (CPX21: 4GB RAM, €5/mes)
3. Guardar IP pública

### Paso 2: Instalar Coolify
```bash
ssh root@YOUR_SERVER_IP
curl -fsSL https://get.coolify.io | bash
```

### Paso 3: Configurar DNS
```
dashboard.ivantintore.com → YOUR_SERVER_IP
```

### Paso 4: Deploy en Coolify
1. Conectar repo GitHub
2. Configurar variables .env
3. Deploy automático

## Opción 2: DigitalOcean + Dokku

(Similar pero más caro: ~$12/mes)

Ver docs completas en /docs/deployment-digitalocean.md
```

**Validación FASE 3:**
```bash
# Test completo
./scripts/start-all.sh

# Verificar servicios
./scripts/status.sh
# → Todos en "healthy"

# Test navegación
open http://localhost
# → Login funciona
# → Dashboard muestra 6 apps
# → Click en cada app funciona

# Test backup
./scripts/backup.sh
# → Crea backup en ./backups/
```

**Output esperado FASE 3:**
- ✅ Dashboard completo funcionando local
- ✅ Las 6 apps accesibles desde un solo lugar
- ✅ Auth funcionando
- ✅ Scripts de gestión operativos
- ✅ Backups funcionando
- ✅ Documentación completa

---

### 🌍 FASE 4: Deploy en Producción (1-2 días)

**Servidor recomendado: Hetzner CPX21**
- 4GB RAM
- 80GB SSD
- €4.90/mes
- Ubuntu 22.04 LTS

#### 4.1 Preparación del servidor

```bash
# 1. Conectar vía SSH
ssh root@YOUR_SERVER_IP

# 2. Actualizar sistema
apt update && apt upgrade -y

# 3. Instalar Docker
curl -fsSL https://get.docker.com | sh

# 4. Instalar Docker Compose
apt install docker-compose-plugin -y

# 5. Crear usuario no-root
adduser ivan
usermod -aG docker ivan
usermod -aG sudo ivan

# 6. Configurar firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

#### 4.2 Deploy del dashboard

```bash
# Como usuario ivan
su - ivan

# Clonar repo
git clone https://github.com/ivantintore/dashboard-personal.git
cd dashboard-personal

# Configurar .env para producción
cp .env.example .env
nano .env
# Cambiar:
# - POSTGRES_PASSWORD a algo seguro
# - REDIS_PASSWORD a algo seguro
# - Resto de configuración

# Actualizar Caddyfile
nano Caddyfile
# Descomentar sección de producción
# Cambiar localhost por dashboard.ivantintore.com

# Iniciar
docker-compose up -d

# Verificar logs
docker-compose logs -f
```

#### 4.3 Configurar DNS

En tu proveedor DNS (Cloudflare, GoDaddy, etc):
```
Type: A
Name: dashboard
Value: YOUR_SERVER_IP
TTL: Auto
```

Esperar propagación DNS (5-30 minutos)

#### 4.4 Verificar SSL

Caddy genera SSL automáticamente:
```bash
# Ver logs de Caddy
docker-compose logs caddy

# Deberías ver:
# "certificate obtained successfully"
```

Abrir: https://dashboard.ivantintore.com
- ✅ HTTPS funcionando
- ✅ Candado verde en navegador

#### 4.5 Backups automáticos

**Configurar cron:**
```bash
crontab -e

# Añadir:
# Backup diario a las 3 AM
0 3 * * * cd /home/ivan/dashboard-personal && ./scripts/backup.sh >> /home/ivan/backup.log 2>&1

# Limpiar backups antiguos (>30 días)
0 4 * * * find /home/ivan/dashboard-personal/backups -type d -mtime +30 -exec rm -rf {} +
```

**Opcional: Sync a S3/Backblaze:**
```bash
# Instalar rclone
curl https://rclone.org/install.sh | sudo bash

# Configurar remote
rclone config
# Seguir wizard para Backblaze/S3

# Script de sync
#!/bin/bash
# sync-backups.sh
rclone sync /home/ivan/dashboard-personal/backups remote:dashboard-backups

# Añadir a cron
0 5 * * * /home/ivan/sync-backups.sh
```

#### 4.6 Monitoring

**Uptime Robot (gratis):**
1. Ir a https://uptimerobot.com
2. Crear monitor:
   - Type: HTTP(s)
   - URL: https://dashboard.ivantintore.com
   - Interval: 5 minutes
   - Alert contacts: tu email

**Logs centralizados:**
```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs específicos
docker-compose logs -f aeat-api
docker-compose logs -f postgres

# Logs históricos
docker-compose logs --tail=100 aeat-api
```

#### 4.7 Actualizar el dashboard

```bash
# Conectar al servidor
ssh ivan@YOUR_SERVER_IP

cd dashboard-personal

# Pull últimos cambios
git pull

# Rebuild y restart
docker-compose down
docker-compose up -d --build

# Verificar
docker-compose ps
```

**Validación FASE 4:**
- ✅ https://dashboard.ivantintore.com accesible
- ✅ SSL funcionando (candado verde)
- ✅ Todas las apps funcionando
- ✅ Backups automáticos configurados
- ✅ Monitoring activo
- ✅ Logs accesibles

**Output esperado FASE 4:**
- ✅ Dashboard público en producción 24/7
- ✅ Accesible desde cualquier dispositivo
- ✅ Backups diarios automáticos
- ✅ Monitoring configurado
- ✅ Proceso de actualización documentado

---

## 🎯 CRITERIOS DE ÉXITO GLOBAL

Al finalizar las 5 fases, debo tener:

### Técnico:
- ✅ 2 repos públicos optimizados (juegos, curso)
- ✅ 1 repo privado con dashboard unificado
- ✅ 6 apps privadas dockerizadas y funcionando
- ✅ Sistema completo desplegado en producción
- ✅ Backups automáticos configurados
- ✅ Monitoring activo

### Funcional:
- ✅ Puedo acceder desde cualquier lugar (Mac, iPad, iPhone, otro ordenador)
- ✅ Un solo login para todas las herramientas
- ✅ Todas las apps funcionan como antes pero centralizadas
- ✅ Datos persistentes y seguros
- ✅ Sistema fácil de mantener

### Documentación:
- ✅ README claro en cada repo
- ✅ Guía de deployment completa
- ✅ Scripts documentados
- ✅ Variables de entorno explicadas

---

## 💡 METODOLOGÍA DE TRABAJO

### Enfoque iterativo:
1. **Análisis primero** - Muéstrame qué planeas hacer ANTES de ejecutar
2. **Validación continua** - Probar cada paso antes de continuar
3. **Documentar todo** - README, comentarios, decisiones técnicas
4. **Preguntar si hay dudas** - Mejor preguntar que asumir

### Comunicación:
- 🇪🇸 **Español:** Explicaciones técnicas, decisiones, dudas
- 🇬🇧 **Inglés:** Código, comentarios, READMEs proyectos públicos
- 🇪🇸 **Español:** READMEs proyectos privados

### Cuando necesites ver código:
```
"¿Puedes mostrarme el archivo X del proyecto Y?"
"¿Cuál es la estructura de directorios de Z?"
```

Te proporcionaré el contenido para que analices.

---

## ⚙️ CONFIGURACIÓN IMPORTANTE

### Variables de entorno (.env.example):

```bash
# ============================================
# DASHBOARD AUTHENTICATION
# ============================================
DASHBOARD_USER=admin
DASHBOARD_PASSWORD=change_this_password_123

# ============================================
# DATABASE (PostgreSQL for AEAT)
# ============================================
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure_postgres_password_456
POSTGRES_DB=aeat_db

# ============================================
# CACHE/QUEUE (Redis for AEAT)
# ============================================
REDIS_PASSWORD=secure_redis_password_789

# ============================================
# URLS
# ============================================
# Development
BASE_URL=http://localhost

# Production (uncomment for FASE 4)
# BASE_URL=https://dashboard.ivantintore.com

# ============================================
# ENVIRONMENT
# ============================================
NODE_ENV=production
FLASK_ENV=production
ENVIRONMENT=production
```

### Puertos internos (Docker networks):

```
Dashboard Web:      3000
AEAT API:           3001
AEAT Streamlit:     8501
Intrastat:          3002
Taxi:               3003
Adela:              3004
Conversor:          8000
Toroidal:           5000
PostgreSQL:         5432
Redis:              6379
Caddy (HTTP):       80
Caddy (HTTPS):      443
```

**Importante:** Estos puertos son internos a Docker. Externamente solo se exponen 80 y 443 (Caddy).

---

## 🎨 DESIGN GUIDELINES

### Dashboard visual:

**Inspiración:**
- Vercel Dashboard (limpio, moderno)
- Linear (minimalista, dark)
- Notion (cards bien organizadas)

**Colores:**
```css
:root {
  --bg-dark: #0a0a0a;
  --bg-card: #1a1a1a;
  --bg-card-hover: #2a2a2a;
  --accent-blue: #0070f3;
  --accent-green: #00ff88;
  --text-primary: #ffffff;
  --text-secondary: #888888;
  --border: #333333;
}
```

**Tipografía:**
- Sistema: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto
- Monospace: "SF Mono", "Fira Code", Consolas

**Responsive breakpoints:**
```css
/* Mobile */
@media (max-width: 768px) {
  grid-template-columns: 1fr;
}

/* Tablet */
@media (min-width: 769px) and (max-width: 1024px) {
  grid-template-columns: repeat(2, 1fr);
}

/* Desktop */
@media (min-width: 1025px) {
  grid-template-columns: repeat(3, 1fr);
}
```

**Iconos para apps:**
- 📊 AEAT Notificaciones
- 📦 Intrastat Manager
- 🚕 Taxi Management
- 💰 Adela Finanzas
- 🖼️ Conversor HEIF
- 🔧 Toroidal Propellers

---

## 🚨 CONSIDERACIONES IMPORTANTES

### Seguridad:
- ❌ NUNCA hardcodear contraseñas en código
- ✅ SIEMPRE usar variables .env
- ✅ .gitignore debe incluir: `.env`, `*.db`, `uploads/`, `backups/`
- ✅ HTTP Basic Auth es suficiente para uso personal
- ✅ SSL automático en producción vía Caddy

### Datos persistentes:
- SQLite files → Volúmenes Docker
- PostgreSQL → Volumen Docker
- Uploads → Volúmenes Docker
- Backups → Fuera de Docker, opcional sync S3

### Performance:
- Multi-stage Docker builds para reducir tamaño
- Health checks en todos los servicios
- Restart policies: `unless-stopped`
- Logs rotation (Docker maneja automáticamente)

### Mantenimiento:
- Backups diarios automáticos
- Actualizar imágenes Docker mensualmente
- Revisar logs periódicamente
- Monitoring con Uptime Robot

---

## ❓ PREGUNTAS INICIALES

Antes de empezar con FASE 0, necesito que me confirmes:

**A.** ¿Entiendes el objetivo completo del proyecto?

**B.** ¿El stack (Astro + Caddy + Docker) te parece correcto?

**C.** ¿Tienes alguna duda técnica antes de empezar?

**D.** ¿Prefieres que empecemos directamente con FASE 0 o quieres discutir algo primero?

Una vez que me confirmes, comenzaremos con **FASE 0: Proof of Concept** usando el Conversor HEIF.

Espero tu confirmación para arrancar. 🚀

---

**Nota final:** Este prompt es largo y detallado intencionalmente. Contiene toda la información necesaria para ejecutar el proyecto completo sin ambigüedades. Léelo completo antes de empezar a codear.
