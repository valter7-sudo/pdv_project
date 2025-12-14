# backend/sales.py
db.session.commit()




def current_user():
identity = get_jwt_identity()
if not identity:
return None
return User.query.filter_by(username=identity).first()




@sales_bp.route('/', methods=['POST'])
@jwt_required()
def create_sale():
user = current_user()
if user.role not in ('admin', 'operator', 'buyer'):
return jsonify({'msg': 'Permissão negada'}), 403


data = request.json or {}
items = data.get('items', [])
if not items:
return jsonify({'msg': 'items obrigatórios'}), 400


sale = Sale(created_by=user.id if user else None, total=0.0)
db.session.add(sale)
total = 0.0


for it in items:
code = it.get('code')
qty = int(it.get('quantity', 0))
product = Product.query.filter_by(code=code).first()
if not product:
db.session.rollback()
return jsonify({'msg': f'Produto com código {code} não encontrado'}), 400
if product.quantity < qty:
db.session.rollback()
return jsonify({'msg': f'Estoque insuficiente para {product.name} (tem {product.quantity})'}), 400


subtotal = product.price * qty
si = SaleItem(sale_id=sale.id, product_id=product.id, quantity=qty, price=product.price, subtotal=subtotal)
db.session.add(si)
product.quantity -= qty
total += subtotal


sale.total = total
db.session.commit()
audit(user.id if user else None, 'create_sale', f'sale_id={sale.id} total={total}')
return jsonify({'msg': 'Venda registrada', 'sale_id': sale.id, 'total': total})




@sales_bp.route('/report/stock', methods=['GET'])
@jwt_required()
def stock_report():
threshold = int(request.args.get('threshold', 10))
products = Product.query.order_by(Product.quantity.asc()).all()
low = [{'code': p.code, 'name': p.name, 'qty': p.quantity} for p in products if p.quantity <= threshold]
return jsonify({'low_stock': low, 'all_count': len(products)})