# Contributing Guide

¡Gracias por tu interés en contribuir a Patrimonia! 🎉

## 🚀 Git Workflow

Usamos un flujo basado en GitFlow simplificado:

1. **`main`** — Código en producción
2. **`develop`** — Rama de integración
3. **`feature/*`** — Nuevas features
4. **`fix/*`** — Bug fixes

### Flujo de trabajo

```bash
# Crear rama desde develop
git checkout develop
git pull origin develop
git checkout -b feature/mi-nueva-feature

# Hacer commits
git add .
git commit -m "feat: añadir filtro por moneda"

# Push y crear PR
git push origin feature/mi-nueva-feature
# Crear PR en GitHub hacia develop
```

## 📝 Convención de Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

| Tipo | Descripción |
|------|-------------|
| `feat:` | Nueva funcionalidad |
| `fix:` | Bug fix |
| `docs:` | Documentación |
| `style:` | Formato (sin cambio de lógica) |
| `refactor:` | Refactor de código |
| `test:` | Tests |
| `chore:` | Tareas de mantenimiento |

Ejemplo: `feat: añadir exportación de reportes a CSV`

## 🧪 Tests

- Todo nuevo código debe incluir tests
- Mínimo 80% de cobertura
- Ejecutar antes de commit:

```bash
make test
```

## 🧹 Code Style

Usamos **Ruff** para lint y format:

```bash
# Verificar
make check

# Formatear automáticamente
make format
```

### Reglas principales

- **Line length:** 100 caracteres
- **Imports:** Ordenados con isort (integrado en ruff)
- **Quotes:** Dobles (`"`)
- **Type hints:** Obligatorios en funciones públicas

## 🔒 Pre-commit Hooks

Los hooks se ejecutan automáticamente antes de cada commit:

- `ruff check` — Lint
- `ruff format` — Formato

Instalación:
```bash
poetry run pre-commit install
```

## ✅ Checklist del PR

- [ ] El código pasa `make check` sin errores
- [ ] Los tests pasan (`make test`)
- [ ] Cobertura ≥ 80%
- [ ] Documentación actualizada
- [ ] Commits siguen la convención
