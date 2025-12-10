# 🏠 Dashboard Personal - RESUMEN COMPLETO
## Ivan Tintore - MAITSA
---

## ✅ ESTADO ACTUAL: EN PRODUCCIÓN

### 🌐 URLs de Acceso:
```
Dashboard:  https://keonycs.com/tools/
Conversor:  https://keonycs.com/tools/conversor/
Raíz:       https://keonycs.com/ (landing "Próximamente")

Login: admin / demo123
```

### 🖥️ Servidor VPS:
```
IP: 46.231.126.152
Usuario: root
Password: 1r6cqJcH
Proveedor: Dinahosting VPS Lite II
Ubicación: /opt/dashboard/
```

---

## 📋 FASES COMPLETADAS

| Fase | Descripción | Estado |
|------|-------------|--------|
| 0 | PoC Conversor HEIF | ✅ |
| 1 | Proyectos públicos (GitHub) | ✅ |
| 2a | Toroidal + Intrastat | ✅ |
| 2b | Taxi + Adela (SQLite) | ✅ |
| 2c | AEAT (multi-servicio) | ✅ |
| 3a | Dashboard Astro | ✅ |
| 3b | Caddy + Docker Compose | ✅ |
| 4 | Deploy producción | ✅ |

---

## 📁 ESTRUCTURA DEL PROYECTO

```
/Users/ivantintore/poc-dashboard/
├── docker-compose.yml        # Stack actual (básico)
├── docker-compose.full.yml   # Stack completo (todas las apps)
├── Caddyfile                 # Configuración local
├── dashboard-web/            # Frontend Astro
├── apps/
│   └── conversor-heif/       # App activa en producción
├── scripts/
│   ├── start-all.sh
│   ├── stop-all.sh
│   └── status.sh
└── LOGS/                     # Logs de operaciones
```

---

## 🔧 COMANDOS ÚTILES

### En tu Mac (local):
```bash
cd /Users/ivantintore/poc-dashboard

# Iniciar local
docker-compose up -d

# Subir cambios al servidor
sshpass -p '1r6cqJcH' rsync -avz ./ root@46.231.126.152:/opt/dashboard/
```

### En el servidor:
```bash
ssh root@46.231.126.152
# Password: 1r6cqJcH

cd /opt/dashboard
docker compose ps              # Ver estado
docker compose logs -f caddy   # Ver logs
docker compose up -d --build   # Reconstruir
docker compose restart caddy   # Reiniciar Caddy
```

---

## 📝 PENDIENTE (Próximas mejoras)

1. **Añadir más apps al servidor:**
   - AEAT Notificaciones
   - Intrastat Manager
   - Taxi Management
   - Adela Finanzas
   - Toroidal Propellers

2. **Cambiar contraseña** de demo123 a algo seguro

3. **Landing page** para keonycs.com (raíz)

4. **Backups automáticos**

---

## 🔐 CREDENCIALES

| Servicio | Usuario | Password |
|----------|---------|----------|
| Dashboard | admin | demo123 |
| VPS SSH | root | 1r6cqJcH |
| Dinahosting | ivantintore | (tu password) |

---

## 📚 REPOS RELACIONADOS

- Dashboard: https://github.com/ivantintore/dashboard-personal (por crear)
- Juegos: https://github.com/ivantintore/juegos-clasicos ✅
- Curso: https://github.com/ivantintore/De-Pascal-a-IA-Moderna-Curso-Completo ✅

---

## 💡 PARA CONTINUAR EN OTRO PC

1. Clona el repo: `git clone https://github.com/ivantintore/dashboard-personal`
2. Conecta al servidor: `ssh root@46.231.126.152`
3. Los archivos están en: `/opt/dashboard/`

---
Generado: $(date)
