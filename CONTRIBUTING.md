# Cómo trabajamos en BioLab (flujo de Git)

Usamos **GitHub Flow**: `main` es la línea base y siempre debe funcionar.
Nadie escribe directamente en `main`; todo cambio entra por un Pull Request revisado.

## 1. Una rama corta por cada cambio
Se crea desde `main` actualizado y se borra cuando se fusiona.

| Prefijo | Para qué | Ejemplo |
|---|---|---|
| `feature/` | Funcionalidad nueva | `feature/hu-04-resultados` |
| `fix/` | Corrección de un error | `fix/orden-examen-inexistente` |
| `docs/` | Solo documentación | `docs/flujo-de-trabajo` |
| `refactor/` | Mejorar el código sin cambiar lo que hace | `refactor/blueprints` |

```bash
git switch main
git pull
git switch -c fix/nombre-corto
```

## 2. Commits atómicos
- Un commit = un cambio lógico. No mezclar un refactor con una funcionalidad nueva.
- Primera línea: qué cambia, en imperativo y en menos de 72 caracteres.
- Cuerpo: **por qué** se hizo el cambio y qué problema resuelve.

```
Rechazar órdenes con exámenes inexistentes

Antes la orden se creaba vacía y decía "Presupuesto generado".
```

## 3. Pull Request y revisión
1. Subir la rama: `git push -u origin nombre-de-la-rama`.
2. Abrir el Pull Request hacia `main` y llenar la plantilla.
3. El **otro integrante** revisa el código y aprueba o pide cambios.
   Quien escribe el cambio no lo aprueba.
4. Antes de fusionar deben pasar todas las pruebas (`python -m pytest`).
5. Se fusiona y se borra la rama.

Nunca se suben `.env` ni `biolab.db` (están en `.gitignore`).

## 4. Versiones (SemVer)
Las versiones se marcan con etiquetas `vMAYOR.MENOR.PARCHE`:
- **PARCHE** (v0.1.1): corrección de errores.
- **MENOR** (v0.2.0): funcionalidad nueva que no rompe lo existente.
- **MAYOR** (v1.0.0): cambio incompatible. La `v1.0.0` será la primera versión
  que la licenciada use en el laboratorio con todo el MVP (incluye resultados y PDF).

```bash
git switch main && git pull
git tag -a v0.1.0 -m "Primer release del MVP"
git push origin v0.1.0
```

Los cambios de cada versión se anotan en `CHANGELOG.md`.
