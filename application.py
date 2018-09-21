import os
import difflib
from flask import Flask, jsonify, request, render_template, make_response, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField
import logging
import json
import string
from model import user_input_to_steamid, get_user_games, get_recs_from_appid, get_friends_recs, get_friends_games, get_user_recs, appid_to_name, is_multiplayer

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
    friends_recs = get_friends_recs(friends_ids, friends_games)

    rec_intersect = {key:[] for key in friends_recs.keys()}
    for i, friend_id in enumerate(friends_ids):
        rec_intersect[friend_id] = set(friends_recs[friend_id]) & set(user_recs['appid'])

    if len(list(rec_intersect.keys())[0]) > 0:
        common_friend1 = list(rec_intersect.keys())[0]
        common_game1 = appid_to_name[list(rec_intersect[common_friend1])[0]]

    if len(list(rec_intersect.keys())[1]) > 0:
        common_friend2 = list(rec_intersect.keys())[1]
        common_game2 = appid_to_name[list(rec_intersect[common_friend2])[0]]

    if len(list(rec_intersect.keys())[2]) > 0:
        common_friend3 = list(rec_intersect.keys())[2]
        common_game3 = appid_to_name[list(rec_intersect[common_friend3])[0]]

    if len(list(rec_intersect.keys())[3]) > 0:
        common_friend4 = list(rec_intersect.keys())[3]
        common_game4 = appid_to_name[list(rec_intersect[common_friend4])[1]]

    return render_template("recommendations.html", steamid = steamid, user_games = user_games, friends_recs = friends_recs, user_recs = user_recs, common_game1 = common_game1, common_friend1 = common_friend1, common_game2 = common_game2, common_friend2 = common_friend2, common_game3 = common_game3, common_friend3 = common_friend3, common_game4 = common_game4, common_friend4 = common_friend4)

#    return jsonify({'error' : 'Could not find your ID!'})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
