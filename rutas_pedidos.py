from flask import Blueprint, render_template, request, redirect, url_for, session
from datos_prueba import obtener_formatos, obtener_sabores, obtener_toppings

pedido_bp = Blueprint("pedido", __name__)


def _calcular_total(items):
    return round(sum(float(item["subtotal"]) for item in items), 2)


@pedido_bp.route("/pedido", methods=["GET"])
def vista_pedido():
    formatos = obtener_formatos(solo_activos=True)
    sabores = obtener_sabores(solo_activos=True)
    toppings = obtener_toppings(solo_activos=True)

    # Si cambias de formato desde el selector, se guarda el formato elegido en sesión
    formato_id_seleccionado = request.args.get("formato_id") or session.get("formato_borrador_id")
    if formato_id_seleccionado:
        session["formato_borrador_id"] = formato_id_seleccionado

    formato_actual = next(
        (f for f in formatos if str(f.get("_id")) == str(formato_id_seleccionado)),
        None
    )

    items = session.get("items_pedido", [])
    total = _calcular_total(items)
    error = session.pop("error_pedido", None)

    return render_template(
        "pedido.html",
        formatos=formatos,
        sabores=sabores,
        toppings=toppings,
        formato_actual=formato_actual,
        items=items,
        total=total,
        error=error
    )


@pedido_bp.route("/pedido/seleccionar-formato", methods=["POST"])
def seleccionar_formato():
    formato_id = request.form.get("formato_id", "").strip()
    session["formato_borrador_id"] = formato_id
    return redirect(url_for("pedido.vista_pedido"))


@pedido_bp.route("/pedido/agregar", methods=["POST"])
def agregar_item():
    formatos = obtener_formatos(solo_activos=True)
    sabores_activos = obtener_sabores(solo_activos=True)
    toppings_activos = obtener_toppings(solo_activos=True)

    formato_id = request.form.get("formato_id", "").strip()
    sabores_ids = request.form.getlist("sabores_ids")
    toppings_ids = request.form.getlist("toppings_ids")

    formato = next((f for f in formatos if str(f.get("_id")) == formato_id), None)
    if not formato:
        session["error_pedido"] = "Debes seleccionar un formato activo."
        return redirect(url_for("pedido.vista_pedido"))

    max_sabores = int(formato.get("max_sabores", 1))
    if len(sabores_ids) == 0:
        session["error_pedido"] = "Debes elegir al menos un sabor."
        return redirect(url_for("pedido.vista_pedido"))

    if len(sabores_ids) > max_sabores:
        session["error_pedido"] = f"El formato {formato['nombre']} permite máximo {max_sabores} sabor(es)."
        return redirect(url_for("pedido.vista_pedido"))

    sabores_map = {str(s.get("_id")): s for s in sabores_activos}
    toppings_map = {str(t.get("_id")): t for t in toppings_activos}

    sabores_elegidos = [sabores_map[sid] for sid in sabores_ids if sid in sabores_map]
    toppings_elegidos = [toppings_map[tid] for tid in toppings_ids if tid in toppings_map]

    if len(sabores_elegidos) != len(sabores_ids):
        session["error_pedido"] = "Uno o más sabores seleccionados no están activos."
        return redirect(url_for("pedido.vista_pedido"))

    precio_base = float(formato.get("precio", 0))
    precio_toppings = sum(float(t.get("precio", 0)) for t in toppings_elegidos)
    subtotal = round(precio_base + precio_toppings, 2)

    nuevo_item = {
        "formato_id": str(formato.get("_id")),
        "formato_nombre": formato.get("nombre"),
        "sabores_nombres": [s.get("nombre") for s in sabores_elegidos],
        "toppings_nombres": [t.get("nombre") for t in toppings_elegidos],
        "subtotal": subtotal
    }

    items = session.get("items_pedido", [])
    items.append(nuevo_item)
    session["items_pedido"] = items
    session.pop("formato_borrador_id", None)

    return redirect(url_for("pedido.vista_pedido"))


@pedido_bp.route("/pedido/quitar/<int:indice>", methods=["POST"])
def quitar_item(indice):
    items = session.get("items_pedido", [])
    if 0 <= indice < len(items):
        items.pop(indice)
        session["items_pedido"] = items
    return redirect(url_for("pedido.vista_pedido"))