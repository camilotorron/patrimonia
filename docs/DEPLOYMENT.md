# Guía de Deployment

## Requisitos del Servidor

- Ubuntu 20.04+ / macOS / Windows con Docker
- Docker 20.10+
- Docker Compose 2.0+
- 2GB RAM mínimo
- 20GB disco

## Instalación inicial

```bash
# 1. Clonar repo
git clone https://github.com/yourusername/patrimonia.git
cd patrimonia

# 2. Configurar variables de entorno
cp .env.example .env.prod
# Editar .env.prod con tus valores de producción

# 3. Levantar con Docker Compose (producción)
docker-compose -f docker-compose.prod.yml up -d

# 4. Verificar health
curl http://localhost:8000/health
# {"status": "ok"}
```

## PostgreSQL (Producción)

El `docker-compose.prod.yml` incluye PostgreSQL 15 con:
- Persistencia de datos (volumen `pgdata`)
- Health checks automáticos
- Reinicio automático (`restart: unless-stopped`)

## Mantenimiento

### Backup

```bash
# Backup de SQLite
make backup

# Backup de PostgreSQL
docker-compose -f docker-compose.prod.yml exec db \
    pg_dump -U patrimonio patrimonio > backup_$(date +%Y%m%d).sql
```

### Logs

```bash
# Ver logs en tiempo real
docker-compose -f docker-compose.prod.yml logs -f

# Logs de un servicio específico
docker-compose -f docker-compose.prod.yml logs -f app
```

### Actualizar

```bash
git pull origin main
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

## Troubleshooting

| Problema | Solución |
|----------|---------|
| App no arranca | `docker-compose logs app` para ver errores |
| BD no conecta | Verificar credenciales en `.env.prod` |
| Puerto ocupado | Cambiar `ports` en docker-compose |
| Precios no actualizan | Verificar conectividad a internet del contenedor |
