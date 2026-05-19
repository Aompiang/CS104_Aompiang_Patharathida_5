import os
import sqlite3
from flask import Flask, g, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'construction-inventory-secret'
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def execute_db(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    return cur.lastrowid


def init_db():
    if os.path.exists(DB_PATH):
        return
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript('''
    CREATE TABLE categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT
    );

    CREATE TABLE suppliers (
        supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        contact_name TEXT,
        phone TEXT,
        email TEXT,
        address TEXT
    );

    CREATE TABLE items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category_id INTEGER NOT NULL,
        supplier_id INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        cost_price REAL NOT NULL,
        stock_quantity INTEGER NOT NULL,
        reorder_level INTEGER NOT NULL,
        FOREIGN KEY(category_id) REFERENCES categories(category_id),
        FOREIGN KEY(supplier_id) REFERENCES suppliers(supplier_id)
    );

    CREATE TABLE purchases (
        purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        supplier_id INTEGER NOT NULL,
        purchase_date TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        unit_cost REAL NOT NULL,
        total_cost REAL NOT NULL,
        FOREIGN KEY(item_id) REFERENCES items(item_id),
        FOREIGN KEY(supplier_id) REFERENCES suppliers(supplier_id)
    );

    CREATE TABLE sales (
        sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        sale_date TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        total_revenue REAL NOT NULL,
        total_cost REAL NOT NULL,
        FOREIGN KEY(item_id) REFERENCES items(item_id)
    );
    ''')

    categories = [
        ('Cement & Mortar', 'Ready-mix cement, mortar and concrete additives.'),
        ('Bricks & Blocks', 'Clay bricks, concrete blocks and masonry units.'),
        ('Structural Steel', 'Steel beams, rebar and reinforcement products.'),
        ('Lumber & Timber', 'Planks, plywood and engineered wood products.'),
        ('Pipes & Plumbing', 'PVC, copper pipes and plumbing accessories.'),
        ('Paint & Coating', 'Interior and exterior paints plus primers.'),
        ('Fasteners', 'Nails, screws, bolts and anchors.'),
        ('Electrical', 'Wiring, conduits, switches and outlets.'),
        ('Insulation', 'Rolls, foam boards and thermal insulation.'),
        ('Safety Equipment', 'Helmets, gloves and protective gear.'),
        ('Hardware', 'Hinges, handles and locks.'),
        ('Adhesives', 'Sealants, adhesives and construction glues.'),
        ('Roofing', 'Shingles, roofing sheets and flashings.')
    ]
    suppliers = [
        ('Summit Supply Co.', 'David Chen', '555-0100', 'david.chen@summitsupply.com', '210 Industrial Road'),
        ('Prime Build Materials', 'Lisa Wong', '555-0111', 'lisa.wong@primebuild.com', '77 Construction Ave'),
        ('Urban Steel Ltd.', 'James Ford', '555-0122', 'james.ford@urbansteel.com', '18 Metal St'),
        ('TimberCraft Distribution', 'Maya Patel', '555-0133', 'maya.patel@timbercraft.com', '300 Wood Lane'),
        ('PipeWorks International', 'Ethan Harris', '555-0144', 'ethan.harris@pipeworks.com', '60 Pipeline Blvd'),
        ('ColorPro Paints', 'Nina Lee', '555-0155', 'nina.lee@colorpro.com', '9 Palette Plaza'),
        ('FastenRight Supplies', 'Omar Yusuf', '555-0166', 'omar.yusuf@fastenright.com', '120 Bolt Street'),
        ('ElectroLine Systems', 'Sofia Grant', '555-0177', 'sofia.grant@electroline.com', '45 Wire Way'),
        ('ThermaShield Insulation', 'Carlos Vega', '555-0188', 'carlos.vega@thermashield.com', '88 Cozy Court'),
        ('SafeGuard Gear', 'Anna Kim', '555-0199', 'anna.kim@safeguard.com', '12 Safety Road'),
        ('Alpha Hardware', 'Trevor White', '555-0200', 'trevor.white@alphahardware.com', '200 Retail Park'),
        ('GlueTech Supplies', 'Emma Brown', '555-0211', 'emma.brown@glutech.com', '33 Bond Ave'),
        ('RoofKing Products', 'Lucas Martin', '555-0222', 'lucas.martin@roofking.com', '5 Ridge Street')
    ]
    items = [
        ('Portland Cement Bag', 1, 1, 9.50, 7.20, 120, 30),
        ('Masonry Brick', 2, 2, 0.55, 0.32, 430, 100),
        ('Steel Rebar 12mm', 3, 3, 15.00, 10.50, 250, 50),
        ('Construction Plywood', 4, 4, 22.00, 14.00, 75, 20),
        ('PVC Drain Pipe 100mm', 5, 5, 4.80, 3.10, 180, 40),
        ('Exterior Latex Paint', 6, 6, 28.00, 18.50, 95, 25),
        ('Galvanized Nails 50mm', 7, 7, 5.20, 3.60, 220, 60),
        ('Electrical Cable 2.5mm', 8, 8, 1.20, 0.75, 310, 80),
        ('Foam Board Insulation', 9, 9, 12.50, 8.00, 100, 30),
        ('Safety Helmet', 10, 10, 18.00, 11.00, 65, 20),
        ('Door Hinge Set', 11, 11, 7.80, 5.20, 145, 35),
        ('Construction Adhesive', 12, 12, 13.00, 8.50, 105, 25),
        ('Roof Shingle Pack', 13, 13, 42.00, 28.00, 56, 15)
    ]
    purchases = [
        (1, 1, '2026-01-04', 40, 7.15, 286.00),
        (2, 2, '2026-01-08', 280, 0.30, 84.00),
        (3, 3, '2026-01-11', 120, 10.20, 1224.00),
        (4, 4, '2026-01-15', 30, 14.00, 420.00),
        (5, 5, '2026-01-20', 90, 3.05, 274.50),
        (6, 6, '2026-01-24', 50, 18.00, 900.00),
        (7, 7, '2026-02-02', 130, 3.55, 461.50),
        (8, 8, '2026-02-07', 150, 0.78, 117.00),
        (9, 9, '2026-02-11', 45, 8.10, 364.50),
        (10, 10, '2026-02-14', 25, 11.20, 280.00),
        (11, 11, '2026-02-18', 65, 5.00, 325.00),
        (12, 12, '2026-02-22', 40, 8.40, 336.00),
        (13, 13, '2026-02-26', 18, 27.50, 495.00)
    ]
    sales = [
        (1, '2026-03-02', 24, 12.50, 300.00, 172.80),
        (2, '2026-03-05', 100, 0.95, 95.00, 32.00),
        (3, '2026-03-09', 75, 18.50, 1387.50, 787.50),
        (4, '2026-03-12', 18, 30.00, 540.00, 252.00),
        (5, '2026-03-16', 45, 6.20, 279.00, 139.50),
        (6, '2026-03-19', 28, 36.00, 1008.00, 518.00),
        (7, '2026-03-23', 90, 6.80, 612.00, 324.00),
        (8, '2026-03-27', 120, 2.15, 258.00, 90.00),
        (9, '2026-03-31', 32, 18.50, 592.00, 256.00),
        (10, '2026-04-03', 15, 25.00, 375.00, 168.00),
        (11, '2026-04-07', 54, 9.25, 499.50, 280.80),
        (12, '2026-04-11', 26, 16.50, 429.00, 221.00),
        (13, '2026-04-15', 12, 48.00, 576.00, 336.00)
    ]
    c.executemany('INSERT INTO categories (name, description) VALUES (?, ?)', categories)
    c.executemany('INSERT INTO suppliers (name, contact_name, phone, email, address) VALUES (?, ?, ?, ?, ?)', suppliers)
    c.executemany('INSERT INTO items (name, category_id, supplier_id, unit_price, cost_price, stock_quantity, reorder_level) VALUES (?, ?, ?, ?, ?, ?, ?)', items)
    c.executemany('INSERT INTO purchases (item_id, supplier_id, purchase_date, quantity, unit_cost, total_cost) VALUES (?, ?, ?, ?, ?, ?)', purchases)
    c.executemany('INSERT INTO sales (item_id, sale_date, quantity, unit_price, total_revenue, total_cost) VALUES (?, ?, ?, ?, ?, ?)', sales)
    conn.commit()
    conn.close()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def index():
    total_sales = query_db('SELECT IFNULL(SUM(total_revenue),0) as total FROM sales', one=True)['total']
    total_purchase = query_db('SELECT IFNULL(SUM(total_cost),0) as total FROM purchases', one=True)['total']
    profit = total_sales - total_purchase
    loss = max(0, total_purchase - total_sales)
    inventory_value = query_db('SELECT IFNULL(SUM(stock_quantity * cost_price),0) as total FROM items', one=True)['total']
    best_sellers = query_db(
        'SELECT items.name as item_name, IFNULL(SUM(sales.quantity),0) as sold_units '
        'FROM items LEFT JOIN sales ON items.item_id = sales.item_id '
        'GROUP BY items.item_id ORDER BY sold_units DESC LIMIT 5'
    )
    low_stock = query_db('SELECT * FROM items WHERE stock_quantity <= reorder_level ORDER BY stock_quantity ASC LIMIT 8')
    item_count = query_db('SELECT COUNT(*) as total FROM items', one=True)['total']
    category_count = query_db('SELECT COUNT(*) as total FROM categories', one=True)['total']
    supplier_count = query_db('SELECT COUNT(*) as total FROM suppliers', one=True)['total']
    return render_template('index.html', total_sales=total_sales, total_purchase=total_purchase,
                           profit=profit, loss=loss, inventory_value=inventory_value,
                           best_sellers=best_sellers, low_stock=low_stock,
                           item_count=item_count, category_count=category_count, supplier_count=supplier_count)


@app.route('/items')
def item_list():
    items = query_db('SELECT items.*, categories.name as category_name, suppliers.name as supplier_name '
                     'FROM items '
                     'JOIN categories ON items.category_id = categories.category_id '
                     'JOIN suppliers ON items.supplier_id = suppliers.supplier_id '
                     'ORDER BY items.item_id')
    return render_template('items.html', items=items)


@app.route('/items/new', methods=['GET', 'POST'])
def item_create():
    categories = query_db('SELECT * FROM categories ORDER BY name')
    suppliers = query_db('SELECT * FROM suppliers ORDER BY name')
    if request.method == 'POST':
        name = request.form['name'].strip()
        category_id = request.form['category_id']
        supplier_id = request.form['supplier_id']
        unit_price = float(request.form['unit_price'] or 0)
        cost_price = float(request.form['cost_price'] or 0)
        stock_quantity = int(request.form['stock_quantity'] or 0)
        reorder_level = int(request.form['reorder_level'] or 0)
        if not name:
            flash('Item name is required.', 'warning')
        else:
            execute_db('INSERT INTO items (name, category_id, supplier_id, unit_price, cost_price, stock_quantity, reorder_level) VALUES (?, ?, ?, ?, ?, ?, ?)',
                       (name, category_id, supplier_id, unit_price, cost_price, stock_quantity, reorder_level))
            flash('New item has been created.', 'success')
            return redirect(url_for('item_list'))
    return render_template('item_form.html', categories=categories, suppliers=suppliers, item=None)


@app.route('/items/edit/<int:item_id>', methods=['GET', 'POST'])
def item_edit(item_id):
    item = query_db('SELECT * FROM items WHERE item_id = ?', (item_id,), one=True)
    if not item:
        flash('Item not found.', 'danger')
        return redirect(url_for('item_list'))
    categories = query_db('SELECT * FROM categories ORDER BY name')
    suppliers = query_db('SELECT * FROM suppliers ORDER BY name')
    if request.method == 'POST':
        name = request.form['name'].strip()
        category_id = request.form['category_id']
        supplier_id = request.form['supplier_id']
        unit_price = float(request.form['unit_price'] or 0)
        cost_price = float(request.form['cost_price'] or 0)
        stock_quantity = int(request.form['stock_quantity'] or 0)
        reorder_level = int(request.form['reorder_level'] or 0)
        if not name:
            flash('Item name is required.', 'warning')
        else:
            execute_db('UPDATE items SET name=?, category_id=?, supplier_id=?, unit_price=?, cost_price=?, stock_quantity=?, reorder_level=? WHERE item_id=?',
                       (name, category_id, supplier_id, unit_price, cost_price, stock_quantity, reorder_level, item_id))
            flash('Item has been updated.', 'success')
            return redirect(url_for('item_list'))
    return render_template('item_form.html', categories=categories, suppliers=suppliers, item=item)


@app.route('/items/delete/<int:item_id>', methods=['POST'])
def item_delete(item_id):
    execute_db('DELETE FROM items WHERE item_id = ?', (item_id,))
    flash('Item has been deleted.', 'success')
    return redirect(url_for('item_list'))


@app.route('/categories')
def category_list():
    categories = query_db('SELECT * FROM categories ORDER BY category_id')
    return render_template('categories.html', categories=categories)


@app.route('/categories/new', methods=['GET', 'POST'])
def category_create():
    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form['description'].strip()
        if not name:
            flash('Category name is required.', 'warning')
        else:
            execute_db('INSERT INTO categories (name, description) VALUES (?, ?)',
                       (name, description))
            flash('Category has been created.', 'success')
            return redirect(url_for('category_list'))
    return render_template('category_form.html', category=None)


@app.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
def category_edit(category_id):
    category = query_db('SELECT * FROM categories WHERE category_id = ?', (category_id,), one=True)
    if not category:
        flash('Category not found.', 'danger')
        return redirect(url_for('category_list'))
    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form['description'].strip()
        if not name:
            flash('Category name is required.', 'warning')
        else:
            execute_db('UPDATE categories SET name=?, description=? WHERE category_id=?',
                       (name, description, category_id))
            flash('Category has been updated.', 'success')
            return redirect(url_for('category_list'))
    return render_template('category_form.html', category=category)


@app.route('/categories/delete/<int:category_id>', methods=['POST'])
def category_delete(category_id):
    execute_db('DELETE FROM categories WHERE category_id = ?', (category_id,))
    flash('Category has been deleted.', 'success')
    return redirect(url_for('category_list'))


@app.route('/suppliers')
def supplier_list():
    suppliers = query_db('SELECT * FROM suppliers ORDER BY supplier_id')
    return render_template('suppliers.html', suppliers=suppliers)


@app.route('/suppliers/new', methods=['GET', 'POST'])
def supplier_create():
    if request.method == 'POST':
        name = request.form['name'].strip()
        contact_name = request.form['contact_name'].strip()
        phone = request.form['phone'].strip()
        email = request.form['email'].strip()
        address = request.form['address'].strip()
        if not name:
            flash('Supplier name is required.', 'warning')
        else:
            execute_db('INSERT INTO suppliers (name, contact_name, phone, email, address) VALUES (?, ?, ?, ?, ?)',
                       (name, contact_name, phone, email, address))
            flash('Supplier has been created.', 'success')
            return redirect(url_for('supplier_list'))
    return render_template('supplier_form.html', supplier=None)


@app.route('/suppliers/edit/<int:supplier_id>', methods=['GET', 'POST'])
def supplier_edit(supplier_id):
    supplier = query_db('SELECT * FROM suppliers WHERE supplier_id = ?', (supplier_id,), one=True)
    if not supplier:
        flash('Supplier not found.', 'danger')
        return redirect(url_for('supplier_list'))
    if request.method == 'POST':
        name = request.form['name'].strip()
        contact_name = request.form['contact_name'].strip()
        phone = request.form['phone'].strip()
        email = request.form['email'].strip()
        address = request.form['address'].strip()
        if not name:
            flash('Supplier name is required.', 'warning')
        else:
            execute_db('UPDATE suppliers SET name=?, contact_name=?, phone=?, email=?, address=? WHERE supplier_id=?',
                       (name, contact_name, phone, email, address, supplier_id))
            flash('Supplier has been updated.', 'success')
            return redirect(url_for('supplier_list'))
    return render_template('supplier_form.html', supplier=supplier)


@app.route('/suppliers/delete/<int:supplier_id>', methods=['POST'])
def supplier_delete(supplier_id):
    execute_db('DELETE FROM suppliers WHERE supplier_id = ?', (supplier_id,))
    flash('Supplier has been deleted.', 'success')
    return redirect(url_for('supplier_list'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
