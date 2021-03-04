from app import db
from sqlalchemy_serializer import SerializerMixin

class Room(db.Model, SerializerMixin):
  __tablename__ = 'room'

  id = db.Column(db.Integer, primary_key=True)
  amount = db.Column(db.Float(), default=25000)
  players = db.relationship('Player', backref='room')

  def __repr__(self):
    return '<Room %r>' % self.id



class Player(db.Model, SerializerMixin):
  __tablename__ = 'player'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), nullable=False)
  room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
  amount = db.Column(db.Float(), default=0)
  history = db.relationship('History', backref='player')
 
  def __repr__(self):
    return '<Player %r>' % self.name



class History(db.Model, SerializerMixin):
  __tablename__ = 'history'

  id = db.Column(db.Integer, primary_key=True)
  history = db.Column(db.Text)
  player_id = db.Column(db.Integer, db.ForeignKey('player.id'))


  def __repr__(self):
    return '<History %r>' % self.history