import os
import difflib
from flask import Flask, jsonify, request, render_template, session
from flask_wtf import FlaskForm
from wtforms import StringField
import logging
import json
import string
from model import user_input_to_steamid, get_user_games, get_recs_from_appid, get_friends_recs, get_friends_games, get_user_recs, appid_to_name, is_multiplayer, multiplayer_games

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

app = Flask(__name__)
#app._static_folder = '/static'
app.config['SECRET_KEY']='\x9d|\xe4\x91\r<\xd8\x94\xf6\xa1\xde\xf7\xdc\x0b\x10\xb6\x92o9\xfe\x1e\xd8\xe9W'
class CompareForm(FlaskForm):
    name = StringField('name')

@app.route("/", methods=['GET'])
def home():
    return render_template("index.html")

#Implement the model result here
@app.route('/search',  methods=['GET', 'POST'])
def recommendation():
    user_input = request.args.get('user_input')
    steamid = user_input_to_steamid(user_input)
    user_games = get_user_games(steamid)
    user_recs = get_user_recs(user_games)
    friends_ids, friends_games = get_friends_games(steamid)
    friends_recs, allfriends_recs = get_friends_recs(friends_ids, friends_games)
    friends_recs_games = [int(val) for val in allfriends_recs]
    multigames = [int(val) for val in multiplayer_games]

    rec_intersect = dict.fromkeys(friends_ids)
    for i, friend_id in enumerate(friends_ids):
        rec_intersect[friend_id] = [int(id) for id in list(set(friends_recs[friend_id]) & set(user_recs['appid']))]

    return render_template("recommendations.html", steamid = steamid,
    user_games = user_games, friends_recs_games = friends_recs_games,
    user_recs = user_recs, friends_ids = [int(id) for id in friends_ids],
    rec_intersect = rec_intersect, multigames = multigames)

#    return jsonify({'error' : 'Could not find your ID!'})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
