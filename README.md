# BlobChess
A chess game written in Python where you can play against the Fairy Stockfish, a random move generator and Maia Chess.

First of all, I would like to thank:
  The Stockfish developers:
    https://stockfishchess.org/
    https://github.com/official-stockfish/Stockfish
  The Fairy Stockfish developers:
    https://github.com/ianfab/Fairy-Stockfish
    
  The Maia developers:
    https://maiachess.com/
    https://github.com/CSSLab/maia-chess
    
  And the Leela Chess Zero developers:
    https://github.com/LeelaChessZero/lc0
    
  And special thanks to @reidmcy for his support on creating this first repository which is my first one, and his technical help for Maia!
  
  
  
![image](https://user-images.githubusercontent.com/89562745/172290954-09011cd7-327b-453d-be29-8bc0292d7aa4.png)


![image](https://user-images.githubusercontent.com/89562745/172292165-68dec124-f086-4966-9fb8-b11091face45.png)

  
  
  
# Running
To run this program, Python 3.x with pip needs to be installed on your machine (Linux or Windows as I did not integrate the Mac OS stockfish/fairy-stockfish/lc0 binaries yet) along with the Python modules PyGame, Chess, Stockfish and Tkinter.
To install them:
Linux:
	```pip install pygame chess stockfish``` or ```pip3 install pygame chess stockfish```
	for Ubuntu and Debian-based distros: ```sudo apt install python-tk``` or ```sudo apt install python3-tk```
	for Arch-based distros: ```sudo pacman -S tk```
		
Windows:
		`pip install pygame chess stockfish tk`
		
		
And then you are ready to go :
`python BlobChess.py`

And have fun!
