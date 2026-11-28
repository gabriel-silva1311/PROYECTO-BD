from flask import Flask, render_template
#from rutas_pedido import pedido_bp
from rutas_menu import menu_bp

app = Flask(__name__)
#app.register_blueprint(pedido_bp)
app.register_blueprint(menu_bp)


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
