from urllib.request import Request, urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import requests
import json
import pickle
import numpy as np
import pandas as pd

datapath = './static/data/'
api_key = 'removed - replace with yours'

BASE_URL = 'https://store.steampowered.com/app/'
session = requests.Session()

#import model
with open(datapath + 'model_30.pickle', 'rb') as fle:
    model = pickle.load(fle)

#import dictionaries
with open(datapath + 'appid_to_idx.txt', 'rb') as fle:
    appid_to_idx = pickle.load(fle)

with open(datapath + 'idx_to_appid.txt', 'rb') as fle:
    idx_to_appid = pickle.load(fle)

with open(datapath + 'steamid_to_idx.txt', 'rb') as fle:
    steamid_to_idx = pickle.load(fle)

with open(datapath + 'idx_to_steamid.txt', 'rb') as fle:
    idx_to_steamid = pickle.load(fle)

with open(datapath + 'appidx_to_name.txt', 'rb') as fle:
    appidx_to_name = pickle.load(fle)

with open(datapath + 'appid_to_name.txt', 'rb') as fle:
    appid_to_name = pickle.load(fle)

with open(datapath + 'multiplayer_games.txt', 'rb') as fle:
    multiplayer_games = pickle.load(fle)


#get game similarity matrix
def get_game_similarity(model):
    game_similarity = model.item_embeddings.dot(model.item_embeddings.T)
    #normalize by the max of each game-game embedding (i.e. self-embedding)
    norm = np.array([np.sqrt(np.diagonal(game_similarity))])
    game_similarity = game_similarity/norm/norm.T

    return game_similarity

game_similarity = get_game_similarity(model)

#get the games most similar to a game in the user's library (ranked)
def get_recs_from_appid(appid):
    try:
        appidx = appid_to_idx[appid]
    except KeyError:
        return []
    recs = game_similarity[appidx]
    df = pd.DataFrame({'game_idx':list(appidx_to_name), 'scores':recs})
    df = df.sort_values(by='scores', ascending=False)
    df['game_id'] = [idx_to_appid[idx] for idx in df.game_idx]
    df['game_names'] = [appidx_to_name[idx] for idx in df.game_idx]

    return df['game_id'].values, df['game_names'].values


#make API call to get user games from steam ID
def get_user_games(steamid):
    req = Request('http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=%s&steamid=%s&format=json&include_appinfo=True'%(api_key, steamid))

    try:
        data_raw = urlopen(req).read()
        data_json = json.loads(data_raw)
        user_games = data_json['response']['games']
        return user_games
    except:
        return []

#gets recommendations for the user (top 10)
def get_user_recs(user_games):
    user_recs = {'appid':[]}
    for i in range(0,34):
        if i < 100:
            try:
                rec_id, rec_name = get_recs_from_appid(user_games[i]['appid'])
                for i, r_id in enumerate(rec_id):
                    if i < 6 and i > 0:
                        user_recs['appid'].append(r_id)
            except ValueError:
                pass

    return user_recs

#make API call to get user friends from steam ID in the form of a dict {friendid:games}
def get_friends_games(steamid):
    req = Request('http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key=%s&steamid=%s&relationship=friend'%(api_key, steamid))

    try:
        data_raw = urlopen(req).read()
        data_json = json.loads(data_raw)
        user_friends = data_json['friendslist']['friends']
    except:
        return []

    friends_ids = [friend['steamid'] for friend in user_friends]
    friends_games = {}
    friends_games = {friend : get_user_games(friend) for friend in friends_ids}

    return friends_ids, friends_games

#make lists of recommendations for friends based on their libraries (top 10)
def get_friends_recs(friends_ids, friends_games):
    eachfriends_recs = {key:[] for key in friends_ids}
    allfriends_recs = []
    for i, friend_id in enumerate(friends_ids):
        friends_games_ids, friends_games_tplayed = sort_games_by_playtime(friends_games[friend_id])
        for i, game_id in enumerate(friends_games_ids):
            try:
                rec_id, rec_name = get_recs_from_appid(game_id)
                count = 0
                for i, r_id in enumerate(rec_id):
                    if count < 6 and i > 0 and is_multiplayer(r_id):
                        eachfriends_recs[friend_id].append(r_id)
                        allfriends_recs.append(r_id)
                        count += 1
            except ValueError:
                pass

    return eachfriends_recs, allfriends_recs


def sort_games_by_playtime(game_info):
	game_ids = [game['appid'] for game in game_info]
	playtimes = [game['playtime_forever'] for game in game_info]
	userdf = pd.DataFrame({'appid': game_ids, 'hours_played' : playtimes})
	userdf = userdf.sort_values(by='hours_played', ascending=False)

	return userdf.appid.values, userdf.hours_played.values

#check on from a set if the game is multiplayer
def is_multiplayer(appid):
    return appid in set(multiplayer_games)

#convert user input to steam ID
def user_input_to_steamid(input_id):
	req = Request('http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=%s&vanityurl=%s'%(api_key, input_id))

	try:
		data_raw = urlopen(req).read()
	except HTTPError:
		return input_id

	data_json = json.loads(data_raw)

	try:
		return int(data_json['response']['steamid'])
	except KeyError:
		return input_id
