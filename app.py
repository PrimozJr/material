from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///materiali.db'
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Material {self.name}>'

@app.route('/')
def index():
    search_name = request.args.get('name', '')
    search_location = request.args.get('location', '')

    # Iskanje po imenu in lokaciji
    if search_name or search_location:
        materials = Material.query.filter(Material.name.ilike(f'%{search_name}%'), 
                                          Material.location.ilike(f'%{search_location}%')).all()
    else:
        materials = Material.query.all()

    return render_template('index.html', materials=materials)

@app.route('/add', methods=['GET', 'POST'])
def add_material():
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        quantity = request.form['quantity']
        
        new_material = Material(name=name, location=location, quantity=quantity)
        
        try:
            db.session.add(new_material)
            db.session.commit()
            flash('Material uspešno dodan!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('Napaka pri dodajanju materiala.', 'error')
            print(e)
            return redirect(url_for('add_material'))

    return render_template('add_material.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_material(id):
    material = Material.query.get_or_404(id)

    if request.method == 'POST':
        material.name = request.form['name']
        material.location = request.form['location']
        material.quantity = request.form['quantity']
        
        try:
            db.session.commit()
            flash('Material uspešno urejen!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('Napaka pri urejanju materiala.', 'error')
            print(e)
            return redirect(url_for('edit_material', id=id))

    return render_template('edit_material.html', material=material)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_material(id):
    material = Material.query.get_or_404(id)
    try:
        db.session.delete(material)
        db.session.commit()
        flash('Material uspešno izbrisan!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Napaka pri brisanju materiala.', 'error')
        print(e)
    return redirect(url_for('index'))

@app.route('/export')
def export_to_excel():
    materials = Material.query.all()
    materials_list = [{'ID': m.id, 'Name': m.name, 'Location': m.location, 'Quantity': m.quantity} for m in materials]

    # Pretvori v DataFrame
    df = pd.DataFrame(materials_list)

    # Shrani kot Excel datoteko
    df.to_excel('materials.xlsx', index=False)

    flash('Materiali so bili izvoženi v Excel datoteko!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ustvari tabelo ob zagonu aplikacije
    app.run(debug=True)
