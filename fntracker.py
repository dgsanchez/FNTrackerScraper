import requests
from bs4 import BeautifulSoup
import json
import time
import sys

url = 'https://fortnitetracker.com/events/epicgames_S14_FNCS_Qualifier1_EU_PC?window=S14_FNCS_Qualifier1_EU_PC_Event1'
url += '&page='

# Initialize variable that will hold the data
results = []
players = None
gamedata = None
accounts = None

# Different booleans for each exit condition.
found = False
found2 = False
found3 = False

# Variables for the player/id to be searched.
id_search = False
searched = ''
player_searched = None

points_top = 0
team_top = None
team_size = 0
teammates = None

top = 100

page = 0
num_players = 100

# Can either see how many points a placement position has or search for a player.
if len(sys.argv) > 1:
	try:
		top = int(sys.argv[1])
	except:
		searched = sys.argv[1].lower()

# Either search with an id or search player and number of points a place has.
if len(sys.argv) > 2:
	if sys.argv[1] == 'id':
		id_search = True
		searched = sys.argv[2]

	else:
		try:
			top = int(sys.argv[1])
			searched = sys.argv[2].lower()
		except:
			top = int(sys.argv[2])
			searched = sys.argv[1].lower()

# Limit the search to the first 2,000 players.
try:
	for page in range(20):
		
		# Getting the page and passing it through BeautifulSoup
		response = requests.get(url + str(page))

		soup = BeautifulSoup(response.text, 'html.parser')
		scripts = soup.find_all('script', type='text/javascript')

		for s in scripts:
			# Search for the leaderboard in the scripts.
			if 'var imp_leaderboard' in str(s):
				gamedata = str(s)
				
				# Save the leaderboard and pass it through JSON.
				gamedata = gamedata[len('var imp_leaderboard = ')+31:-10]
				gamedata = json.loads(gamedata)
		
				try:		
					accounts = gamedata['internal_Accounts']
					gamedata = gamedata['entries']

				except:
					pass

		players = {}

		# Little precaution in case page is empty.
		if accounts is None or gamedata is None:
			break

		# Search for the player and save all the players on the actual page.
		for tmp in accounts.keys():
			# print(accounts[tmp]['nickname'])
			players[tmp] = accounts[tmp]['nickname']

			if not id_search:
				if accounts[tmp]['nickname'].lower().find(searched.lower()) != -1 and not found:
					found = True
					player_searched = tmp

			else:
				if tmp == searched:
					found = True
					player_searched = tmp
		
		# Process the data and give the information if the player is found in this page.
		if found:
			for row in gamedata:
				team = row['teamAccountIds']

				if player_searched in team:

					count = 1
					for game in row['sessionHistory']:
						print('Game', count)
						print("Position:", game['trackedStats']['PLACEMENT_STAT_INDEX'])
						print("Kills:", game['trackedStats']['TEAM_ELIMS_STAT_INDEX'])
						print()

						count += 1

					tmp = []

					for idx, player in enumerate(team):
						tmp.append(players[player])

					print(', '.join(tmp))
					print("POSITION: ", row['rank'])
					print("POINTS: ", row['pointsEarned'], end="\n\n")

		# Check if the placement is in the actual page.
		if page == int((top - 1) / num_players):
			index = top - num_players * page

			team_top = gamedata[index - 1]['teamAccountIds']
			points_top = gamedata[index - 1]['pointsEarned']

			team_size = len(team_top)

			teammates = []

			for player in team_top:
				teammates.append(players[player])

			found2 = True

		# If both conditions are true, we're done.
		if found and found2:
			break

except KeyboardInterrupt:
	pass

print("-----> TOP " + str(top) + ":", points_top, "points", "-", end=" ")
print(', '.join(teammates))
