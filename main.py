from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, URL
from flask_bootstrap import Bootstrap
from dotenv import load_dotenv
import os
import datetime

CURRENT_YEAR = datetime.datetime.now().year

load_dotenv("./.env")

app = Flask(__name__)
Bootstrap(app)
# create/connect to database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", 'sqlite:///cafes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
db = SQLAlchemy(app)


# Cafe table configuration
class Cafe(db.Model):
    __tablename__ = "cafe"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


#  create a new table
db.create_all()


# creating a form with FlaskForm from Flask-WTF
class CafeForm(FlaskForm):
    name = StringField(label="Cafe Name", validators=[DataRequired()])
    map_url = StringField(label="Google Maps Location Link", validators=[DataRequired(), URL()])
    img_url = StringField(label="Image Link", validators=[DataRequired(), URL()])
    location = StringField(label="Location in London", validators=[DataRequired()])
    has_sockets = BooleanField(label="Cafe has Electrical Sockets?")
    has_toilet = BooleanField(label="Cafe has Toilets?")
    has_wifi = BooleanField(label="Cafe has WiFi?")
    can_take_calls = BooleanField(label="Cafe can take calls?")
    seats = SelectField(label="Approximate Number of Seats? (eg. 20-30, 50+, etc.)",
                        choices=['0-10', '10-20', '20-30', '30-40', '40-50', '50+'],
                        validators=[DataRequired()])
    coffee_price = StringField(label="Price of a Coffee Cup (eg. £2.65)", default="£0.00", validators=[DataRequired()])
    submit = SubmitField(label="Submit")


@app.route('/')
def home():
    cafes = Cafe.query.all()
    locations = []
    for cafe in cafes:
        if cafe.location not in locations:
            locations.append(cafe.location)
    # print(locations)
    locations = sorted(locations, key=str.lower)

    return render_template("index.html", all_cafes=cafes, all_locations=locations, year=CURRENT_YEAR)


@app.route('/add-cafe', methods=["GET", "POST"])
def add_cafe():
    add_cafe_form = CafeForm()
    if add_cafe_form.validate_on_submit():
        new_cafe = Cafe(
            name=add_cafe_form.name.data,
            map_url=add_cafe_form.map_url.data,
            img_url=add_cafe_form.img_url.data,
            location=add_cafe_form.location.data,
            has_sockets=add_cafe_form.has_sockets.data,
            has_toilet=add_cafe_form.has_toilet.data,
            has_wifi=add_cafe_form.has_wifi.data,
            can_take_calls=add_cafe_form.can_take_calls.data,
            seats=add_cafe_form.seats.data,
            coffee_price=add_cafe_form.coffee_price.data,
        )
        print(new_cafe)
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add-cafe.html", form=add_cafe_form, year=CURRENT_YEAR)


@app.route('/edit-cafe/<int:cafe_id>', methods=["GET", "POST"])
def edit_cafe(cafe_id):
    cafe_to_edit = Cafe.query.get(cafe_id)
    edit_cafe_form = CafeForm(
        name=cafe_to_edit.name,
        map_url=cafe_to_edit.map_url,
        img_url=cafe_to_edit.img_url,
        location=cafe_to_edit.location,
        has_sockets=cafe_to_edit.has_sockets,
        has_toilet=cafe_to_edit.has_toilet,
        has_wifi=cafe_to_edit.has_wifi,
        can_take_calls=cafe_to_edit.can_take_calls,
        seats=cafe_to_edit.seats,
        coffee_price=cafe_to_edit.coffee_price,
    )
    if edit_cafe_form.validate_on_submit():
        cafe_to_edit.name = edit_cafe_form.name.data
        cafe_to_edit.map_url = edit_cafe_form.map_url.data
        cafe_to_edit.img_url = edit_cafe_form.img_url.data
        cafe_to_edit.location = edit_cafe_form.location.data
        cafe_to_edit.has_sockets = edit_cafe_form.has_sockets.data
        cafe_to_edit.has_toilet = edit_cafe_form.has_toilet.data
        cafe_to_edit.has_wifi = edit_cafe_form.has_wifi.data
        cafe_to_edit.can_take_calls = edit_cafe_form.can_take_calls.data
        cafe_to_edit.seats = edit_cafe_form.seats.data
        cafe_to_edit.coffee_price = edit_cafe_form.coffee_price.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit-cafe.html", form=edit_cafe_form, year=CURRENT_YEAR)


@app.route('/delete/<int:cafe_id>')
def delete_cafe(cafe_id):
    print(cafe_id)
    cafe_to_delete = Cafe.query.get(cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
