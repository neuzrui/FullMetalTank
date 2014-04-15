----------------------- Python Version 2.7.5 ------------------------

1. To run the Wumpus game program, please enter
   "python WumpusGUI.py [PROVER9_BIN_PATH] [MAP_FILE_PATH]"
   on your command line. e.g "python WumpusGUI.py ./prover9 world1.txt"

2. At the beginning, the game will load the map from the configurations
   specified in the given "wumpus_world.txt" file. You can also load
   your favorites map by clicking the "load" button to load from other
   map files.

3. After a map is loaded and initialized, click "play" button to let
   the agent automatically explore the world. All the moving and
   important information along the way will be shown in the textbox.
   Scroll the textbox to review previous information.

4. After the agent finish the exploring, the textbox will show the
   total score and the number of steps taken to achieve the score.

5. Click "quit" button to quit the game if you want.

6. The "generate" button is not implemented yet due to tight time
   schedule. However, you can always load your favorite map file from
   file system by clicking the "load" button. This function will be
   finished in the future.

7. World examples:
   a. wumpus_world.txt is the example given.
   b. map1.txt and map2.txt are the files given by TA.
   c. world1.txt, world2.txt, world3.txt, world4.txt are the files created.
   d. wrong.txt is a invalid world file to test the program.

8. P9_input.txt and p9_input_template.txt are required files for the
   TheoremProver.py
