from flask import Flask, request, jsonify
import db 

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "API de Inventario en ejecución"}), 200

# Ruta para obtener todos los productos
@app.route('/producto/<int:producto_id>', methods=['GET'])
def get_producto(producto_id):
    mydb = db.get_connection()
    mycursor = mydb.cursor()
    
    sql = "SELECT p.id, p.nombre, p.precio, c.nombre AS categoria FROM productos p LEFT JOIN categorias c ON p.categoria_id = c.id WHERE p.id = %s"
    val = (producto_id,)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()
    
    mydb.close()
    
    if result:
        producto = {
            "id": result[0],
            "nombre": result[1],
            "precio": float(result[2]),
            "categoria": result[3] if result[3] else "Sin categoría"
        }
        return jsonify(producto), 200
    else:
        return jsonify({"message": "Producto no encontrado"}), 404


# Ruta para obtener el inventario de un producto
@app.route('/inventario/<int:producto_id>', methods=['GET'])
def get_inventario(producto_id):
    mydb = db.get_connection()
    mycursor = mydb.cursor()
    
    sql = "SELECT i.id, p.nombre, i.cantidad, i.fecha_actualizacion FROM inventario i JOIN productos p ON i.producto_id = p.id WHERE i.producto_id = %s"
    val = (producto_id,)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()
    
    mydb.close()
    
    if result:
        inventario = {
            "id": result[0],
            "producto": result[1],
            "cantidad": result[2],
            "fecha_actualizacion": result[3].strftime('%Y-%m-%d %H:%M:%S')
        }
        return jsonify(inventario), 200
    else:
        return jsonify({"message": "Inventario no encontrado"}), 404


# Ruta para crear un producto

@app.route('/producto', methods=['POST'])
def crear_producto():
    mydb = db.get_connection()
    mycursor = mydb.cursor()

    try:
        data = request.get_json()

        nombre = data.get('nombre')
        precio = data.get('precio')
        categoria_nombre = data.get('categoria')

        if not nombre or not precio or not categoria_nombre:
            return jsonify({"error": "Faltan datos"}), 400

        precio = float(precio)  # Convierte a float

        # Busca o crea la categoría
        sql_categoria = "SELECT id FROM categorias WHERE nombre = %s"
        val_categoria = (categoria_nombre,)
        mycursor.execute(sql_categoria, val_categoria)
        result_categoria = mycursor.fetchone()

        if result_categoria:
            categoria_id = result_categoria[0]
        else:
            sql_insert_categoria = "INSERT INTO categorias (nombre) VALUES (%s)"
            val_insert_categoria = (categoria_nombre,)
            mycursor.execute(sql_insert_categoria, val_insert_categoria)
            mydb.commit()
            categoria_id = mycursor.lastrowid

        # Inserta el producto
        sql_producto = "INSERT INTO productos (nombre, precio, categoria_id) VALUES (%s, %s, %s)"
        val_producto = (nombre, precio, categoria_id)
        mycursor.execute(sql_producto, val_producto)
        mydb.commit()

        return jsonify({"message": "Producto creado", "id": mycursor.lastrowid}), 201

    except mysql.connector.Error as err:
        mydb.rollback()
        return jsonify({"error": str(err)}), 500
    except ValueError:  # Captura error si el precio no es un número
        mydb.rollback()
        return jsonify({"error": "Precio inválido"}), 400
    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()

if __name__ == '__main__':
    app.run(debug=True)