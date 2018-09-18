import os
import gensim
import difflib
from flask import Flask, jsonify, request, render_template, make_response, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField
import logging
import json
import string

def appid_to_name(gameid):
    with open('appid_to_game.json','r') as file:
        gamejson = json.load(file)
    gamelist = gamejson['applist']['apps']

    for ind, game in enumerate(gamelist):
        if game['appid'] == gameid:
            return game['name']

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
    user_input = request.args.get('steamid')
    steamid = convert2steamid(user_input)
    user_games = get_user_games(steamid)
    user_friends = get_user_friends(steamid)
    friend_games = get_friend_games(steamid)

    if steamid:
        #sim = model.docvecs.most_similar(positive=difflib.get_close_matches(str(name), perfumeslist, 1), topn=10)

        return render_template("recommendations.html")

    return jsonify({'error' : 'Could not find your ID!'})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
