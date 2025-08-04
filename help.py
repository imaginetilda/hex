import tkinter as tk
import random
from tkinter import *
from tkinter import messagebox, scrolledtext
import re #regular expression module
import math
import os


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

        # configure grid for centering content
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.current_frame = None # to keep track of the currently displayed frame

        self.show_help_screen() # show main menu


    def switch_frame(self, frame_class):
        """removes current frame and switches to new"""
        if self.current_frame:
            self.current_frame.destroy() # remove  old frame
        new_frame = frame_class(self) # make new frame, passing self (the hexgame instance)
        self.current_frame = new_frame
        self.current_frame.grid(row=0, column=0, sticky="nsew") # make new frame
   

    def show_help_screen(self):
        """standard game screen"""
        self.switch_frame(HelpScreen)    




class HelpScreen(tk.Frame):
    '''Display text file containing the help'''
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
                                 command=self.master.show_help_screen) #For testing purposes - needs to be changed when adding it to the main app!!!
        back_button.grid(row=0, column=0, pady=(10, 20), sticky="n",)


        self.text_area = scrolledtext.ScrolledText(
            self,
            # Wrap words at the window boundary
            wrap=tk.WORD,
            font=("Arial", 12),
            # padding within widget
            padx=10,       
            pady=10,       
        )
        self.text_area.grid(
            row=1,        
            column=0,      
            sticky="nsew", 
        )

        # Load and parse the file
        self.load_and_display_text("Help Component\help.txt")

        # Make the text area read-only after loading
        self.text_area.config(state=tk.DISABLED)

 
    def load_and_display_text(self, file_name):

        # Use try, because there is a lot that can go wrong - the file doesn't exist or contains garbage.
        # By using try, if it fails for some reason, the app can put up an error message instead of crashing the program
        try:
            # OPen the file read only
            with open(file_name, "r", encoding="utf-8") as help_file:
                help_lines = help_file.readlines()

            for help_line in help_lines:
                # remove trailing new line
                help_line = help_line.strip('\n')


                self.text_area.insert(tk.END, help_line)
                 # Add newline after each processed line
                self.text_area.insert(tk.END, "\n")

        except FileNotFoundError:
            messagebox.showerror("Error", f"File not found: {file_name}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

   
# run game
if __name__ == "__main__":
    app = HexGame()
    app.mainloop()