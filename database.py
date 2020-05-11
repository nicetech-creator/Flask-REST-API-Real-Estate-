from flask_sqlalchemy import SQLAlchemy, event
from flask_login import UserMixin
from flask_marshmallow import Marshmallow
from marshmallow import fields, pre_load, post_load
from config import db, ma
from secrets import token_hex

"""
@login_manager.user_loader
def get_user(ident):
    return User.query.filter_by(id=ident).first()
"""

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    surname = db.Column(db.Text)
    name = db.Column(db.Text)
    bday = db.Column(db.DateTime)  
    token = db.Column(db.Text)  
    estate = db.relationship('Estate', backref="owner_estate", cascade="all, delete-orphan", lazy='dynamic')


class Estate(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    id_owner=db.Column(db.Integer, db.ForeignKey("user.id"))
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    re_type = db.Column(db.Text)
    city = db.Column(db.Text)
    rooms = db.relationship('Room', back_populates="estate_parent", cascade="all, delete-orphan", lazy='dynamic')


class Room(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    id_estate=db.Column(db.Integer, db.ForeignKey("estate.id"))
    estate_parent = db.relationship("Estate", back_populates="rooms", cascade = 'all, delete-orphan',single_parent = True)

class RoomSchema(ma.ModelSchema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required = True)
    description = fields.Str()
    id_estate = fields.Int()
    class Meta:
        model = Room 
        sqla_session = db.session  

class EstateSchema(ma.ModelSchema):
    id = fields.Int(dump_only=True)
    description = fields.Str()
    name = fields.Str(required = True)
    re_type = fields.Str(required = True)
    city = fields.Str(required = True)
    rooms = fields.Nested(RoomSchema, many=True)
    id_owner = fields.Int()

    @pre_load
    def toUp(self, in_data, **kwargs):
        #when loading data from the post request, city names are converted to uppercase
        #we might not have a city field
        if in_data.get('city'):
            in_data["city"] = in_data["city"].upper()
        return in_data
    class Meta:
        model = Estate
        sqla_session = db.session
        
class UserSchema(ma.ModelSchema):
    id = fields.Int(dump_only=True)
    surname = fields.Str()
    name = fields.Str()
    bday = fields.DateTime('%d-%m-%Y')
    token = fields.Str()
    estate = fields.Nested(EstateSchema, many=True, only=["name"])
    @pre_load
    def generateToken(self, in_data, **kwargs):
        in_data["token"] = token_hex(40)
        return in_data
    class Meta:
        model = User
        sqla_session = db.session
       