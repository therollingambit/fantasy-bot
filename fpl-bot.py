import os
import telebot
import requests
import pandas as pd

my_secret = os.environ['API_KEY']
bot = telebot.TeleBot(my_secret)

def merge_list(l1, l2, l3):
  return list(map(lambda x, y, z:(x,y,z), l1, l2, l3))

#API Set-Up
url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
r = requests.get(url)
json = r.json()

elements_df = pd.DataFrame(json['elements'])
element_types_df = pd.DataFrame(json['element_types'])
teams_df = pd.DataFrame(json['teams'])

main_df = elements_df[['web_name','first_name','team','element_type','now_cost','selected_by_percent', 'transfers_in','transfers_out','form','event_points','total_points','bonus','points_per_game', 'value_season','minutes','goals_scored','assists','ict_index','clean_sheets','saves']]

#merging elements_types_df onto main_df
main_df = pd.merge(left=main_df,right=element_types_df[['id','singular_name']],left_on='element_type', right_on='id', how='left')
main_df = main_df.drop(["id", "element_type"],axis=1)
main_df = main_df.rename(columns = {'singular_name': 'position'})

#merging teams_df onto main_df
main_df = pd.merge(left=main_df,right=teams_df[['id','name','played','strength_overall_away','strength_overall_home']],left_on='team', right_on='id', how='left')
main_df = main_df.drop(["id", "team"],axis=1)
main_df = main_df.rename(columns = {'name': 'team'})

#Additional columns stored as floats
main_df['value'] = main_df.value_season.astype(float)
main_df['ict_score'] = main_df.ict_index.astype(float)
main_df['selection_percentage'] = main_df.selected_by_percent.astype(float)
main_df['current_form'] = main_df.form.astype(float)

#Total Goals Contribution column = Goals + Assists
main_df['total_contribution']= main_df['goals_scored'] + main_df['assists']

gk_df = main_df.loc[main_df.position == 'Goalkeeper']
gk_df = gk_df[['web_name','team','selection_percentage','now_cost','clean_sheets','saves','bonus','total_points','value']]
def_df = main_df.loc[main_df.position == 'Defender']
def_df = def_df[['web_name','team','selection_percentage','now_cost','clean_sheets','assists','goals_scored','total_contribution','ict_score','bonus','total_points','value']]
mid_df = main_df.loc[main_df.position == 'Midfielder']
mid_df = mid_df[['web_name','team','selection_percentage','now_cost','assists','goals_scored','total_contribution','ict_score','current_form','bonus','total_points','value']]
fwd_df = main_df.loc[main_df.position == 'Forward']
fwd_df = fwd_df[['web_name','team','selection_percentage','now_cost','assists','goals_scored','total_contribution','ict_score','current_form','minutes','bonus','total_points','value']]

# top 5 players
top5_gk_df = gk_df.nlargest(5, 'value')
top5_def_df = def_df.nlargest(5, 'value')
top5_mid_df = mid_df.nlargest(5, 'value')
top5_fwd_df = fwd_df.nlargest(5, 'value')

# bot commands
@bot.message_handler(commands=['start'])
def start(message):
  bot.reply_to(message, """
    Welcome to fpl top 5 players! 🏴󠁧󠁢󠁥󠁮󠁧󠁿

    /help - list of commands 🙋🏻‍♂️

    /gk - top 5 goalkeepers 🧤

    /def - top 5 defenders 🪨

    /mid - top 5 midfielders 🏃🏻‍♂️

    /fwd - top 5 forwards ⚽️
  """)

@bot.message_handler(commands=['help'])
def help(message):
  bot.reply_to(message, """
    Get your data by position now 😋

    /gk - top 5 goalkeepers 🧤

    /def - top 5 defenders 🪨

    /mid - top 5 midfielders 🏃🏻‍♂️

    /fwd - top 5 forwards ⚽️
  """)

@bot.message_handler(commands=['gk'])
def gk(message):
  names = top5_gk_df.web_name.tolist()
  clubs = top5_gk_df.team.tolist()
  prices = top5_gk_df.now_cost.tolist()
  arr = merge_list(names, clubs, prices)

  results = '''name            club              price
-----------------------------------\n'''
  for value in arr:
    for x in value:
      if isinstance(x, int):
        x /= 10
        x = '£' + str(x) + 'm'
      results += str(x) + '        '

    results += '\n'

  bot.send_message(message.chat.id, results)

@bot.message_handler(commands=['def'])
def df(message):
  names = top5_def_df.web_name.tolist()
  clubs = top5_def_df.team.tolist()
  prices = top5_def_df.now_cost.tolist()
  arr = merge_list(names, clubs, prices)

  results = '''name            club              price
-----------------------------------\n'''
  for value in arr:
    for x in value:
      if isinstance(x, int):
        x /= 10
        x = '£' + str(x) + 'm'
      results += str(x) + '        '

    results += '\n'

  bot.send_message(message.chat.id, results)

@bot.message_handler(commands=['mid'])
def md(message):
  names = top5_mid_df.web_name.tolist()
  clubs = top5_mid_df.team.tolist()
  prices = top5_mid_df.now_cost.tolist()
  arr = merge_list(names, clubs, prices)

  results = '''name            club              price
-----------------------------------\n'''
  for value in arr:
    for x in value:
      if isinstance(x, int):
        x /= 10
        x = '£' + str(x) + 'm'
      results += str(x) + '        '

    results += '\n'

  bot.send_message(message.chat.id, results)

@bot.message_handler(commands=['fwd'])
def fwd(message):
  # results = ''
  # for _, txt in enumerate(top5_fwd_df.web_name):
  #   results += str(txt) + '\n'

  # bot.send_message(message.chat.id, results)
  names = top5_fwd_df.web_name.tolist()
  clubs = top5_fwd_df.team.tolist()
  prices = top5_fwd_df.now_cost.tolist()
  arr = merge_list(names, clubs, prices)

  results = '''name            club              price
-----------------------------------\n'''
  for value in arr:
    for x in value:
      if isinstance(x, int):
        x /= 10
        x = '£' + str(x) + 'm'
      results += str(x) + '        '

    results += '\n'

  bot.send_message(message.chat.id, results)

bot.polling()