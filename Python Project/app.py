import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g, session, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key

# Database setup
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('inventory.db')
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

# Home route
@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.execute('SELECT * FROM products')
    products = cursor.fetchall()
    return render_template('home.html', products=products)

# Add product route
@app.route('/add', methods=['POST'])
def add_product():
    name = request.form['name']
    stock = int(request.form['stock'])
    db = get_db()
    db.execute('INSERT INTO products (name, stock) VALUES (?, ?)', (name, stock))
    db.commit()
    return redirect(url_for('home'))

# Sell product route
@app.route('/sell/<int:id>')
def sell_product(id):
    db = get_db()
    cursor = db.execute('SELECT stock FROM products WHERE id = ?', (id,))
    current_stock = cursor.fetchone()[0]
    if current_stock > 0:
        new_stock = current_stock - 1
        db.execute('UPDATE products SET stock = ? WHERE id = ?', (new_stock, id))
        db.commit()
    return redirect(url_for('home'))

# Delete product route
@app.route('/delete/<int:id>')
def delete_product(id):
    db = get_db()
    db.execute('DELETE FROM products WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('home'))

# Logout route
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

# Visualize route
@app.route('/visualize')
def visualize():
    db = get_db()
    cursor = db.execute('SELECT name, stock FROM products')
    data = cursor.fetchall()
    product_names = [item[0] for item in data]
    stock_levels = [item[1] for item in data]

    return render_template('visualize.html', product_names=product_names, stock_levels=stock_levels)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            session['logged_in'] = True
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
