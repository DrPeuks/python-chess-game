# BlobChess
A chess game written in Python based on python-chess and PyGame with which you can play against the Fairy Stockfish, a random move generator and Maia Chess. The Stockfish 14 NNUE evaluation is also available. 
I'm using the Lichess API for the opening explorer, and to let you play online against the Fairy Stockfish on Lichess (because it will play better openings) and the bots maia1, maia5 and maia9 on Lichess, still because of the openings. But in order to play online, you will have to create yourself a token to use the Lichess API here: https://lichess.org/account/oauth/token/create?scopes[]=challenge:read&scopes[]=challenge:write&scopes[]=board:play&description=Play+on+Lichess+from+BlobChess (the required scopes are prefilled)

First of all, I would like to thank:

  The Stockfish developers:
    https://stockfishchess.org/
    https://github.com/official-stockfish/Stockfish

  The Fairy Stockfish developer:
    https://github.com/ianfab/Fairy-Stockfish

  The Maia developers:
    https://maiachess.com/
    https://github.com/CSSLab/maia-chess

  Lichess for information about the Fairy-stockfish settings to make different levels:
    https:/lichess.org

  the Leela Chess Zero developers:
    https://github.com/LeelaChessZero/lc0
    
  Lichess for their API (and of course their amazing app):
    https://lichess.org/api

  And special thanks to @reidmcy for his support on creating this first repository which is my first one, and his technical help for Maia!






![image](https://user-images.githubusercontent.com/89562745/172292165-68dec124-f086-4966-9fb8-b11091face45.png)



Instead of playing against the Stockfish or whatever, you can also create a game with the Fairy-stockfish level 6 as White and Maia 1900 as Black! This kind of setup can prove instructive or fun to watch. The random move generator against itself is particularly funny! For example, one lucky day I watched a game with the random move generator playing against itself, and the game was drawn because of the most common stalemate among beginners : the one that is caused by a king and a queen that block a lonely king. Delightful! 
But you can't create a game with both sides playing online. And please, don't cheat on rated games by using the Stockfish otherwise you will get banned!



# Installation


## Linux

You need to compile the Stockfish.

Stockfish :

https://github.com/official-stockfish/Stockfish
Once the repo is cloned, navigate to Stockfish/src/ and run the following command to build : ```make net && make help && make build ARCH=[your_architecture]``` and replace [your_architecture] by for example x86-64 for common Linux computers or armv7 for a Raspberry Pi.

Then move the content of Stockfish to BlobChess/stockfish-linux/.

Then the path to Stockfish should be ```BlobChess/stockfish/src/stockfish``` but at line 170 you will have to edit the stockfish_path variable.


Lc0:

https://github.com/LeelaChessZero/lc0#building-and-running-lc0

Once you have completed the building instructions, move the content of ```lc0/``` to BlobChess/lc0-linux. Then, the path to Lc0 should be ```BlobChess/lc0-linux/build/release/lc0``` and then again at line 170, edit lc0_path.


Make sure that the paths are respected otherwise the program won't be able to load the engines, at least if you don't edit the code. You could create custom paths.


Fairy Stockfish

Download the Fairy Stockfish executable from https://github.com/ianfab/Fairy-Stockfish and place it in BlobChess/fairy-stockfish. Edit fairy_stockfish_path at line 170.

## Windows

For Windows, you don't really have to compile Stockfish and Lc0 by yourself, you can just download them :
https://stockfishchess.org/download/
Then unzip the downloaded file, and then move the executable file to BlobChess/stockfish-windows/
The path to Stockfish should then look like ```BlobChess/stockfish/stockfish-something-x-x.exe``` and edit stockfish_path variable.
Also make sure that there is only one executable file in BlobChess/stockfish-windows/ because the program will use the first executable file found in that directory.

For Lc0, you can download the Windows package at https://github.com/LeelaChessZero/lc0/releases/tag/v0.28.2, the one I recommend for CPU users is https://github.com/LeelaChessZero/lc0/releases/tag/v0.28.2

Then extract the content of the zip file to ```BlobChess/lc0/```. The path to Lc0 should then look like ```BlobChess/lc0/lc0.exe```


Fairy Stockfish

Same as for Linux, download the executable, place it in BlobChess/fairy-stockfish/ and edit fairy_stockfish_path.


To run this program, Python 3.x with pip needs to be installed on your machine (Linux or Windows as I did not integrate the Mac OS stockfish/fairy-stockfish/lc0 binaries yet) along with the Python modules PyGame, Chess, Stockfish and Tkinter.
To install them:
Linux:
	```pip install pygame chess stockfish``` or ```pip3 install pygame chess stockfish```
	for Ubuntu and Debian-based distros: ```sudo apt install python-tk``` or ```sudo apt install python3-tk```
	for Arch-based distros: ```sudo pacman -S tk```

  if you want to run CPU version : ```sudo apt install libopenblas-dev meson libgtest-dev```


Windows:
		`pip install pygame chess stockfish tk`





And then you are ready to go :
`python BlobChess.py`

And have fun!
