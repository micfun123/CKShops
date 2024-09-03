from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///minecraft.db'
db = SQLAlchemy(app)

class Shop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    owner = db.Column(db.String(80), nullable=False)
    coordinates = db.Column(db.String(80), nullable=False)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.String(80), nullable=False)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    shop = db.relationship('Shop', backref=db.backref('items', lazy=True))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_shop', methods=['GET', 'POST'])
def add_shop():
    if request.method == 'POST':
        data = request.form
        new_shop = Shop(name=data['name'], owner=data['username'], coordinates=data['coordinates'])
        db.session.add(new_shop)
        db.session.commit()
        return redirect(url_for('add_item'))
    return render_template('add_shop.html')

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        data = request.form
        shop_id = int(data['shop_id'])
        if Shop.query.filter_by(id=shop_id).first() is None:
            return jsonify({'message': 'Shop does not exist!'}), 404
        new_item = Item(name=data['item_name'], price=data['price'], shop_id=shop_id)
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('add_item'))
    shops = Shop.query.all()
    return render_template('add_item.html', shops=shops)

@app.route('/search', methods=['GET'])
def search_items():
    if request.args.get('item_name'):
        item_name = request.args.get('item_name')
        items = Item.query.filter(Item.name.ilike(f'%{item_name}%')).all()
        return render_template('search_results.html', items=items)
    return render_template('search.html')

@app.route('/shop_catalogue', methods=['GET'])
def shop_catalogue():
    shops = Shop.query.all()
    return render_template('shop_catalogue.html', shops=shops)


@app.route('/manage_shop/<int:shop_id>', methods=['GET', 'POST'])
def manage_shop(shop_id):
    shop = Shop.query.get_or_404(shop_id)
    if request.method == 'POST':
        # Handle adding an item
        if 'item_name' in request.form:
            new_item = Item(
                name=request.form['item_name'],
                price=request.form['price'],
                shop_id=shop.id
            )
            db.session.add(new_item)
            db.session.commit()
            return redirect(url_for('manage_shop', shop_id=shop.id))

        # Handle deleting an item
        if 'delete_item_id' in request.form:
            item_id = int(request.form['delete_item_id'])
            item = Item.query.get_or_404(item_id)
            db.session.delete(item)
            db.session.commit()
            return redirect(url_for('manage_shop', shop_id=shop.id))

        # Handle deleting the shop
        if 'delete_shop' in request.form:
            db.session.delete(shop)
            db.session.commit()
            return redirect(url_for('get_shops'))

    return render_template('manage_shop.html', shop=shop)

@app.route('/shops', methods=['GET'])
def get_shops():
    shops = Shop.query.all()
    return render_template('shops.html', shops=shops)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True,host='0.0.0.0',port=8080)
