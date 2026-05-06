# chess_engine
attempt to code a functionnal chess engine using modern algorithms

Search logic :

A value for each piece is hardcoded as follow :(pawn: 1, bishop: 3.10, knight: 2.95, rook: 5, queen: 10) this aims to give an idea of the value of an exchange.
A dinamic grid attributes a value to each square of the board ranging from 0.1 to 0.5, the closer you get to the center and/or opponents king the higher the value.

The objective is to determine if a sequence of move is better than an other, for that purpose we use an evaluation depending on 2 factors:
    The material gain of the sequence represented by the value of the pieces captured - the value of the pieces the opponent captured
    The positional gain of the sequence is determined by the value of squares "controlled" by your pieces relatively to there privious position compared to the positional gain of your opponent in that same sequence.

Note that we always take in consideration that the opponent will make it's best legal move.


Optimisation :

There are many problems related to the optimisation of the engine:
  Limiting the number of calculated paths by trimming useless sequences :


One problem is determining whether the last few move will not be biased by a lack of power making the computer think moves such as sacrifices would be valuable :
  Quiscence search

Usage :
  If you want to try the engine for yourself, i recommend using lichess bot API which i personnaly use to try this engine, you will need python3 to be installed and the libraries listed in the requirements.txt file which you can download threw // pip install -r requirements.txt, you can then start the bot by just executing the main file with // python3 main.py
