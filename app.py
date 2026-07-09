import os
import uuid
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from supabase import create_client, Client
from flask_caching import Cache
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300

cache = Cache(app)

# Supabase connection
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# Admin Login Decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/menu', methods=['GET'])
@cache.cached(timeout=60)
def get_menu():
    try:
        response = supabase.table('dishes').select('*, categories(id, name)').execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/categories', methods=['GET'])
@cache.cached(timeout=3600)
def get_categories():
    response = supabase.table('categories').select('*').execute()
    return jsonify(response.data)

# --- ADMIN LOGIN ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == "maggieshotel2025":
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))
        return "Invalid Password", 401
    return render_template('admin_login.html')

@app.route('/admin/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
@admin_required
def admin_panel():
    return render_template('admin.html')

# --- ADMIN CRUD (ADD/EDIT/DELETE) ---
@app.route('/api/admin/add', methods=['POST'])
@admin_required
def add_dish():
    data = request.form
    image_url = None
    if 'image' in request.files and request.files['image'].filename:
        file = request.files['image']
        file_ext = file.filename.split('.')[-1]
        filename = f"{uuid.uuid4()}.{file_ext}"
        supabase.storage.from_('menu-images').upload(filename, file.read())
        image_url = supabase.storage.from_('menu-images').get_public_url(filename)
    
    supabase.table('dishes').insert({
        'name': data.get('name'),
        'description': data.get('description'),
        'price': int(data.get('price')),
        'category_id': int(data.get('category_id')),
        'image_url': image_url
    }).execute()
    
    cache.clear()
    return jsonify({"success": True})

@app.route('/api/admin/update/<int:dish_id>', methods=['POST'])
@admin_required
def update_dish(dish_id):
    data = request.form
    image_url = data.get('current_image')
    
    if 'image' in request.files and request.files['image'].filename:
        file = request.files['image']
        file_ext = file.filename.split('.')[-1]
        filename = f"{uuid.uuid4()}.{file_ext}"
        supabase.storage.from_('menu-images').upload(filename, file.read())
        image_url = supabase.storage.from_('menu-images').get_public_url(filename)
    
    supabase.table('dishes').update({
        'name': data.get('name'),
        'description': data.get('description'),
        'price': int(data.get('price')),
        'category_id': int(data.get('category_id')),
        'image_url': image_url
    }).eq('id', dish_id).execute()
    
    cache.clear()
    return jsonify({"success": True})

@app.route('/api/admin/delete/<int:dish_id>', methods=['DELETE'])
@admin_required
def delete_dish(dish_id):
    supabase.table('dishes').delete().eq('id', dish_id).execute()
    cache.clear()
    return jsonify({"success": True})

@app.route('/api/admin/categories/add', methods=['POST'])
@admin_required
def add_category():
    name = request.json.get('name')
    supabase.table('categories').insert({'name': name}).execute()
    cache.clear()
    return jsonify({"success": True})

@app.route('/api/admin/categories/delete/<int:cat_id>', methods=['DELETE'])
@admin_required
def delete_category(cat_id):
    supabase.table('categories').delete().eq('id', cat_id).execute()
    cache.clear()
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)