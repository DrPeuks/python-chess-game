# BlobChess
A chess game written in Python based on python-chess and PyGame with which you can play against the Fairy Stockfish, a random move generator and Maia Chess. The Stockfish 14 NNUE evaluation is also available.

First of all, I would like to thank:

  The Stockfish developers:
    https://stockfishchess.org/
    https://github.com/official-stockfish/Stockfish
    
  The Fairy Stockfish developers:
    https://github.com/ianfab/Fairy-Stockfish

  The Maia developers:
    https://maiachess.com/
    https://github.com/CSSLab/maia-chess

  Lichess for information about the Fairy-stockfish settings to make different levels:
    https:/lichess.org

  And the Leela Chess Zero developers:
    https://github.com/LeelaChessZero/lc0

  And special thanks to @reidmcy for his support on creating this first repository which is my first one, and his technical help for Maia!



![image](https://user-images.githubusercontent.com/89562745/172290954-09011cd7-327b-453d-be29-8bc0292d7aa4.png)


![image](https://user-images.githubusercontent.com/89562745/172292165-68dec124-f086-4966-9fb8-b11091face45.png)



Instead of playing against the Stockfish or whatever, you can also create a game with the Fairy-stockfish level 6 as White and Maia 1900 as Black! This kind of setup can prove instructive or fun to watch. The random move generator against itself is particularly funny!



# Installation


## Linux

You need to compile the Stockfish and Lc0 as the Fairy-stockfish is already provided.

Stockfish :

https://github.com/official-stockfish/Stockfish
Once the repo is cloned, navigate to Stockfish/src/ and run the following command to build : ```make net && make help && make-build ARCH=[your_architecture]``` and replace [your_architecture] by for example x86_64 for common Linux computers or armv7 for a Raspberry Pi.

Then move the content of Stockfish to BlobChess/stockfish-linux/.

Then the path to Stockfish should be ```BlobChess/stockfish-linux/src/stockfish```.


Lc0:

https://github.com/LeelaChessZero/lc0#building-and-running-lc0

Once you have completed the building instructions, move the content of ```lc0/``` to BlobChess/lc0-linux. Then, the path to Lc0 should be ```BlobChess/lc0-linux/build/release/lc0```


Make sure that the paths are respected otherwise the program won't be able to load the engines, at least if you don't edit the code. You could create custom paths.



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
