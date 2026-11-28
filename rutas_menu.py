from collections import OrderedDict

from flask import Blueprint, render_template

from database import dbConnection

menu_bp = Blueprint("menu", __name__)


def _activos(coleccion, orden):
    """Devuelve solo los documentos con activo = True, ordenados."""
    db = dbConnection()
    if db is None:
        return []
    return list(db[coleccion].find({"activo": True}).sort(orden))


def _agrupar_por_categoria(sabores):
    """Agrupa los sabores en un diccionario {categoria: [sabores]}."""
    grupos = OrderedDict()
    for sabor in sabores:
        categoria = sabor.get("categoria") or "Otros"
        grupos.setdefault(categoria, []).append(sabor)
    return grupos


# HU-02: el cliente ve el menu sin entrar al panel de administracion
@menu_bp.route("/menu")
def menu():
    formatos = _activos("formatos", "precio")
    sabores = _activos("sabores", [("categoria", 1), ("nombre", 1)])
    toppings = _activos("toppings", "nombre")

    return render_template(
        "menu.html",
        formatos=formatos,
        sabores_por_categoria=_agrupar_por_categoria(sabores),
        toppings=toppings,
    )
