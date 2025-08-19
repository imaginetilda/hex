# =====================================
# Project Name: HexaGuessa
# Author: Jessica Bell
# Version: 1
# Date: 11/08/25
# Description: A hex code guessing game
# ======================================
import json
import math
import os
import random
import re
import webbrowser
import tkinter as tk
from tkinter import *
from tkinter import messagebox, scrolledtext
"""Constants."""

# Window Dimensions
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 1000
# Dimensions for displaying colour squares in the main game
CANVAS_WIDTH = 400
CANVAS_HEIGHT = 200
# The size of the boxes containing the target colour and the
# guessed colour
COLOUR_BOX_HEIGHT = 150
COLOUR_BOX_WIDTH = 150
# The length of each colour guess, ie the length of a Colour Hex Code
HEX_LENGTH = 6
# The number of guesses allowed in the main game before it is Game Over
MAX_ALLOWED_GUESSES = 8
# How helpful are the error margin indicators.
# 2 is very easy - must be a value 2 or greater
ERR_INDICATOR_DIFFICULTY = 2
# The tag used for headings in the help text.
# This is the only one we're doing for now, but we could add more later.
TAG_HEADING = "heading"
# Files
LOGO_IMAGE = "hexaguessa.png"
HIGH_SCORE_FILE = "highscores.json"
HTML_FILE_TO_OPEN = "help.html"
HELP_TEXT_FILE = "help.txt"
# Difficulty levels for the game
DIFFICULTY_STANDARD = "Standard"
DIFFICULTY_EXPERT = "Expert"
# Button colours
DEFAULT_BUTTON_COLOUR = "light blue"
DEFAULT_ACTIVE_BUTTON_COLOUR = "dark blue"
# Font
FONT = "Arial Rounded MT Bold"


# main
class HexGame(tk.Tk):
    """
    This is the main class for the game.
    It controls which windows should be displayed.
    """

    def __init__(self):
        """Initalise."""
        super().__init__()
        self.title("Hex-a-Guess-a")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.difficulty = DIFFICULTY_STANDARD
        # configure grid for centering content
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # To keep track of currently displayed frame
        self.current_frame = None
        self.show_menu_screen()

    def switch_frame(self, frame_class):
        """Remove current frame and switch to new,
            ie moving from screen to screen
            frame_class is the window we are going to change to
        """
        if self.current_frame:
            self.current_frame.destroy()  # remove old frame
        new_frame = frame_class(self)
        self.current_frame = new_frame
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def show_menu_screen(self):
        """Main menu."""
        self.switch_frame(MenuScreen)

    def show_new_game_screen(self):
        """New game options screen."""
        self.switch_frame(NewGameScreen)

    def exit_game(self):
        """End everything and close the game."""
        self.destroy()

    def show_game(self, difficulty):
        """Play the game with the difficulty selected."""
        self.difficulty = difficulty
        self.switch_frame(PlayGame)

    def show_help_screen(self):
        """Help screen."""
        self.switch_frame(HelpScreen)

    def show_high_score_screen(self):
        """Display high scores screen."""
        self.switch_frame(HighScoreScreen)

    def show_enter_high_score_screen(self, score):
        """Player gets a high score show this screen.
        This screen will only ever be entered from PlayGame,
        ie the player cannot navigate to this page from a menu etc
        score is a decimal value
        """
        self.score = score
        if self.current_frame:
            self.current_frame.destroy()  # remove old frame
        self.current_frame = EnterHighScoreScreen(self, self.score)
        self.current_frame.grid(row=0, column=0, sticky="nsew")


class MainGameLayout(tk.Frame):
    """This contains the layout for the PlayGame screen.
    It separates the logic from the layout.
    It does not add in bindings etc to the entries,
    as this is done and handled in the game logic
    """
    def __init__(self, master):
        super().__init__(master, bg="white")
        self.master = master
        # Define the layout for each column in the grid
        for i in range(MAX_ALLOWED_GUESSES - 1):
            # for padding at bottom
            self.grid_columnconfigure(i, weight=0)
        # The first and last column is space from left of the grid to
        # the left of the window, and from the right of the grid to the
        # right edge of the window, hence weight=1
        self.grid_columnconfigure(0, weight=1)  # for padding at left
        for i in range(1, HEX_LENGTH + 1):
            # don't stretch the entries in the main part of the grid
            self.grid_columnconfigure(i, weight=0)
        self.grid_columnconfigure(8, weight=1)  # for padding at right
        # The area at the top containing the coloured boxes
        self.colour_canvas = self.create_canvas()
        self.target_box = self.create_target_box()
        self.guess_box = self.create_guess_box()
        self.guess_grid = self.create_guess_grid()
        self.entry_boxes = []  # To store references to our Entry widgets
        # To store their associated StringVars, ie their values
        self.entry_input_values = []
        # Create the boxes where we enter our guesses in to
        for i in range(HEX_LENGTH):
            # Create a StringVar for each entry
            var = tk.StringVar()
            self.entry_input_values.append(var)
            # Create the Entry widget,
            # ie each box where you enter your guess
            entry = tk.Entry(self,
                             textvariable=var,
                             width=2,
                             font=(FONT,25)
                            )
            entry.grid(row=3, column=i+1, padx=5, pady=2, sticky='ew')
            self.entry_boxes.append(entry)
        # main manu button, so we can quit the game at any point
        self.main_menu_button = tk.Button(self,
                                    text="Main Menu",
                                    font=(FONT, 14),
                                    bg=DEFAULT_BUTTON_COLOUR,
                                    fg="black",
                                    activebackground=DEFAULT_ACTIVE_BUTTON_COLOUR,
                                    activeforeground="white",
                                    width=15,
                                    relief="raised",
                                    bd=2,
                                    command=self.return_to_main_menu)
        self.main_menu_button.grid(row=(MAX_ALLOWED_GUESSES * 2) + 5,
                                    column=2,
                                    columnspan=HEX_LENGTH-2,
                                    pady=(10, 20),
                                    sticky="n")

    def create_canvas(self):
        """Create the area that contains squares containing the
            squares of the target colour and the previous guess's colour
        """
        colour_canvas = tk.Canvas(self,
                                width=CANVAS_WIDTH,
                                height=CANVAS_HEIGHT,
                                bg="white",
                                highlightbackground="black",
                                highlightthickness=2)
        # Position the canvas with a blank column to the left in order
        # to centre correctly with the guessed grid
        colour_canvas.grid(row=0,
                            column=1,
                            columnspan = HEX_LENGTH + 0,
                            padx=5,
                            pady=10,
                            sticky='w')
        return colour_canvas

    def create_target_box(self):
        """Create a square area containing the actual target colour"""
        # draw a rectangle (the "box") on the canvas
        # coordinates are (x1, y1, x2, y2) where
        # (x1, y1) is the top-left corner
        # and (x2, y2) is the bottom-right corner
        # The 'fill' option sets the solid colour
        # The 'outline' option sets the border colour
          
        # Calculate coordinates to center the target box on the
        # LEFT HALF of the canvas
        x1 = (CANVAS_WIDTH / 2 - COLOUR_BOX_WIDTH) / 2
        y1 = ((CANVAS_HEIGHT - COLOUR_BOX_HEIGHT) / 2)+10
        x2 = x1 + COLOUR_BOX_WIDTH
        y2 = y1 + COLOUR_BOX_HEIGHT
        self.targetBox = self.colour_canvas.create_rectangle(x1, y1, x2, y2,
                                                             fill="#888888",
                                                             outline="",
                                                             width=0)
        # Add centered text above the target box
        text_x = x1 + COLOUR_BOX_WIDTH / 2
        text_y = y1 - 15  # Place text slightly above the box's top edge
        if text_y < 0:  # Ensure text is not drawn off-canvas top edge
            text_y = 15  # Default to 15 pixels from canvas top
        self.colour_canvas.create_text(text_x, text_y,
                                       text="Target Colour",
                                       font=(FONT, 14),
                                       fill="black")

    def create_guess_box(self):
        """Create a square area containing the previous guess's colour.
            Set to default on creation.
        """
        # Calculate coordinates to center the guess box on the
        # RIGHT HALF of the canvas
        x1 = CANVAS_WIDTH / 2 + (CANVAS_WIDTH / 2 - COLOUR_BOX_WIDTH) / 2
        # 10 pixels for padding from the text
        y1 = ((CANVAS_HEIGHT - COLOUR_BOX_HEIGHT) / 2) + 10
        x2 = x1 + COLOUR_BOX_WIDTH
        y2 = y1 + COLOUR_BOX_HEIGHT
        self.guessBox = self.colour_canvas.create_rectangle(x1, y1, x2, y2,
                                                            fill="#888888",
                                                            outline="",
                                                            width=0)
        # Add centered text above the guess box
        text_x = x1 + COLOUR_BOX_WIDTH / 2
        text_y = y1 - 15 # Place text slightly above the box's top edge
        if text_y < 0: # Ensure text is not drawn off-canvas top edge
            text_y = 15 #Default to 15 pixels from canvas top 
        self.colour_canvas.create_text(text_x, text_y, 
                                        text="Your Guess",
                                        font=(FONT, 14), 
                                        fill="black")

    def create_guess_grid(self):
        """This is where we display the previous guesses and the hints 
            if it's too high or too low
        """
        # initialize the grid array
        self.guessGridStructure = [] # This is the guess grid as a whole
        # guessLineStructure = [] - This is just one line of the grid 
        # (here for clarity).
        # For each guess line there's an indicator row (up or down), 
        # and a row below that contains the guess
        self.guesses = [] # To store references to our Entry widgets
        self.guess_vars = [] # To store their associated StringVars
        # We store 2 parts for each guess - The first is the errorMargin
        # for each colour pair (3 values), then the 2 associated digits  
        # for each colour (ie 6 values). 
        for i in range(MAX_ALLOWED_GUESSES):
            guessLineStructure = []
            #error margin up/down indicators
            for j in range(3):
                labelElement = tk.Label(self, text="")
                labelElement.grid(row=(2*i)+4,  
                                    column=(2*j)+1,  
                                    columnspan=2, 
                                    padx=5, 
                                    pady=2, 
                                    sticky='ew')
                guessLineStructure.append(labelElement)
            #the colour guesses    
            for j in range(HEX_LENGTH):
                entryText = tk.StringVar()
                entryText.set("")
                # Create the Entry widget
                guessElement = tk.Entry(self, 
                                        textvariable=entryText, 
                                        state="disabled", 
                                        width=2, 
                                        font=(FONT, 25))
                guessElement.grid(row=(2*i)+5, 
                                    column=j+1, 
                                    padx=5, 
                                    pady=2, 
                                    sticky='ew')
                # We don't need to save the reference to the actual 
                # Entry, only to the reference of the entryText
                guessLineStructure.append(entryText) 
            self.guessGridStructure.append(guessLineStructure)      

    def return_to_main_menu(self):
        messagebox_reply = messagebox.askokcancel("Return to Main Menu?", 
                                    "Are you sure you want to quit this game?")
        if messagebox_reply: # result is True if Yes, False if Cancel
            self.master.master.show_menu_screen()
        else:
            return # Continue playing   


class MainGameLogic(tk.Frame):
    """
        This controls the game, makes the checks and evaluated the 
        entries, and updates the layout via the layout passed to it.
        It adds a binding to each entry box to monitor for key presses 
        and responds to each accordingly. This way it can auto advance
        and only allow certain keys to be entered.
    """
    def __init__(self, master, layout):
        super().__init__(master, bg="white")
        self.master = master
        self.layout = layout
        self.difficulty = master.difficulty 
        # Get the lowest score in the High Score json for this 
        # difficulty, so we know if, when they have finished, they got a
        # high score or not. 
        # If they did get a high score they will be directed to enter 
        # their name so it will be added to the high score json
        self.lowest_score_for_difficulty = \
                                        self.get_lowest_score_for_difficulty()
        self.score = 255 # maximum decimal value of 0xFF
        self.focus = 0 
        self.guess_count = 0 
        self.game_ended = False 
        self.end_game_choice = 0   
        # This is a list of each submitted guess so far.
        # It contains the previous guess_line_values. 
        # guess_line_values contains the error margin for each hex 
        # colour pair, then each hex digit the player submitted as a 
        # guess                     
        self.list_of_guess_line_values = [] 
        # register the validation command, 
        validate_is_single_character = self.register(self.validate_single_char)
        # We created the entry boxes in the layout, but now we are going
        # to add validation to them, and add bindings to add fine 
        # control over what happens when a key is pressed, and to make 
        # sure the entry is valid ie because of the fine control we can 
        # make sure only valid input is entered
        for i in range(len(self.layout.entry_boxes)): 
            entry_box = self.layout.entry_boxes[i]
            entry_box.config(validate='key', 
                             validatecommand=(validate_is_single_character, 
                                              '%P'))
            # Bind the <KeyRelease> event to our advance_focus function
            # We use <KeyRelease> instead of <KeyPress> because
            # the textvariable will have been updated by the time 
            # KeyRelease fires.
            entry_box.bind("<KeyRelease>", 
                            lambda event, 
                            idx=i: self.advance_focus(event, idx))
            # Bind <BackSpace> or <Delete> to move backward
            entry_box.bind("<BackSpace>", 
                            lambda event, 
                            idx=i: self.regress_focus(event, idx))
            entry_box.bind("<Delete>", 
                            lambda event, 
                            idx=i: self.regress_focus(event, idx))
            # Bind <Return> (Enter button) to submit the entry
            entry_box.bind("<Return>", 
                            lambda event, 
                            idx=i: self.submit_entry(event, idx))
        # Set initial focus to the first entry
        self.layout.entry_boxes[0].focus_set()
        # Define the colour for the target box
        # Makes a random colour hex, eg #26e16b
        self.target_colour = "#%06x" % random.randint(0, 0xFFFFFF) 
        print(self.target_colour) # Helps with cheating ;)
        # We get the RGB values from index 1, because index 0 is hash #
        self.target_red = int(self.target_colour[1:3], 16)
        self.target_green = int(self.target_colour[3:5], 16)
        self.target_blue = int(self.target_colour[5:7], 16)
        self.update_target_box(self.target_colour)

    def update_guess_box(self,colour):
        """Updates the box with the actual colour of the player's latest
           guess colour is a 6 digit hex value 
        """
        self.colour = colour
        self.layout.colour_canvas.itemconfig(self.layout.guessBox, 
                                             fill=self.colour)

    def update_target_box(self,colour):
        """Updates the box with the target colour that the player is 
            trying to guess colour is a 6 digit hex value 
        """
        self.colour = colour
        self.layout.colour_canvas.itemconfig(self.layout.targetBox, 
                                             fill=self.colour)

    def validate_single_char(self, input_text):
        """validation function to ensure only one character is entered
            and that character is a valid hex digit, ie 0-9, a-f
            input_text is a single character
        """
        if (len(input_text) <= 1) and \
                                (re.fullmatch(r"^[a-fA-F0-9]*$", input_text)):
            return True
        else:
            return False

    def advance_focus(self, event, current_idx):
        """Moves the cursor to the next entry box and selects it 
            (so it will overwrite the value already there if the
            player enters a different value) event is the ky pressed 
            event current_idx is an integer value of wheich entry box we
            are currently in
        """
        # The following is a workaround to an issue:
        # Because this is run in a KeyRelease event it is ALSO being run
        # when we press BackSpace or Delete.
        # This means we go back an entry, but then immediately go 
        # forward again, since BOTH events are processed.
        # To stop the entry going forward again we check 
        # "was the key press backspace or delete" and if it was don't do
        # anything.
        keyPressed = event.keysym # get the key that was just pressed
        # Check if the key is one we are monitoring for elsewhere. 
        # If it is, do nothing, to stop double handling
        if keyPressed in {"BackSpace", 
                          "Delete",
                          "Tab", 
                          "Shift_L", 
                          "Shift_R", 
                          "Left"}:
            return
        current_text = self.layout.entry_input_values[current_idx].get()
        # If a single valid character was entered
        if current_text and len(current_text) == 1 and \
                                current_idx < len(self.layout.entry_boxes) - 1:
            # Move focus to the next entry
            self.layout.entry_boxes[current_idx + 1].focus_set()
            # Select any text in the next box for easy overwriting
            self.layout.entry_boxes[current_idx + 1].selection_range(0, tk.END)

    def regress_focus(self, event, current_idx):
        """Moves the cursor to the previous box (if it exists) and 
            selects it (so it will overwrite the value already there if 
            the player enters a different value) 
            event is the key pressed event
            current_idx is an integer value of current entry box
        """
        # If Backspace or Delete was pressed and the entry is empty
        if not self.layout.entry_input_values[current_idx].get() \
                                                        and current_idx > 0:
            # Move focus to the previous entry
            self.layout.entry_boxes[current_idx - 1].focus_set()
            # select the entry (so that it will be over-written)
            self.layout.entry_boxes[current_idx - 1].selection_range(0, tk.END)

    def submit_entry(self, event, current_idx):
        """If the user presses enter we will now attempt to handle the 
            full entry
            event is the key pressed event
            current_idx is an integer value of the current entry box
        """
        # If Enter was clicked first validate the entries so far to make
        # sure each box has a valid entry, then if it has update the 
        # grid, check if the game has finished, if it hasn't clear the 
        # entry boxes
        if (not self.validate_entries()):
            return
        else:
            self.guess_count += 1
            # If everything is ok combine the boxes and check it against 
            # the target colours. 
            guess_red = int(f"{self.layout.entry_boxes[0].get()}" +
                            f"{self.layout.entry_boxes[1].get()}", 16)
            guess_green = int(f"{self.layout.entry_boxes[2].get()}" +
                              f"{self.layout.entry_boxes[3].get()}", 16)
            guess_blue = int(f"{self.layout.entry_boxes[4].get()}" +
                             f"{self.layout.entry_boxes[5].get()}", 16)
            # Calculate the error margins for each colour
            diff_red = guess_red - self.target_red
            diff_green = guess_green - self.target_green
            diff_blue = guess_blue - self.target_blue
            # Give different "hints" based on difficulty selected
            if (self.difficulty == DIFFICULTY_STANDARD):
                error_margin_red = self.error_margin_indicator(diff_red)
                error_margin_green = self.error_margin_indicator(diff_green)
                error_margin_blue = self.error_margin_indicator(diff_blue)
            else: # DIFFICULTY_EXPERT
                error_margin_red = self.get_sign(diff_red)
                error_margin_green = self.get_sign(diff_green)
                error_margin_blue = self.get_sign(diff_blue)
            self.update_score(diff_red,diff_green,diff_blue)
            # Move everything in the answer grid down 1, append the 
            # latest answer to the grid
            self.update_guess_grid(self.layout.entry_boxes, 
                                   error_margin_red, 
                                   error_margin_green, 
                                   error_margin_blue)
            #update their guess colour on the canvas
            guessed_colour = "#"
            for digit in self.layout.entry_boxes:
                guessed_colour = guessed_colour + f"{digit.get()}"
            self.update_guess_box(guessed_colour)   
            # Are all the entries correct? If so, game over. 
            # Put up a congratulations message, does it qualify as a 
            # high score, if so, in the congrats message have an entry 
            # box to enter your name, then save the high scores back
            game_over = False
            if diff_red == 0 and diff_green == 0 and diff_blue == 0:
                #Player won the game
                #Did they get a high score?
                if (self.accuracy > self.lowest_score_for_difficulty):
                    self.master.master.show_enter_high_score_screen(    
                                                                self.accuracy)
                    return
                messagebox_reply = \
                                 messagebox.askretrycancel("Play Again?", 
                                        "You won! Do you want to play again?")
                game_over = True
            elif self.guess_count >=  MAX_ALLOWED_GUESSES:
                #Player lost the game
                messagebox_reply = \
                                messagebox.askretrycancel("Play Again?", 
                                        "You lost! Do you want to play again?")
                game_over = True
            if game_over:
                if messagebox_reply: # result is True if Retry
                    self.master.master.show_game(self.difficulty)
                else:
                    self.master.master.show_menu_screen()
                return
            # If you get here then the game is still going 
            # - clear the entered guesses and put the focus back into 
            # the first box,
            # clear input fields for the next guess
            for var in self.layout.entry_input_values:
                var.set("")
            self.layout.entry_boxes[0].focus_set()
            self.layout.entry_boxes[0].selection_range(0, tk.END)

    def validate_entries(self):
        """Checks to see if there is an enrty in each box 
            (you can't submit an entry only half done!)
        """
        for entry_box in self.layout.entry_input_values:
            content = entry_box.get()
            if not content: 
                return False
        return True    
   
    def update_guess_grid(self, 
                          entry_boxes, 
                          error_margin_red, 
                          error_margin_green, 
                          error_margin_blue):
        """Adds the submitted guess to the previous guesses but adding 
            it in the first position, thus moving every previous guess 
            down
            entry_boxes is a list of references to each guess entry box
            error_margin_red etc is an indicator for how far out the 
             guess was (integer)
        """
        # guess_line_values contains the error margin for each hex 
        # colour pair, then each hex digit the player submitted as a 
        # guess
        guess_line_values = [error_margin_red, 
                             error_margin_green, 
                             error_margin_blue] 
        for hex_digit in entry_boxes:   # Add each hex digit
            guess_line_values.append(hex_digit.get())
        # Insert the latest guess into the first position of the list 
        # that contains the previous guesses
        self.list_of_guess_line_values.insert(0, guess_line_values) 
        # Add in the error margin hints and the guessed hex digits
        for i in range(min(len(self.list_of_guess_line_values), 
                                                        MAX_ALLOWED_GUESSES)):
            guessLineStructure = self.layout.guessGridStructure[i]
            # up/down indicators
            for j in range(3):
                guessLineStructure[j]['text'] = \
                self.error_margin_symbols(self.list_of_guess_line_values[i][j])
            for j in range(HEX_LENGTH):
                guessLineStructure[j+3].set(
                                        self.list_of_guess_line_values[i][j+3])   
                  
    def error_margin_indicator(self, number):
        """Calculates the "error" in the player's guess to give a hint 
            as to how far out their guess is. We do this my taking the 
            log of the absolte difference between the guessed value and 
            the target value.
            This can be adjusted by changeing the base log value, 
            contained in ERR_INDICATOR_DIFFICULTY,
            ie log 2 is easiest , log 3+ will give a wider range. 
            ERR_INDICATOR_DIFFICULTY is the base log value. 
            It should be set as an integer from 2+
            number is an integer, indicating error
        """
        # Calculates the logarithm of the absolute of a number and 
        # rounds it up to the next integer.
        # If the original number is negative it then returns this value 
        # as a negative. 
        # Need to add 1, since if you are out by 1 then log will return 
        # zero, but the guess is still not quite correct
        if number == 0:
            return 0
        elif number < 0:
            margin = -math.ceil(math.log(-(number),ERR_INDICATOR_DIFFICULTY))-1
            if margin < -1:
                margin = margin + 1
        else:
            margin = math.ceil(math.log(number, ERR_INDICATOR_DIFFICULTY)) + 1
            if margin > 1:
                margin = margin - 1
        return margin

    def error_margin_symbols(self, number):
        """ Draws the arrows left or right as a hint to the player how 
            far out they are
            number is an integer, indicating error
        """
        symbol = ""    
        if number == 0:
            return "O"
        elif number < 0:
            for i in range(abs(number)):
                symbol = symbol + ">"
        else:
            for i in range(number):
                symbol = symbol + "<"
        return symbol    

    def update_score(self, 
                     error_margin_red, 
                     error_margin_green, 
                     error_margin_blue):
        """The score is not displayed, but is used to determin the high 
            score charts. Most weight is given to the initial guesses, 
            since each subsequent guess is easier.
            error_margin_xxx is an integer value for actual difference 
             between target and guess
        """
        average_error = (abs(error_margin_red) + 
                         abs(error_margin_green) + 
                         abs(error_margin_blue)) / 3
        self.score = ((255 - average_error)/255) * self.score 
        self.accuracy = round((int(self.score)/255)*100, 2)

    def get_sign(self, value):
        """ Is the value less than, great than, or equal to zero
            value is an integer
        """
        if value > 0:
            return 1
        elif value < 0:
            return -1
        else:
            return 0    

    def get_lowest_score_for_difficulty(self):
        """Find the lowest score for the difficult - used to determine 
            whether a winning game is good enough to make the charts
        """
        # If the high score file has an error (eg not found etc) then the
        # lowest score is zero
        if not os.path.exists(HIGH_SCORE_FILE):
            return 0
        try:
            with open(HIGH_SCORE_FILE, "r") as high_score_file:
                high_score_data = json.load(high_score_file)
        except json.JSONDecodeError:
            return 0
        except IOError as e:
            return 0
        if self.difficulty not in high_score_data:
            return 0
        if len(high_score_data[self.difficulty]) < 3:
            return 0
        return high_score_data[self.difficulty] \
                              [len(high_score_data[self.difficulty])-1] \
                              ["score"]


class PlayGame(tk.Frame):
    """The actual game!
        We use different classes for the layout and logic, 
        hence we need this class to bring them together.   
    """
    def __init__(self, master):
        super().__init__(master, bg="white")
        self.master = master
        self.difficulty = master.difficulty 
        # Stretch the grid to cover the window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # Initialise the layout
        self.layout = MainGameLayout(self)
        self.layout.grid(row=0, column=0, sticky="nsew")  
        # Pass the layout to the game logic
        self.logic = MainGameLogic(self, self.layout)


class HelpScreen(tk.Frame):
    """Display text file containing the help
        Due to limitations with TKinter we only display very simple text
         within the game window. 
        We display more complex help text as html in the browser 
        (since it's not possible using TKinter)
    """
    def __init__(self, master):
        super().__init__(master, bg="white")
        self.master = master # reference to the main application
        # configure grid for centering buttons within this frame
        self.grid_rowconfigure(0, weight=0) 
        self.grid_rowconfigure(1, weight=1) 
        self.grid_columnconfigure(0, weight=1) 
        back_button = tk.Button(self, 
                                text="Back",
                                font=(FONT, 14), 
                                bg=DEFAULT_BUTTON_COLOUR, 
                                fg="black",
                                activebackground=DEFAULT_ACTIVE_BUTTON_COLOUR, 
                                activeforeground="white",
                                width=15, 
                                relief="raised", 
                                bd=2,
                                command=self.master.show_menu_screen)
        back_button.grid(row=4, column=0, pady=(10, 20), sticky="n")
        self.text_area = scrolledtext.ScrolledText(self,
                                wrap=tk.WORD,
                                font=(FONT, 12),
                                padx=10,       
                                pady=10)
        self.text_area.grid(
                                row=1,        
                                column=0,      
                                sticky="nsew")
        self.configure_tags()               
        self.load_and_display_text(HELP_TEXT_FILE)
        # Make the text area read-only after loading
        self.text_area.config(state=tk.DISABLED)
        more_information_button = tk.Button(self, 
                text="More Information",
                command=lambda: self.open_html_in_browser(HTML_FILE_TO_OPEN),
                font=(FONT, 14), 
                bg=DEFAULT_BUTTON_COLOUR, 
                fg="black",
                activebackground=DEFAULT_ACTIVE_BUTTON_COLOUR, 
                activeforeground="white",
                width=15, 
                relief="raised", 
                bd=2) 
        more_information_button.grid(row=2, 
                                     column=0,  
                                     pady=(10, 20), 
                                     sticky="s",)

    def configure_tags(self):
        """Define the tags we can use. At the moment it is just Heading 
            tag, but we could add more later.
        """
        # Heading tag
        self.text_area.tag_config(TAG_HEADING, 
                                  font=(FONT, 16, "bold"), 
                                  foreground="navy", 
                                  justify="center",
                                  spacing2=1, # Space between lines
                                  spacing3=1)
 
    def load_and_display_text(self, file_name):
        """Go through each of the lines in the help.txt file, and 
           determine if they have been tagged to be formatted in some 
           way. If they have, apply the tag to the text. If not, just 
           display the text as is.
           file_name is text, preferable from constants
        """
        # Use try, because there is a lot that can go wrong - the file 
        # doesn't exist or contains garbage.
        # By using try, if it fails for some reason, the app can put up 
        # an error message instead of crashing the program
        try:
            # OPen the file read only
            with open(file_name, "r", encoding="utf-8") as help_file:
                help_lines = help_file.readlines()
            for help_line in help_lines:
                # Remove trailing new line
                help_line = help_line.strip('\n')
                if help_line.startswith("#") and help_line.endswith("#"):
                    #Take away the markup
                    text = help_line.strip("#").strip() + "\n\n"    
                    self.text_area.insert(tk.END, text, (TAG_HEADING,))  
                    continue 
                # There was no markup so just add the line 
                self.text_area.insert(tk.END, help_line) 
                # Add newline after each processed line
                self.text_area.insert(tk.END, "\n") 
        # If the file doesn't exist, or there is some other error, 
        except FileNotFoundError:
            messagebox.showerror("Error", f"File not found: {file_name}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def open_html_in_browser(self, html_file_name):
        """
            Opens the specified HTML file in the user's default web 
            browser. Due to limitations of TKinter we can't display html
            files which are far richer and can container images etc. 
            As an alternative to the simple help we display IN the app 
            we offer more help in the browser window (as html)
            html_file_name is text, preferably from constants
        """
        html_help_file_dir = os.path.dirname(__file__) 
        html_file_path = os.path.join(html_help_file_dir, html_file_name) 
        # Check if the HTML file actually exists
        if not os.path.exists(html_file_path):
            messagebox.showerror("File Not Found",
                      f"The HTML help file '{html_file_name}'" 
                      f" was not found at:\n{html_file_path}\n"
                      " Please ensure it's in the same directory as this app.")
            return
        try: 
            # Use 'file:///' prefix for local files 
            webbrowser.open(f"file:///{html_file_path}")
        except Exception as e: #If it didn't work display the error why
            messagebox.showerror("Browser Error",
                                f"Could not open the HTML page in your"
                                f" default browser.\nError: {e}")
            print(f"Error opening HTML file: {e}")


class HighScoreScreen(tk.Frame):
    """Display the high scores"""
    def __init__(self, master):
        super().__init__(master, bg="white")
        self.master = master # reference to the main application
        # configure grid for centering buttons within this frame
        self.grid_rowconfigure(0, weight=0) 
        self.grid_rowconfigure(1, weight=1) 
        self.grid_columnconfigure(0, weight=1) 
        back_button = tk.Button(self, text="Back",
                                 font=(FONT, 14), 
                                 bg=DEFAULT_BUTTON_COLOUR, 
                                 fg="black",
                                 activebackground=DEFAULT_ACTIVE_BUTTON_COLOUR, 
                                 activeforeground="white",
                                 width=15, relief="raised", 
                                 bd=2,
                                 command=self.master.show_menu_screen)
        back_button.grid(row=4, column=0, pady=(10, 20), sticky="n")
        # frame to hold difficulty buttons for better layout
        self.scores_frame = tk.Frame(self, bg="white")
        self.scores_frame.grid(row=1, column=0, pady=20)
        self.load_and_display_scores()

    def load_and_display_scores(self):
        """Reads the JSON High Score file and updates the GUI with the 
           score data.
        """
        if not os.path.exists(HIGH_SCORE_FILE):
            messagebox.showerror("High Score File Not Found", 
                               f"The file '{HIGH_SCORE_FILE}' does not exist.")
            return
        #We use try because a lot can go wrong, (file moved etc)
        try:
            with open(HIGH_SCORE_FILE, "r") as high_score_file:
                high_score_data = json.load(high_score_file)
        except json.JSONDecodeError:
            messagebox.showerror("JSON Error", 
                                 "Could not decode High Score JSON from file.")
            return
        except IOError as e:
            messagebox.showerror("File Error", 
                   f"An error occurred while reading the High Score file: {e}")
            return
        # Start grid layout from the top
        row_counter = 1
        for difficulty, players in high_score_data.items():
            # Create a label for the difficulty level spanning two columns
            difficulty_label = tk.Label(self.scores_frame, 
                                        text=f"{difficulty.capitalize()} ", 
                                        font=(FONT, 26, "bold"), 
                                        bg="white")
            difficulty_label.grid(row=row_counter, 
                                    column=0, 
                                    columnspan=2, 
                                    pady=(15, 5))
            row_counter += 1
            # Create header labels for the columns
            player_header = tk.Label(self.scores_frame, 
                                     text="Player Name", 
                                     font=(FONT, 20, "bold"), 
                                     bg="white")
            player_header.grid(row=row_counter, 
                               column=0, 
                               padx=10, 
                               pady=2, 
                               sticky="w")
            score_header = tk.Label(self.scores_frame, 
                                    text="Score", 
                                    font=(FONT, 20, "bold"), 
                                    bg="white")
            score_header.grid(row=row_counter, 
                              column=1, 
                              padx=10, 
                              pady=2, 
                              sticky="w")
            row_counter += 1
            # Display the scores for each player
            for player in players:
                player_name_label = tk.Label(self.scores_frame, 
                                            text=player["player_name"], 
                                            font=(FONT, 18, "bold"), 
                                            bg="white")
                player_name_label.grid(row=row_counter, 
                                       column=0, 
                                       padx=10, 
                                       pady=2, 
                                       sticky="w")
                score_label = tk.Label(self.scores_frame, 
                                        text=player["score"], 
                                        font=(FONT, 18, "bold"), 
                                        bg="white")
                score_label.grid(row=row_counter, 
                                 column=1, 
                                 padx=10, 
                                 pady=2, 
                                 sticky="w")
                row_counter += 1


class MenuScreen(tk.Frame):
    """initial screen with option for new game"""
    def __init__(self, master):
        super().__init__(master, bg="white")
        self.master = master # reference to the main application
        # configure grid for centering buttons within this frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0) # for buttons
        self.grid_rowconfigure(2, weight=0) # for buttons
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # title Label
        self.photo = PhotoImage(file="hexaguessa.png")
        # resize to 1/4 of original image size
        self.photo = self.photo.subsample(4)
        title_label = tk.Label(self, image=self.photo, bg="white")
        title_label.grid(row=0, column=0, pady=(10, 20), sticky="ns") 
        new_game_button = tk.Button(self, text="New Game",
                                    font=(FONT, 20), 
                                    bg="darkolivegreen3", 
                                    fg="black",
                                    activebackground="darkolivegreen4", 
                                    activeforeground="white",
                                    width=12, 
                                    height=2, 
                                    relief="raised", 
                                    bd=4,
                                    command=self.master.show_new_game_screen)
        new_game_button.grid(row=1, column=0, pady=10)
        highscores_button = tk.Button(self, 
                                    text="Leaderboard",
                                    font=(FONT, 20), 
                                    bg="goldenrod3", 
                                    fg="black",
                                    activebackground="goldenrod4", 
                                    activeforeground="white",
                                    width=12, 
                                    height=1, 
                                    relief="raised", 
                                    bd=4,
                                    command=self.master.show_high_score_screen)
        highscores_button.grid(row=2, column=0, pady=10, sticky="n")
        help_button = tk.Button(self, 
                                    text="Help",
                                    font=(FONT, 20), 
                                    bg="steelblue3", 
                                    fg="black",
                                    activebackground="steelblue4", 
                                    activeforeground="white",
                                    width=12, 
                                    height=1, 
                                    relief="raised", 
                                    bd=4,
                                    command=self.master.show_help_screen)
        help_button.grid(row=3, column=0, pady=10, sticky="n")
        exit_game_button = tk.Button(self, 
                                    text="Exit",
                                    font=(FONT, 20), 
                                    bg="coral1", 
                                    fg="black",
                                    activebackground="coral3", 
                                    activeforeground="white",
                                    width=12, 
                                    height=1, 
                                    relief="raised", 
                                    bd=4,
                                    command=self.master.exit_game)
        exit_game_button.grid(row=4, column=0, pady=10, sticky="n")


class NewGameScreen(tk.Frame):
    """for entering difficulty"""
    def __init__(self, master):
        super().__init__(master, bg="white")
        self.master = master
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=0) # difficulty buttons
        self.grid_rowconfigure(4, weight=0) # back button
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # frame to hold difficulty buttons for better layout
        difficulty_buttons_frame = tk.Frame(self, bg="white")
        difficulty_buttons_frame.grid(row=3, column=0, pady=20)
        standard_button = tk.Button(difficulty_buttons_frame, 
                    text=DIFFICULTY_STANDARD,
                    font=(FONT, 16), 
                    bg=DEFAULT_BUTTON_COLOUR, 
                    fg="black",
                    activebackground=DEFAULT_ACTIVE_BUTTON_COLOUR, 
                    activeforeground="white",
                    width=10, 
                    height=1, 
                    relief="raised", 
                    bd=3,
                    command=lambda: self.master.show_game(DIFFICULTY_STANDARD))
        standard_button.pack(side=tk.LEFT, padx=10)
        expert_button = tk.Button(difficulty_buttons_frame, 
                    text=DIFFICULTY_EXPERT,
                    font=(FONT, 16), 
                    bg=DEFAULT_BUTTON_COLOUR, 
                    fg="black",
                    activebackground=DEFAULT_ACTIVE_BUTTON_COLOUR, 
                    activeforeground="white",
                    width=10, 
                    height=1, 
                    relief="raised", 
                    bd=3,
                    command=lambda: self.master.show_game(DIFFICULTY_EXPERT))
        expert_button.pack(side=tk.LEFT, padx=10)
        back_button = tk.Button(self, 
                                text="Back",
                                font=(FONT, 14), 
                                bg=DEFAULT_BUTTON_COLOUR, 
                                fg="black",
                                activebackground=DEFAULT_ACTIVE_BUTTON_COLOUR, 
                                activeforeground="white",
                                width=15, 
                                relief="raised", 
                                bd=2,
                                command=self.master.show_menu_screen)
        back_button.grid(row=4, column=0, pady=(10, 20), sticky="n")


class EnterHighScoreScreen(tk.Frame):
    """Enter a new high score
        This screen is ONLY entered from PlayGame, the player CANNOT 
        navigate here
    """
    def __init__(self, master,new_score):
        super().__init__(master, bg="white")
        self.master = master # reference to the main application
        self.difficulty = master.difficulty 
        self.new_score = new_score
        # to center everything
        central_frame = tk.Frame(self, bg="white")
        central_frame.pack(expand=True, padx=20, pady=20)
        central_frame.grid_columnconfigure(0, weight=1)
        for i in range(6):
            central_frame.grid_rowconfigure(i, weight=1)
        high_score_label = tk.Label(central_frame, 
                                    text="You got a High Score!",
                                    font=(FONT, 20), 
                                    bg="white")
        high_score_label.grid(row=0, column=0, pady=(0, 20), sticky='s')
        difficulty_label = tk.Label(central_frame, 
                            text=f"Difficulty: {self.difficulty.capitalize()}",
                            font=(FONT, 15), 
                            bg="white")
        difficulty_label.grid(row=1, column=0, pady=5, sticky='n')
        score_label = tk.Label(central_frame, 
                               text=f"Score: {self.new_score}",
                               font=(FONT, 15), 
                               bg="white")
        score_label.grid(row=2, column=0, pady=(5, 20), sticky='n')
        enter_name_label = tk.Label(central_frame, 
                                    text="Enter name:",
                                    font=(FONT, 15), 
                                    bg="white")
        enter_name_label.grid(row=3, column=0, pady=5, sticky='n')
        self.player_name_text = tk.StringVar()
        self.player_name_text.set("")
        validate_player_name  = self.register(self.validate_player_name)
        player_name = tk.Entry(central_frame, 
                               textvariable=self.player_name_text,
                               width=20, 
                               font=(FONT, 20), 
                               justify='center')
        player_name.config(validate='key', 
                           validatecommand=(validate_player_name, 
                                            '%P'))
        player_name.grid(row=4, column=0, pady=10, ipady=5, sticky='n')
        player_name.focus_set()
        submit_button = tk.Button(central_frame, 
                                text="Submit",
                                font=(FONT, 14), 
                                bg=DEFAULT_BUTTON_COLOUR, fg="black",
                                activebackground=DEFAULT_ACTIVE_BUTTON_COLOUR, 
                                activeforeground="white",
                                width=15, 
                                relief="raised", 
                                bd=2,
                                command=self.update_scores)
        submit_button.grid(row=5, column=0, pady=(20, 0), sticky="n")

    def read_scores(self,high_score_filename):
        """Load scores from the high score JSON file
            high_score_filename is text, preferably from constants
        """
        try:
            with open(high_score_filename, 'r') as high_score_file:
                return json.load(high_score_file)
        except FileNotFoundError:
            # If the file doesn't exist, return a default structure.
            return {
                DIFFICULTY_STANDARD: [],
                DIFFICULTY_EXPERT: []
            }
        except json.JSONDecodeError:
            return {
                DIFFICULTY_STANDARD: [],
                DIFFICULTY_EXPERT: []
            }
   
    def update_scores(self):
        """Update the JSON file with new player's data."""
        all_scores = self.read_scores(HIGH_SCORE_FILE)
        # Create a dictionary for the new score entry
        new_score_entry = {
            'player_name': self.player_name_text.get(),
            'score': self.new_score
        }
        # Check if the difficulty level exists in the list of levels
        if self.difficulty not in all_scores:
            all_scores[self.difficulty] = [new_score_entry]
        else:  # The difficult exists so we append out score 
            all_scores[self.difficulty].append(new_score_entry)
            # Sort the scores list (for this difficulty) by score
            all_scores[self.difficulty] = sorted(all_scores[self.difficulty], 
                                        reverse=True, key=lambda x: x['score'])
            # Keep all but 3 scores for this difficulty
            all_scores[self.difficulty] = all_scores[self.difficulty][:3]
            # Save back to JSON file
        with open(HIGH_SCORE_FILE, 'w') as file:
            json.dump(all_scores, file, indent=4)
        self.master.show_high_score_screen()  

    def validate_player_name(self, player_name):
        # Check if the player_name contains only alphabetic characters
        # Regular expression to allow letters, numbers, spaces, and 
        # underscores.
        # The pattern r'^[a-zA-Z0-9_ ]*$' checks for:
        # ^ : start of the string
        # [a-zA-Z0-9_ ] : any character that is a letter 
        # (upper or lowercase), a number, an underscore, or a space
        # * : zero or more of the preceding characters
        # $ : end of the string
        if re.match(r'^[a-zA-Z0-9_ ]*$', player_name):
            # Check if the length is too long
            max_length = 20  
            if len(player_name) <= max_length:
                return True  
        return False  


# run game
if __name__ == "__main__":
    app = HexGame()
    app.mainloop()