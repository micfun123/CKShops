from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///minecraft.db'
db = SQLAlchemy(app)

# Define your database models
class Shop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    owner = db.Column(db.String(80), nullable=False)
    coordinates = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'Shop(name={self.name}, owner={self.owner}, coordinates={self.coordinates})'

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.String(80), nullable=False)  # Changed to String
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    shop = db.relationship('Shop', backref=db.backref('items', lazy=True))

    def __repr__(self):
        return f'Item(name={self.name}, price={self.price}, shop_id={self.shop_id})'


# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_shop', methods=['POST'])
def add_shop():
    data = request.form
    new_shop = Shop(name=data['name'], owner=data['username'], coordinates=data['coordinates'])
    db.session.add(new_shop)
    db.session.commit()
    
    return jsonify({
        'message': 'Shop added successfully!',
        'shop_id': new_shop.id,
        'name': new_shop.name,
        'owner': new_shop.owner,
        'coordinates': new_shop.coordinates
    })

@app.route('/add_item', methods=['POST'])
def add_item():
    data = request.form
    shop_id = int(data['shop_id'])
    if Shop.query.filter_by(id=shop_id).first() is None:
        return jsonify({'message': 'Shop does not exist!'}), 404

    new_item = Item(name=data['item_name'], price=float(data['price']), shop_id=shop_id)
    db.session.add(new_item)
    db.session.commit()
    return jsonify({'message': 'Item added successfully!'})

@app.route('/search', methods=['GET'])
def search_items():
    item_name = request.args.get('item_name')
    items = Item.query.filter(Item.name.ilike(f'%{item_name}%')).all()
    results = []
    for item in items:
        shop = Shop.query.get(item.shop_id)
        results.append({
            'item_name': item.name,
            'price': item.price,
            'shop_name': shop.name,
            'coordinates': shop.coordinates
        })
    return jsonify(results)

@app.route('/shops', methods=['GET'])
def get_shops():
    shops = Shop.query.all()
    shop_list = []
    for shop in shops:
        items = Item.query.filter_by(shop_id=shop.id).all()
        item_list = [{'item_name': item.name, 'price': item.price} for item in items]
        shop_list.append({
            'shop_id': shop.id,
            'name': shop.name,
            'owner': shop.owner,
            'coordinates': shop.coordinates,
            'items': item_list
        })
    return jsonify(shop_list)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True,host='0.0.0.0',port=8080)
