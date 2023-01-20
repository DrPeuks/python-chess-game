import berserk
import chess
import json
import requests
import subprocess
import threading





class PlayGame(threading.Thread):

	def __init__(self, client, game_id, **kwargs):

		super().__init__(**kwargs)
		self.client = client
		self.stream = client.board.stream_game_state(game_id)
		self.current_state = next(self.stream)
		self.moves = []
		self.whiteToPlay = True



	def run(self):

		for event in self.stream:
			if event['type'] == 'gameState':
				self.handle_state_change(event)
			elif event['type'] == 'chatLine':
				self.handle_chat_line(event)
			elif event['type'] == 'gameFull':
				print(event)


	def handle_state_change(self, game_state):

		moves = game_state['moves'].split()
		self.moves = moves
		if len(self.moves) % 2 == 0:
			self.whiteToPlay = True
		elif len(self.moves) % 2 == 1:
			self.whiteToPlay = False


	def handle_chat_line(self, chatLineState):

		pass

	def handle_full_change(self, fullState):

		pass


	def get_last_move(self):


		return self.moves[len(self.moves)-1]






lichessToken = ''


class LichessGame:

	def __init__(self, target, white=['User'], black=['Stockfish', 1], timeControl=[15, 10]):


		self.white = white
		self.black = black

		self.session = berserk.TokenSession(lichessToken)
		self.client = berserk.Client(session=self.session)

		self.gameId = ''
		self.gameData = self.create_game(white, black, timeControl, target, 'maia1')



	def create_game(self, white, black, timeControl, target='ai', player=''):

		if target == 'ai':
			if self.white[0] == 'User' and self.black[0] == "Stockfish":
				color = "white"
				level = self.black[1]
				gameData = self.client.challenges.create_ai(level=self.black[1], color='white')
			elif self.white[0] == 'Stockfish' and self.black[0] == 'User':
				color = 'black'
				level = self.white[1]
				gameData = self.client.challenges.create_ai(level=self.white[1], color='black')
			#gameData = subprocess.check_output(['curl', '-H', f'Authorization: Bearer {lichessToken}', '-d', 'keepAliveStream=true', 'https://lichess.org/api/challenge/ai', '-d', 'level='+str(level)+'&days=14&color='+color])

			self.gameId = gameData['id']

			self.gamePlayer = PlayGame(self.client, gameData['id'])
			self.gamePlayer.start()

		elif target == 'player':

			#gameData = self.client.challenges.create(username='maia1', rated=False, clock_limit=900, clock_increment=10, color='white')



			if self.white[0] == 'User' and self.black[0] == 'Maia Chess':
				maiaLevel = int((int(self.black[1]) - 1000) / 100)
				gameData = json.loads(subprocess.check_output(['curl', '-X', 'POST', '-H', f'Authorization: Bearer {lichessToken}', f'https://lichess.org/api/challenge/maia{maiaLevel}', '-d', 'rated=false&clock.limit=300&clock.increment=3&color=white']))
				print(gameData)
			elif self.white[0] == 'Maia Chess' and self.black[0] == 'User':
				maiaLevel = int((int(self.white[1]) - 1000) / 100)
				gameData = json.loads(subprocess.check_output(['curl', '-X', 'POST', '-H', f'Authorization: Bearer {lichessToken}', 'https://lichess.org/api/challenge/maia{maiaLevel}', '-d', 'rated=false&clock.limit=900&clock.increment=10&color=black']))
				print(gameData)



			#print(gameData)

			ongoingGames = json.loads(subprocess.check_output(['curl', '-X', 'GET', '-H', f'Authorization: Bearer {lichessToken}', 'https://lichess.org/api/account/playing', '-d', 'nb=1']))
			#print(ongoingGames)

			self.gameId = gameData['challenge']['id']




			self.gamePlayer = PlayGame(self.client, game_id=self.gameId)
			self.gamePlayer.start()


		return gameData

	def makeMove(self, move):


		self.client.board.make_move(self.gameId, move)
