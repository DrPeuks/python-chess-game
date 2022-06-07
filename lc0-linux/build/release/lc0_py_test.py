from subprocess import *
import time





def ecommand(p, comm):

	p.stdin.write(f"{comm}\n")


def analyze(efile, _moveList):

	bestmove = "0000"

	p = Popen(efile, stdout=PIPE, stdin=PIPE, stderr=PIPE, bufsize=0, text=True)  # stderr=STDOUT, also send stderr to stdout to see everything in stdout

	ecommand(p, f"position startpos moves {moveList}")
	ecommand(p, "go nodes 2000")

	for line in iter(p.stdout.readline, ''): # read each line of engine output as it replies from our command
		
		line = line.strip()
		print(line)

		if line.startswith("bestmove"): # exit the loop when we get the engine bestmove

			bestmove = line.split()[1].strip()
			break


	ecommand(p, "quit") # properly quit the engine

	# Make sure process 'p' is terminated (if not terminated for some reason) as we already sent the quit command.
	try:
		p.communicate(timeout=5)
	except TimeoutExpired:
		p.kill()
		p.communicate()

	_moveList += bestmove + " "
	return bestmove, _moveList


moveList = ""

efile = "./lc0"
while True:
	bestmove, moveList = analyze(efile, moveList)
	print(f"\nbest move : {bestmove}\n")
	time.sleep(2)

	if len(moveList.split()) == 30:
		print("\n{}".format(moveList))
		break