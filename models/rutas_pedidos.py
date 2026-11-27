from flask import Blueprint, render_template, request, jsonify
from models.pedidos import Pedido
from datos_prueba import (
    obtener_formatos,
    obtener_sabores,
    obtener_toppings,
    guardar_pedido,
)

pedido_bp = Blueprint("pedido", __name__)

@pedido_bp.route("/pedido", methods=["GET"])
def vista_pedido():
    return render_template(
        "pedido.html",
        formatos=obtener_formatos(solo_activos=True),
        sabores=obtener_sabores(solo_activos=True),
        toppings=obtener_toppings(solo_activos=True),
    )

@pedido_bp.route("/pedidos", methods=["POST"])
def crear_pedido():
    data = request.get_json(silent=True) or {}
    items_raw = data.get("items", [])

    if not items_raw:
        return jsonify({"ok": False, "error": "El pedido debe tener al menos un ítem."}), 400

    formatos_map = {f["_id"]: f for f in obtener_formatos(solo_activos=True)}
    sabores_map = {s["_id"]: s for s in obtener_sabores(solo_activos=True)}
    toppings_map = {t["_id"]: t for t in obtener_toppings(solo_activos=True)}

    items_validados = []
    total_pedido = 0.0

    for idx, item in enumerate(items_raw, start=1):
        formato_id = item.get("formato_id")
        sabores_ids = item.get("sabores_ids", [])
        toppings_ids = item.get("toppings_ids", [])

        if not formato_id or formato_id not in formatos_map:
            return jsonify({"ok": False, "error": f"Ítem {idx}: formato inválido o inactivo."}), 400

        formato = formatos_map[formato_id]

        if not sabores_ids:
            return jsonify({"ok": False, "error": f"Ítem {idx}: debe elegir al menos un sabor."}), 400

        if len(sabores_ids) > formato["max_sabores"]:
            return jsonify({
                "ok": False,
                "error": f"Ítem {idx}: máximo {formato['max_sabores']} sabores para {formato['nombre']}."
            }), 400

        sabores_nombres = []
        for sid in sabores_ids:
            if sid not in sabores_map:
                return jsonify({"ok": False, "error": f"Ítem {idx}: sabor inválido o inactivo."}), 400
            sabores_nombres.append(sabores_map[sid]["nombre"])

        toppings_nombres = []
        total_toppings = 0.0
        for tid in toppings_ids:
            if tid not in toppings_map:
                return jsonify({"ok": False, "error": f"Ítem {idx}: topping inválido o inactivo."}), 400
            toppings_nombres.append(toppings_map[tid]["nombre"])
            total_toppings += float(toppings_map[tid]["precio"])

        subtotal = round(float(formato["precio"]) + total_toppings, 2)
        total_pedido = round(total_pedido + subtotal, 2)

        items_validados.append({
            "formato": formato["nombre"],
            "precio_base": float(formato["precio"]),
            "sabores": sabores_nombres,
            "toppings": toppings_nombres,
            "subtotal": subtotal,
        })

    nuevo_pedido = Pedido(items=items_validados, total=total_pedido)
    pedido_id = guardar_pedido(nuevo_pedido.toDbConnection())

    return jsonify({
        "ok": True,
        "pedido_id": pedido_id,
        "total": total_pedido,
        "mensaje": "Pedido registrado correctamente.",
    }), 201