import json
from uuid import uuid4
from flask import Flask, jsonify, request

from firebaseadmin import connection

app = Flask(__name__)

path = '/api'

db  = connection()

rooms = []
players = []

@app.route( path +  '/rooms', methods=['GET', 'POST'])
def rooms_api():

  
  if request.method == "POST":
    
    initial_amount = float(25000)

    if request.data is not None:
      json_data = json.loads(request.data)
      if type(json_data['amount']) == float or type(json_data['amount']) == int:
        initial_amount = float(json_data['amount'])

    room = {'id': str(uuid4()) , 'amount': initial_amount }
    rooms.append(room)

    return jsonify(room), 201

  else: #GET

    id = request.args.get('id', None)
    
    if id is not None:
      try:
        room = list(filter( lambda x: x['id'] == id, rooms))
      except:
        room = None
      
      if room is not None:
        return jsonify(room), 200

    return jsonify(rooms), 200


@app.route( path +  '/players', methods=['POST','GET'])
def player():

  if request.method == "POST":

    if request.data is None:
      return jsonify({'status': 1, "message": "Empty body"}), 400

    json_data = json.loads(request.data)

    if not json_data['room_id'] or not json_data['name']:
      return jsonify({'status': 1, "message": "Player name and room_id must be provided."}), 400
        
    try:
      room = list(filter( lambda x: x['id'] == json_data['room_id'], rooms))[0]
    except:
      room = None

    if room is None:
      return jsonify({'status': 1, "message": "Room not found"}), 404

    new_player = {
                'id': str( uuid4() ) , 
                'name': json_data['name'], 
                'room': room['id'] , 
                'amount': room['amount'],
                'history': []
              }
    players.append( new_player )

    return jsonify(new_player), 201

  else: #GET

    id = request.args.get('id',None)
    room_id = request.args.get('room',  None)

    if room_id is not None and id is not None:
      try:
        player_list = list(filter(lambda x: x['room'] == room_id, players))
      except:
        player_list = None

      if player_list is not None:
        if id is not None:
          try:
            list_by_id = list(filter(lambda x: x['id'] == id, players))
          except:
            list_by_id = None
        
          if list_by_id is not None:
            return jsonify(list_by_id)

        return jsonify(player_list), 200
      return jsonify(players), 200

    if room_id is not None:
      try:
        player_list = list(filter(lambda x: x['room'] == room_id, players))
      except:
        player_list = None

      if player_list is not None:
        return jsonify(player_list), 200

      return jsonify(players), 200

    if id is not None:
      try:
        player_list = list(filter(lambda x: x['id'] == id, players))
      except:
        player_list = None

      if player_list is not None:
        return jsonify(player_list), 200
        
      return jsonify(players), 200

    return jsonify(players), 200


@app.route( path +  '/players/payment', methods=['POST'])
def player_amount_pay():

    if request.data is None:
      return jsonify({'status': 1,'message':'payload not provided'}), 400


    json_data = json.loads(request.data)

    if type(json_data['amount']) != int and type(json_data['amount']) != float:
      return jsonify({'status': 1,'message':'amount not provided'}), 400
      
    if type(json_data['payer']) != str:
      return jsonify({'status': 1,'message':'payer_id not provided'}), 400
    
    if type(json_data['receiver']) != str:
      return jsonify({'status': 1,'message':'receiver_id not provided'}), 400
    
    id_payer = json_data['payer']
    id_receiver = json_data['receiver']

    players_id = [ id_payer, id_receiver]

    payer_index = -1
    receiver_index = -1

    for i in range(len(players)):
      if players[i]['id'] == id_payer:
        payer_index = i
      if players[i]['id'] == id_receiver:
        receiver_index = i
    
    if payer_index < 0:
      return jsonify({'status': 1,'message':'payer not found'}), 404

    if receiver_index < 0:
      return jsonify({'status': 1,'message':'receiver not found'}), 404

    amount = json_data['amount']

    amount = players[payer_index]['amount'] if amount > players[payer_index]['amount'] else amount

    players[payer_index]['amount'] -= amount
    players[receiver_index]['amount'] += amount

    players[payer_index]['history'].append(f"pagou {amount} para {players[receiver_index]['name']}")
    players[receiver_index]['history'].append(f"recebeu {amount} de {players[payer_index]['name']}")

    player_list = [ players[payer_index] , players[receiver_index] ]
    return jsonify(player_list)


@app.route( path +  '/players/amount', methods=['POST'])
def player_amount():

    allowed_transactions = ['addition', 'deduction']

    if request.data is None:
      return jsonify({'status': 1,'message':'payload not provided'}), 400

    json_data = json.loads(request.data)

    if type(json_data['amount']) != int and type(json_data['amount']) != float:
      return jsonify({'status': 1,'message':'amount not provided'}), 400

    if type(json_data['players']) != list or len(json_data['players']) == 0:
      return jsonify({'status': 1,'message':'players list not provided'}), 400

    if type(json_data['type']) != str or json_data['type'] not in allowed_transactions:
      return jsonify({'status': 1,'message':'Invalid transaction type'}), 400

    player_idex = -1
    amount = json_data['amount']
    payment = json_data['type'] == 'addition'

    for player in json_data['players']:

      for i in range(len(players)):
        if players[i]['id'] == player:
          player_idex = i
          break
      
      if player_idex < 0:
          return jsonify({'status': 1,'message':'player not found'}), 404

      if payment:
        players[player_idex]['amount'] += amount
        players[player_idex]['history'].append(f"recebeu {amount} do banco")
      else:
        amount = players[player_idex]['amount'] if amount > players[player_idex]['amount'] else amount
        players[player_idex]['amount'] -= amount
        players[player_idex]['history'].append(f"pagou {amount} ao banco")

    new_list = list(filter(lambda x: x['id'] in json_data['players'], players))

    return jsonify(new_list)

if __name__ == '__main__':
  app.run(debug=False, host='25.115.201.183',port=5200)