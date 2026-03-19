from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'collins123'  # your password
app.config['MYSQL_DB'] = 'drinks_db'

mysql = MySQL(app)

# ---------------- CRUD API ---------------- #

@app.route('/drinks', methods=['GET'])
def get_drinks_api():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM drinks")
    rows = cur.fetchall()
    drinks = [{"id": row[0], "name": row[1], "price": row[2], "description": row[3]} for row in rows]
    return jsonify(drinks)

@app.route('/drinks/<int:id>', methods=['GET'])
def get_drink_api(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM drinks WHERE id=%s", (id,))
    row = cur.fetchone()
    if row:
        drink = {"id": row[0], "name": row[1], "price": row[2], "description": row[3]}
        return jsonify(drink)
    return jsonify({"message": "Drink not found"}), 404

@app.route('/drinks', methods=['POST'])
def add_drink_api():
    data = request.get_json()
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO drinks(name, price, description) VALUES(%s,%s,%s)",
                (data['name'], data['price'], data['description']))
    mysql.connection.commit()
    return jsonify({"message": "Drink added successfully"})

@app.route('/drinks/<int:id>', methods=['PUT'])
def update_drink_api(id):
    data = request.get_json()
    cur = mysql.connection.cursor()
    cur.execute("UPDATE drinks SET name=%s, price=%s, description=%s WHERE id=%s",
                (data['name'], data['price'], data['description'], id))
    mysql.connection.commit()
    return jsonify({"message": "Drink updated successfully"})

@app.route('/drinks/<int:id>', methods=['DELETE'])
def delete_drink_api(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM drinks WHERE id=%s", (id,))
    mysql.connection.commit()
    return jsonify({"message": "Drink deleted successfully"})

# ---------------- Web Page ---------------- #

@app.route('/')
def home():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM drinks")
    rows = cur.fetchall()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Drinks Menu</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f2f2f2;
                padding: 20px;
            }
            h1 {
                text-align: center;
                color: #007bff;
            }
            table {
                width: 80%;
                margin: auto;
                border-collapse: collapse;
                background: white;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            th, td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #007bff;
                color: white;
            }
            tr:hover {background-color: #f1f1f1;}
            a.button {
                padding: 6px 12px;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                margin-right: 5px;
                font-size: 14px;
            }
            a.edit { background-color: #28a745; }
            a.delete { background-color: #dc3545; }
            a.add { background-color: #007bff; margin-bottom: 10px; display:inline-block;}
            form { display:inline; }
        </style>
    </head>
    <body>
        <h1>Drinks Menu</h1>
        <a class="button add" href="/add">Add New Drink</a>
        <table>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Price (UGX)</th>
                <th>Description</th>
                <th>Actions</th>
            </tr>
    """
    
    for row in rows:
        html += f"""
            <tr>
                <td>{row[0]}</td>
                <td>{row[1]}</td>
                <td>{row[2]}</td>
                <td>{row[3]}</td>
                <td>
                    <a class='button edit' href='/edit/{row[0]}'>Edit</a>
                    <a class='button delete' href='/delete/{row[0]}'>Delete</a>
                </td>
            </tr>
        """
    
    html += """
        </table>
    </body>
    </html>
    """
    return render_template_string(html)

# ---------------- Web Forms ---------------- #

@app.route('/add', methods=['GET', 'POST'])
def add_drink_form():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO drinks(name, price, description) VALUES(%s,%s,%s)", (name, price, description))
        mysql.connection.commit()
        return redirect('/')
    return render_template_string("""
        <h2 style='text-align:center'>Add New Drink</h2>
        <form method='POST' style='text-align:center; margin-top:20px'>
            Name: <input type='text' name='name' required><br><br>
            Price: <input type='number' name='price' required><br><br>
            Description:<br>
            <textarea name='description' rows='4' cols='30'></textarea><br><br>
            <input type='submit' value='Add Drink'>
        </form>
        <p style='text-align:center'><a href='/'>Back to Menu</a></p>
    """)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_drink_form(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM drinks WHERE id=%s", (id,))
    drink = cur.fetchone()
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        cur.execute("UPDATE drinks SET name=%s, price=%s, description=%s WHERE id=%s",
                    (name, price, description, id))
        mysql.connection.commit()
        return redirect('/')
    return render_template_string(f"""
        <h2 style='text-align:center'>Edit Drink</h2>
        <form method='POST' style='text-align:center; margin-top:20px'>
            Name: <input type='text' name='name' value='{drink[1]}' required><br><br>
            Price: <input type='number' name='price' value='{drink[2]}' required><br><br>
            Description:<br>
            <textarea name='description' rows='4' cols='30'>{drink[3]}</textarea><br><br>
            <input type='submit' value='Update Drink'>
        </form>
        <p style='text-align:center'><a href='/'>Back to Menu</a></p>
    """)

@app.route('/delete/<int:id>')
def delete_drink_form(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM drinks WHERE id=%s", (id,))
    mysql.connection.commit()
    return redirect('/')

# ---------------- Run App ---------------- #
if __name__ == '__main__':
    app.run(debug=True)