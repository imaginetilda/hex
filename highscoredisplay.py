import tkinter as tk
import random
from tkinter import *
from tkinter import messagebox, scrolledtext
import re #regular expression module
import math
import os
import webbrowser
import json


""" Constants """

# Window Dimensions
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 800

# Dimensions for displaying colour squares in the main game
CANVAS_WIDTH = 400
CANVAS_HEIGHT = 200

# Default colours for initialising the main game
DEFAULT_TARGET_COLOUR = "#888888"
HEX_RED = "88"
HEX_GREEN = "88"
HEX_BLUE = "88"
DEFAULT_GUESS_COLOUR = "#888888"

# The size of the boxes containing the target colour and the guessed colour
COLOUR_BOX_HEIGHT = 150
COLOUR_BOX_WIDTH = 150

# The length of each colour guess, ie the length of a Colour Hex Code
HEX_LENGTH = 6

# The number of guesses allowed in the main game before it is Game Over
MAX_ALLOWED_GUESSES = 8

# How helpful are the error margin indicators. 2 is very easy - must be a value 2 or greater
ERROR_MARGIN_INDICATOR_DIFFICULTY = 2 

# The tag used for headings in the help text. This is the only one we're doing for now, but we could add more later.
TAG_HEADING = "heading"

# The help HTML file to be opened
HTML_FILE_TO_OPEN = "help.html"

# The High Scores json file to be opened
HIGH_SCORE_FILE = "highscores.json"


# main
class HexGame(tk.Tk):
    """
    This is the main class for the game. It controls which windows should be displayed.
    """
    def __init__(self):
        """ Initalise """    
        super().__init__()
        self.title("Hex-a-Guess-a")
        self.geometry("500x900")
        self.minsize(500,900)
       # self.resizable(False, False)

        # configure grid for centering content
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.current_frame = None # to keep track of the currently displayed frame

        self.show_high_score_screen() # show high score screen

    def switch_frame(self, frame_class):
        """removes current frame and switches to new"""
        if self.current_frame:
            self.current_frame.destroy() # remove  old frame
        new_frame = frame_class(self) # make new frame, passing self (the hexgame instance)
        self.current_frame = new_frame
        self.current_frame.grid(row=0, column=0, sticky="nsew") # make new frame
   


    def show_high_score_screen(self):
        """display high scores screen"""
        self.switch_frame(HighScoreScreen)    




class HighScoreScreen(tk.Frame):
    '''Display the high scores'''
    def __init__(self, master):
        super().__init__(master, bg="white")
        self.master = master # reference to the main application

        # configure grid for centering buttons within this frame
        self.grid_rowconfigure(0, weight=0) # for buttons - minimise to the top
        self.grid_rowconfigure(1, weight=1) # for help text - maximimise to fill the rest of the frame
       
        self.grid_columnconfigure(0, weight=1) # fill the width of the frame

        # back button
        back_button = tk.Button(self, text="Back",
                                 font=("Arial Rounded MT Bold", 14), bg="light blue", fg="black",
                                 activebackground="dark blue", activeforeground="white",
                                 width=15, relief="flat", bd=2,
                                 command=self.master.show_high_score_screen) #For testing purposes - needs to be changed when adding it to the main app!!!
        back_button.grid(row=0, column=0, pady=(10, 20), sticky="n",)


        # frame to hold difficulty buttons for better layout
        self.scores_frame = tk.Frame(self, bg="white")
        self.scores_frame.grid(row=1, column=0, pady=20)

        self.load_and_display_scores()



    def load_and_display_scores(self):
        """
        Reads the JSON High Score file and updates the GUI with the score data.
        """

       
        if not os.path.exists(HIGH_SCORE_FILE):
            messagebox.showerror("High Score File Not Found", f"The file '{HIGH_SCORE_FILE}' does not exist.")
            return

        try:
            with open(HIGH_SCORE_FILE, "r") as high_score_file:
                high_score_data = json.load(high_score_file)
        except json.JSONDecodeError:
            messagebox.showerror("JSON Error", "Could not decode High Score JSON from file.")
            return
        except IOError as e:
            messagebox.showerror("File Error", f"An error occurred while reading the High Score file: {e}")
            return

        # Start grid layout from the top
        row_counter = 1
        for difficulty, players in high_score_data.items():
            # Create a label for the difficulty level spanning two columns
            difficulty_label = tk.Label(self.scores_frame, text=f"{difficulty.capitalize()} ", font=("Arial Rounded MT Bold", 26, "bold"))
            difficulty_label.grid(row=row_counter, column=0, columnspan=2, pady=(15, 5))
            row_counter += 1

            # Create header labels for the columns
            player_header = tk.Label(self.scores_frame, text="Player Name", font=("Helvetica", 20, "bold"))
            player_header.grid(row=row_counter, column=0, padx=10, pady=2, sticky="w")
            score_header = tk.Label(self.scores_frame, text="Score", font=("Helvetica", 18, "bold"))
            score_header.grid(row=row_counter, column=1, padx=10, pady=2, sticky="w")
            row_counter += 1
            
            # Display the scores for each player
            for player in players:
                player_name_label = tk.Label(self.scores_frame, text=player["player_name"], font=("Helvetica", 18, "bold"))
                player_name_label.grid(row=row_counter, column=0, padx=10, pady=2, sticky="w")
                
                score_label = tk.Label(self.scores_frame, text=player["score"], font=("Helvetica", 18, "bold"))
                score_label.grid(row=row_counter, column=1, padx=10, pady=2, sticky="w")
                
                row_counter += 1
        
      

   
# run game
if __name__ == "__main__":
    app = HexGame()
    app.mainloop()