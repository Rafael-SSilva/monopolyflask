import json
from datetime import datetime
from uuid import uuid4
from flask import Blueprint, jsonify, request

# monopoly_app = Blueprint(name='monopoly_app', __name__, template_folder='templates')
from app import db, app, route
from app.models.models import Player, History, Room

@app.route(route + '/rooms', methods=['GET', 'POST'])
@app.route(route + '/rooms/<string:id>', methods=['GET'])
def rooms_api(id=None):

  
  if request.method == "POST":
    
    initial_amount = float(25000)

    if request.data is not None:
      json_data = json.loads(request.data)
      if json_data['amount'] and type(json_data['amount']) == float or type(json_data['amount']) == int:
        initial_amount = float(json_data['amount'])
    
    # if type(json_data['player_name']) != str:
    #   return jsonify({'message': 'player_name must be provided'})
      
    new_room = Room(amount=initial_amount)
    db.session.add(new_room)
    db.session.commit()

    room = {'id': new_room.id , 'amount': new_room.amount, 'players': [] }
    print('sala criada')
    print(room)
    return jsonify(room), 201

  else: #GET
    
    if id is not None:
      try:
        room = Room.query.filter_by(id=id).first()
      except:
        room = None
      
      if room is not None:
        players = [
                    {'id': player.id, 'name': player.name,'amount': player.amount,
                    "room": room.id,
                    'history':[{'id':hist.id, 'history': hist.history} for hist in player.history]}
                    for player in room.players
                  ]
        room_json = {'id': room.id, 'amount':room.amount, 'players':players}

        return jsonify(room_json), 200

    rooms_db = Room.query.all()
    rooms_json = [{
      'id':room.id,
      'amount':room.amount,
      'players':[{'id': player.id, 'name': player.name,'amount':player.amount,
                  "room": room.id,
                   'history':[{'id':hist.id, 'history': hist.history} for hist in player.history]} 
                   for player in room.players],
                } for room in rooms_db]
    
    return jsonify(rooms_json), 200


@app.route(route + '/players/<string:id>', methods=['GET'])
@app.route(route + '/players', methods=['POST','GET'])
def player(id=None):

  if request.method == "POST":

    if request.data is None:
      return jsonify({'status': 1, "message": "Empty body"}), 400

    json_data = json.loads(request.data)
    print('recebido')
    if json_data['room_id'] is None or json_data['name'] is None:
      return jsonify({'status': 1, "message": "Player name and room_id must be provided."}), 400
        
    try:
      room = Room.query.filter_by(id=json_data['room_id'] ).first()
    except:
      room = None

    if room is None:
      return jsonify({'status': 1, "message": "Room not found"}), 404

    #Search player by name and room id.
    new_player = Player.query.filter_by(name=json_data['name'], room_id=room.id).first()

    if new_player is None:
      new_player = Player(name=json_data['name'], room=room, amount=room.amount)
      db.session.add(new_player)
      db.session.commit()
    else:
      print('')
      print('Player encontrado')
      print(new_player.name)

    player_json = [{
      'id': new_player.id,
      'name': new_player.name,
      'amount': new_player.amount,
      'room': new_player.room_id,
      'history': [{'id':hist.id, 'history': hist.history} for hist in new_player.history]
    }]

    return jsonify(player_json), 201

  else: #GET
    
    players_all = Player.query.all()

    if id is not None:
      try:
        players = Player.query.filter_by(id=id)
      except:
        players = None

      if players is not None:
        players_all = players

    player_json = [{
      'id': player.id,
      'name': player.name,
      'amount': player.amount,
      'room': player.room_id,
      'history': [{'id':hist.id, 'history': hist.history} for hist in player.history]
    } for player in players_all]

    return jsonify(player_json), 200


@app.route(route + '/players/payment', methods=['POST'])
def player_amount_pay():

    if request.data is None:
      return jsonify({'status': 1,'message':'payload not provided'}), 400

    json_data = json.loads(request.data)

    if type(json_data['amount']) != int and type(json_data['amount']) != float:
      print({'status': 1,'message':'amount not provided'})
      return jsonify({'status': 1,'message':'amount not provided'}), 400
      
    if type(json_data['payer']) is None:
      print({'status': 1,'message':'payer_id not provided'})
      return jsonify({'status': 1,'message':'payer_id not provided'}), 400
    
    if type(json_data['receiver']) is None:
      print({'status': 1,'message':'receiver_id not provided'})
      return jsonify({'status': 1,'message':'receiver_id not provided'}), 400
    
    id_payer = json_data['payer']
    id_receiver = json_data['receiver']

    players_id = [ id_payer, id_receiver]

    payer = Player.query.filter_by(id=id_payer).first()
    receiver = Player.query.filter_by(id=id_receiver).first()
    
    if payer is None:
      return jsonify({'status': 1,'message':'payer not found'}), 404

    if id_receiver is None:
      return jsonify({'status': 1,'message':'receiver not found'}), 404

    amount = json_data['amount']

    amount = payer.amount if amount > payer.amount else amount

    payer.amount = payer.amount - amount #Debit
    receiver.amount = receiver.amount + amount #Credit

    db.session.commit()

    time = datetime.now().strftime("%H:%M:%S")
    hist_payer = History(history=f"-{amount} --> {receiver.name} : {time}", player=payer)
    hist_receiver = History(history=f"+ Recebeu {amount} de {payer.name} : {time}", player=receiver)

    db.session.add(hist_payer)
    db.session.add(hist_receiver)
    db.session.commit()

    player_list = [ {'id': payer.id, 'name': payer.name, 'room': payer.room.id, 'amount': payer.amount,
                    'history': [{'id':hist.id, 'history': hist.history} for hist in payer.history]} 
                  , {'id': receiver.id, 'name': receiver.name, 'room': receiver.room.id, 'amount': receiver.amount,
                   'history': [{'id':hist.id, 'history': hist.history} for hist in receiver.history]}]

    return jsonify(player_list)


@app.route(route + '/players/amount', methods=['POST'])
def player_amount():

    allowed_transactions = ['addition', 'deduction']
    players_list =[]

    if request.data is None:
      return jsonify({'status': 1,'message':'payload not provided'}), 400

    json_data = json.loads(request.data)

    if type(json_data['amount']) != int and type(json_data['amount']) != float:
      return jsonify({'status': 1,'message':'amount not provided'}), 400

    if type(json_data['players']) != list or len(json_data['players']) == 0:
      return jsonify({'status': 1,'message':'players list not provided'}), 400

    if type(json_data['type']) != str or json_data['type'] not in allowed_transactions:
      return jsonify({'status': 1,'message':'Invalid transaction type'}), 400

    amount = json_data['amount']
    payment = json_data['type'] == 'addition'

    for player_id in json_data['players']:

      player = Player.query.filter_by(id=player_id).first()
      
      if player is None:
          return jsonify({'status': 1,'message':'player not found'}), 404
      
      time = datetime.now().strftime("%H:%M:%S")
      if payment:

        player.amount = player.amount + amount
        hist_player = History(history=f"+ Recebeu {amount} do banco : {time}", player=player)

      else:

        amount = player.amount if amount > player.amount else amount
        player.amount = player.amount - amount
        hist_player = History(history=f"-Pagou {amount} ao banco : {time}", player=player)
      
      players_list.append({
                          'id': player.id,
                          'name': player.name,
                          'amount': player.amount,
                          'room': player.room_id,
                          'history': [{'id':hist.id, 'history': hist.history} for hist in player.history]
                          })

      db.session.add(hist_player)
      db.session.commit()

    return jsonify(players_list)


@app.route(route + '/players', methods=['DELETE'])
def players_delete():

  players = Player.query.all()

  for player in players:
    db.session.delete(player)
    db.session.commit()
  
  histories = History.query.all()

  for hist in histories:
    db.session.delete(hist)
    db.session.commit()
  
  return jsonify({}), 204


@app.route(route + '/rooms', methods=['DELETE'])
def rooms_delete():

  rooms = Room.query.all()

  for room in rooms:
    db.session.delete(room)
    db.session.commit()


  return jsonify({}), 204