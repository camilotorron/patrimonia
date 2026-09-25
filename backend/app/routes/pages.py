"""Rutas que sirven el frontend (templates Jinja2).

El frontend está separado en ``/frontend`` y se sirve como archivos estáticos.
Estas rutas solo manejan las páginas HTML principales.
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.config import settings

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Página principal — redirige al dashboard."""
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/frontend/dashboard.html")


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Redirige al dashboard del frontend."""
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/frontend/dashboard.html")
