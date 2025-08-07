#=====================================
# Project Name: HexaGuessa
# Author: Jessica Bell
# Version: 1.0
# Date: 01/08/25
# Description: A hex code guessing game
#======================================


import tkinter as tk
import random
from tkinter import *
from tkinter import messagebox, scrolledtext
import re #regular expression module
import math
import json
import os
import webbrowser


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

# Files
HIGH_SCORE_FILE = "highscores.json"
HTML_FILE_TO_OPEN = "help.html"

#Difficulty levels for the game
DIFFICULTY_STANDARD = 1
DIFFICULTY_HARD = 2




# main
class HexGame(tk.Tk):
    """
    This is the main class for the game. It controls which windows should be displayed.
    """
    def __init__(self):
        """ Initalise """    
        super().__init__()
        self.title("Hex-a-Guess-a")
        self.geometry("500x950")
        self.minsize(500,950)

        self.difficulty = DIFFICULTY_STANDARD # Default difficulty level

        # configure grid for centering content
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.current_frame = None # to keep track of the currently displayed frame

        self.show_menu_screen() # show main menu


    def switch_frame(self, frame_class):
        """removes current frame and switches to new"""
        if self.current_frame:
            self.current_frame.destroy() # remove  old frame
        new_frame = frame_class(self) # make new frame, passing self (the hexgame instance)
        self.current_frame = new_frame
        self.current_frame.grid(row=0, column=0, sticky="nsew") # make new frame


    def show_menu_screen(self):
        """main menu"""
        self.switch_frame(MenuScreen)


    def show_new_game_screen(self):
        """new game options screen"""
        self.switch_frame(NewGameScreen)

    def exit_game(self):
        self.destroy()


    def show_game(self, difficulty):
        """standard game screen"""
        self.difficulty = difficulty
        self.switch_frame(MainGameGUI)

    def show_help_screen(self):
        """help screen"""
        self.switch_frame(HelpScreen)

    def show_high_score_screen(self):
        """display high scores screen"""
        self.switch_frame(HighScoreScreen)  




class MainGameGUI(tk.Frame):
    """
    MainGameGUI constructs and controls the GUI for the main part of the game where it is played.
    The GUI monitors for key presses and responds to each accordingly. This way it can auto advance
    and only allow certain keys to be entered.
    """
    # Initialise the GUI layout, 
    def __init__(self, master):
        """ When MainGameGUI is started this will set everything up, and start monitoring for key presses """
        super().__init__(master, bg="white")
        self.master = master
        self.difficulty = master.difficulty # Set the difficulty level for the game

        self.score = 255
        self.focus = 0 # We focus on the first entry when starting the game
        self.guess_count = 0 # At the beginning of the game we have had zero guesses

        self.game_ended = False # At the beginning of the game the game is not ended
        self.end_game_choice = 0 # holds the player's choice at the end of the game. At the beginning of the game the player has not made a choice, so set to zero

        self.list_of_guess_line_values = [] # This is a list of each submitted guess so far. It contains the previous guess_line_values. 
                                            # guess_line_values contains the error margin for each hex colour pair, then each hex digit the player submitted as a guess

        ###### The main layout for the grid containing places for the guesses to to placed once entered ######
        # Columns:
        # The first column is space from the left edge of the window to the left of the grid

        # Define the layout for each column in the grid
        for i in range(MAX_ALLOWED_GUESSES - 1):
            self.grid_columnconfigure(i, weight=0) # for padding at bottom

        # The last column is space from the right of the grid to the right edge of the window
        self.grid_columnconfigure(0, weight=1)
        for i in range(1, HEX_LENGTH + 1):
            self.grid_columnconfigure(i, weight=0)
        self.grid_columnconfigure(8, weight=1)# for padding at right
    
        self.create_canvas() 
        self.create_target_box()
        self.create_guess_box()
        self.create_guess_grid()

         # register the validation command
        # the %P is a special Tkinter placeholder that represents the value of the entry
        # if the edit is allowed.
        vcmd = self.register(self.validate_single_char)

        self.entry_boxes = [] # To store references to our Entry widgets
        self.entry_input_values = [] # To store their associated StringVars
        for i in range(HEX_LENGTH):
            # Create a StringVar for each entry
            var = tk.StringVar()
            self.entry_input_values.append(var)

            # Create the Entry widget
            # the validate='key' means validation will occur on every key press.
            # the validatecommand is the function to call for validation.
            entry = tk.Entry(self, textvariable=var, validate='key', validatecommand=(vcmd, '%P'), width=2, font=("Arial Rounded MT Bold", 25))
            entry.grid(row=3, column=i+1, padx=5, pady=2, sticky='ew')
            self.entry_boxes.append(entry)

            # Bind the <KeyRelease> event to our advance_focus function
            # <KeyRelease> is generally preferred over <KeyPress> because
            # the textvariable will have been updated by the time KeyRelease fires.
            entry.bind("<KeyRelease>", lambda event, idx=i: self.advance_focus(event, idx))

            # Bind <BackSpace> or <Delete> to move backward
            entry.bind("<BackSpace>", lambda event, idx=i: self.regress_focus(event, idx))
            entry.bind("<Delete>", lambda event, idx=i: self.regress_focus(event, idx))
            # Bind <Return> (Enter button) to submit the entry
            entry.bind("<Return>", lambda event, idx=i: self.submit_entry(event, idx))

        # main manu button
        main_menu_button = tk.Button(self, text="Main Menu",
                                 font=("Arial Rounded MT Bold", 14), bg="light blue", fg="black",
                                 activebackground="dark blue", activeforeground="white",
                                 width=15, relief="flat", bd=2,
                                 command=self.master.show_menu_screen)
        main_menu_button.grid(row=(MAX_ALLOWED_GUESSES * 2) + 5, column=0, columnspan=HEX_LENGTH+1, pady=(10, 20), sticky="n")


        # Set initial focus to the first entry
        self.entry_boxes[0].focus_set()


    def create_canvas(self):
        """ Creates the area that contains squares containing the squares of the target colour and the previous guess's colour """
        self.colour_canvas = tk.Canvas(self, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white", highlightbackground="black", highlightthickness=2)

        # Position the canvas with a blank column to the left in order to centre correctly with the guessed grid
        self.colour_canvas.grid(row=0, column=1, columnspan=HEX_LENGTH, padx=5, pady=10, sticky='w') 


    def create_target_box(self):
        """ Create a square area containing the actual target colour """
        # define the color for the box
        self.target_colour = "#%06x" % random.randint(0, 0xFFFFFF)
        print(self.target_colour)
        #We get the RGB values from index 1, because index 0 is hash #
        self.targetRed = int(self.target_colour[1:3], 16)
        self.targetGreen = int(self.target_colour[3:5], 16)
        self.targetBlue = int(self.target_colour[5:7], 16)

        # draw a rectangle (the "box") on the canvas
        # coordinates are (x1, y1, x2, y2) where (x1, y1) is the top-left corner
        # and (x2, y2) is the bottom-right corner
        # The 'fill' option sets the solid color
        # The 'outline' option sets the border color
          
        # Calculate coordinates to center the target box on the LEFT HALF of the canvas
        x1 = (CANVAS_WIDTH / 2 - COLOUR_BOX_WIDTH) / 2
        y1 = ((CANVAS_HEIGHT - COLOUR_BOX_HEIGHT) / 2)+10
        x2 = x1 + COLOUR_BOX_WIDTH
        y2 = y1 + COLOUR_BOX_HEIGHT

        self.targetBox = self.colour_canvas.create_rectangle(x1, y1, x2, y2, fill=self.target_colour, outline="", width=0)

        # Add centered text above the target box
        text_x = x1 + COLOUR_BOX_WIDTH / 2
        text_y = y1 - 15 # Place text slightly above the box's top edge
        if text_y < 0: # Ensure text is not drawn off-canvas top edge
            text_y = 15 # Default to 15 pixels from canvas top if it would go off

        self.colour_canvas.create_text(text_x, text_y, text="Target Colour",
                                      font=("Arial Rounded MT Bold", 14), fill="black")


    def create_guess_box(self):
        """ Create a square area containing the previous guess's colour. Set to default on creation. """

        # draw a rectangle (the "box") on the canvas.
        # the coordinates are (x1, y1, x2, y2) where (x1, y1) is the top-left corner
        # and (x2, y2) is the bottom-right corner.
        # the 'fill' option sets the solid color.
        # the 'outline' option sets the border color.
        
        # Calculate coordinates to center the guess box on the RIGHT HALF of the canvas
        x1 = CANVAS_WIDTH / 2 + (CANVAS_WIDTH / 2 - COLOUR_BOX_WIDTH) / 2
        y1 = ((CANVAS_HEIGHT - COLOUR_BOX_HEIGHT) / 2) + 10 # 10 pixels for padding from the text
        x2 = x1 + COLOUR_BOX_WIDTH
        y2 = y1 + COLOUR_BOX_HEIGHT
        
        self.guessBox = self.colour_canvas.create_rectangle(x1, y1, x2, y2, fill=DEFAULT_GUESS_COLOUR, outline="", width=0)     

        # Add centered text above the guess box
        text_x = x1 + COLOUR_BOX_WIDTH / 2
        text_y = y1 - 15 # Place text slightly above the box's top edge
        if text_y < 0: # Ensure text is not drawn off-canvas top edge
            text_y = 15 # Default to 15 pixels from canvas top if it would go off
        self.colour_canvas.create_text(text_x, text_y, text="Your Guess",
                                      font=("Arial Rounded MT Bold", 14), fill="black")


    def update_guess_box(self):
        # generate a random hex color code
        colour = "#%06x" % random.randint(0, 0xFFFFFF)
        self.colour_canvas.itemconfig(self.guessBox, fill=colour)


    def validate_single_char(self, input_text):
        """validation function to ensure only one character is entered"""
        if (len(input_text) <= 1) and (re.fullmatch(r"^[a-fA-F0-9]*$", input_text)):
            return True
        else:
            return False


    def get_input(self):
        """function to retrieve the single character entered"""
        char = self.r1Guess.get()
        print(f"You entered: {char}")


    def advance_focus(self, event, current_idx):
        """Moves the cursor to the next entry box"""
        # The following is a workaround to an issue:
        # Because this is run in a KeyRelease event it is ALSO being run when we press BackSpace or Delete
        # This means we go back an entry, but then immediately go forward again, since BOTH events are processed
        # To stop the entry going forward again we check "was the key press backspace or delete" 
        # and if it was don't do anything
        # There was also the same problem with Tab (jumping 2 places to the right, once for the Tab key pressed, and then again when KeyRelease)
        # The same problem with Shift_L or Shift_R pressed with Tab (to move to the previous box). It would move to the left on shift-tab, but then
        # immediately jump to the right again on KeyRelease. Also same issue with left arrow
        keyPressed = event.keysym # get the key that was just pressed
        print(keyPressed)
        # Check if the key is Backspace or Delete
        if keyPressed == "BackSpace" or keyPressed == "Delete" or keyPressed == "Tab" or keyPressed == "Shift_L" or keyPressed == "Shift_R" or keyPressed == "Left":
            # If it's one of these keys, do nothing and exit the function
            return


        # Get the current text in the entry
        current_text = self.entry_input_values[current_idx].get()

        # If a character was entered (and it's not empty after deletion/backspace)
        # and it's a single character (ensures we don't advance on second char in same box if width > 1)
        # and we are not on the last entry
        if current_text and len(current_text) == 1 and current_idx < len(self.entry_boxes) - 1:
            # Move focus to the next entry
            self.entry_boxes[current_idx + 1].focus_set()
            # Select the text in the next box for easy overwriting
            self.entry_boxes[current_idx + 1].selection_range(0, tk.END)


    def regress_focus(self, event, current_idx):
        # If Backspace or Delete was pressed and the entry is empty (or about to become empty)
        if not self.entry_input_values[current_idx].get() and current_idx > 0:
            # Move focus to the previous entry
            self.entry_boxes[current_idx - 1].focus_set()
            # select the entry (so that it will be over-written)
            self.entry_boxes[current_idx - 1].selection_range(0, tk.END)


    def submit_entry(self, event, current_idx):
        # If Enter was clicked first validate the entries so far to make sure each box has a valid entry,
        #  then if it has update the grid, check if the game has finished, if it hasn't clear the entry boxes
        #check if entries are already disabled
        if self.entry_boxes[0].cget("state") == "disabled":
            return
        #Validate entries are all full
        if (not self.validate_entries()):
            print("Entries are invalid")
            return
        else:
            print("Entries are valid")
            #adding guess number
            self.guess_count += 1
            #If everything is ok combine the boxes and check it against the target colours. 
            guessRed = int(f"{self.entry_boxes[0].get()}{self.entry_boxes[1].get()}", 16)
            guessGreen = int(f"{self.entry_boxes[2].get()}{self.entry_boxes[3].get()}", 16)
            guessBlue = int(f"{self.entry_boxes[4].get()}{self.entry_boxes[5].get()}", 16)
           
            #Calculate the error margins for each colour
            differenceRed = guessRed - self.targetRed
            differenceGreen = guessGreen - self.targetGreen
            differenceBlue = guessBlue - self.targetBlue

            if (self.difficulty == DIFFICULTY_STANDARD):
                errorMarginRed = self.error_margin_indicator(differenceRed)
                errorMarginGreen = self.error_margin_indicator(differenceGreen)
                errorMarginBlue = self.error_margin_indicator(differenceBlue)
            else: # DIFFICULTY_HARD
                errorMarginRed = self.get_sign(differenceRed)
                errorMarginGreen = self.get_sign(differenceGreen)
                errorMarginBlue = self.get_sign(differenceBlue)

            self.update_score(differenceRed,differenceGreen,differenceBlue)

            #Move everything in the answer grid down 1, append the latest answer to the grid
            self.update_guess_grid(self.entry_boxes, errorMarginRed, errorMarginGreen, errorMarginBlue)

            #update their guess colour on the canvas
            colour = "#%06x" % int(f"{self.entry_boxes[0].get()}{self.entry_boxes[1].get()}{self.entry_boxes[2].get()}{self.entry_boxes[3].get()}{self.entry_boxes[4].get()}{self.entry_boxes[5].get()}", 16)
            self.colour_canvas.itemconfig(self.guessBox, fill=colour)

            #track if game is ongoing
            game_ended = False

            # Are all the entries correct? If so, game over. Put up a congratulations message, does it qualify as a high score, if so, 
            # in the congrats message have an entry box to enter your name, then save the high scores back
            game_over = FALSE
            if differenceRed == 0 and differenceGreen == 0 and differenceBlue == 0:
                #Player won the game
                messagebox_reply = messagebox.askretrycancel("Play Again?", "You won! Do you want to play again?")
                game_over = TRUE
            elif self.guess_count >=  MAX_ALLOWED_GUESSES:
                #Player lost the game
                messagebox_reply = messagebox.askretrycancel("Play Again?", "You lost! Do you want to play again?")
                game_over = TRUE
            if game_over:
                if messagebox_reply: # result is True if Retry, False if Cancel
                    self.master.show_standard_game()
                else:
                    self.master.show_menu_screen()
                return
            
            #If you get here then the game is still going - clear the entered guesses and put the focus back into the first box
            # clear input fields for the next guess
            for var in self.entry_input_values:
                    var.set("")
            #Set focus back to the first entry box
            self.entry_boxes[0].focus_set()
            #Select all for easy overwriting
            self.entry_boxes[0].selection_range(0, tk.END)


    def validate_entries(self):
        for var in self.entry_input_values:
            content = var.get()
            if not content:
                return False
        return True    
       

    def create_guess_grid(self):
        #initialize the grid array
        self.guessGridStructure = []
        guessLineStructure = []
        #For each guess line there's an indicator row (up or down), and a row below that contains the guess
        self.guesses = [] # To store references to our Entry widgets
        self.guess_vars = [] # To store their associated StringVars

        # We store 3 tuplets for each guess - The first is the errorMargin for the guess, then the 2 associated digits for each colour. 
        for i in range(MAX_ALLOWED_GUESSES):
            guessLineStructure = []
            #up/down indicators
            for j in range(3):
                labelElement = tk.Label(self, text="")
                labelElement.grid(row=(2*i)+4, column=(2*j)+1,  columnspan=2, padx=5, pady=2, sticky='ew')
                guessLineStructure.append(labelElement)
            for j in range(HEX_LENGTH):
                # Create a StringVar for each entry
                entryText = tk.StringVar()
                entryText.set("")
                #self.guess_vars.append(var)

                # Create the Entry widget
                guessElement = tk.Entry(self, textvariable=entryText, state="disabled", width=2, font=("Helvetica", 25))
                guessElement.grid(row=(2*i)+5, column=j+1, padx=5, pady=2, sticky='ew')

                #We don't need to save the reference to the actual Entry, only to the reference of the entryText
                guessLineStructure.append(entryText) 

            self.guessGridStructure.append(guessLineStructure)      


    def update_guess_grid(self, entry_boxes, errorMarginRed, errorMarginGreen, errorMarginBlue ):
        # guess_line_values contains the error margin for each hex colour pair, then each hex digit the player submitted as a guess
        guess_line_values = [errorMarginRed, errorMarginGreen, errorMarginBlue] # Add the error margins
        for hex_digit in entry_boxes:   # Add each hex digit
            guess_line_values.append(hex_digit.get())

        self.list_of_guess_line_values.insert(0, guess_line_values) # Insert the latest guess into the first position of the list that contains the previous guesses
        
        for i in range(min(len(self.list_of_guess_line_values), MAX_ALLOWED_GUESSES)):
            guessLineStructure = self.guessGridStructure[i]
            #up/down indicators
            for j in range(3):
                guessLineStructure[j]['text'] = self.error_margin_symbols(self.list_of_guess_line_values[i][j])
            for j in range(HEX_LENGTH):
                guessLineStructure[j+3].set(self.list_of_guess_line_values[i][j+3])   
        
                  
    def error_margin_indicator(self, number):
        # Calculates the base-3 logarithm of the absolute of a number and rounds it up to the next integer.
        # If the original number is negative it then returns this value as a negative. 
        # Need to add 1, since if you are out by 1 then log3 will be zero, and the guess is still not quite correct
        if number == 0:
            return 0
        elif number < 0:
            margin = -1 * math.ceil(math.log(abs(number), ERROR_MARGIN_INDICATOR_DIFFICULTY)) - 1
            if margin < -1:
                margin = margin + 1
        else:
            margin = math.ceil(math.log(number, ERROR_MARGIN_INDICATOR_DIFFICULTY)) + 1
            if margin > 1:
                margin = margin - 1
        return margin


    def error_margin_symbols(self, number):
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


    def update_score(self, error_margin_red, error_margin_green, error_margin_blue):
        print(f"R: {error_margin_red} G: {error_margin_green}   B: {error_margin_blue}")

        average_error = (abs(error_margin_red) + abs(error_margin_green) + abs(error_margin_blue)) / 3
        print(f"err: {average_error}")
        self.score = ((255 - average_error)/255) * self.score 
        print(f"Score: {self.score}")
        self.accuracy = (int(self.score)/255)*100
        print(f"Accuracy: {round(self.accuracy,2)}%")




    def get_sign(self, value):
            if value > 0:
                return 1
            elif value < 0:
                return -1
            else:
                return 0    



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
                                 command=self.master.show_menu_screen)
        back_button.grid(row=4, column=0, pady=(10, 20), sticky="n")


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

        # Configure tags for various styles
        self.configure_tags()               
        # Load and parse the file
        self.load_and_display_text("help.txt")

        # Make the text area read-only after loading
        self.text_area.config(state=tk.DISABLED)

        # Button to trigger opening the HTML file
        more_information_button = tk.Button(self, text="More Information",
                            command=lambda: self.open_html_in_browser(HTML_FILE_TO_OPEN),
                            font=("Arial Rounded MT Bold", 14), bg="light blue", fg="black",
                                 activebackground="dark blue", activeforeground="white",
                                 width=15, relief="flat", bd=2,
                            ) 
        more_information_button.grid(row=2, column=0, pady=(10, 20), sticky="s",)


    def configure_tags(self):
        '''Define the tags we can use. At the moment it is just Heading tag, but we could add more later.'''
        # Heading tag
        self.text_area.tag_config(TAG_HEADING, font=("Arial", 16, "bold"), foreground="navy", justify="center",spacing2=1, #Space between lines (if multiline)
                            spacing3=1)
       


 
    def load_and_display_text(self, file_name):
        '''Go through each of the lines in the help.txt file, and determine if they have been tagged to be formatted in some way.
           If they have, apply the tag to the text. If not, just display the text as is.'''
        # Use try, because there is a lot that can go wrong - the file doesn't exist or contains garbage.
        # By using try, if it fails for some reason, the app can put up an error message instead of crashing the program
        try:
            # OPen the file read only
            with open(file_name, "r", encoding="utf-8") as help_file:
                help_lines = help_file.readlines()

            for help_line in help_lines:
                # remove trailing new line
                help_line = help_line.strip('\n')


                if help_line.startswith("#") and help_line.endswith("#"):
                    text = help_line.strip("#").strip() + "\n\n"    #Take away the markup
                    self.text_area.insert(tk.END, text, (TAG_HEADING,))  #Add  it t o the text area as a Heading
                    continue # Break out of the for loop, because we have now finished proceessing this line

  
                self.text_area.insert(tk.END, help_line) #If we got here then there was no markup so just add the line 
                self.text_area.insert(tk.END, "\n") # Add newline after each processed line

        # If the file doesn't exist, or there is some other error, then we will catch it here
        except FileNotFoundError:
            messagebox.showerror("Error", f"File not found: {file_name}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")


    def open_html_in_browser(self, html_file_name):
        """
        Opens the specified HTML file in the user's default web browser. Due to limitations of TKinter we can't display html files
        which are far richer and can container images etc. As an alternative to the simple help we display IN the app we  offer more 
        help in the browser window (as html)

        """
        html_help_file_dir = os.path.dirname(__file__) # os.path.dirname(__file__) gets the directory of the app
        html_file_path = os.path.join(html_help_file_dir, html_file_name) # os.path.join combines the directory with the filename

        # Check if the HTML file actually exists
        if not os.path.exists(html_file_path):
            messagebox.showerror("File Not Found",
                                f"The HTML help file '{html_file_name}' was not found at:\n{html_file_path}\n"
                                "Please ensure it's in the same directory as this app.")
            return

        try: #We use try, so if something goes wrong we don't crash the whole app.
            # Use 'file:///' prefix for local files to ensure they open correctly
            webbrowser.open(f"file:///{html_file_path}")
            #print(f"Successfully opened '{html_file_path}' - yay!")
        except Exception as e: #If it didn't work display the error why
            messagebox.showerror("Browser Error",
                                f"Could not open the HTML page in your default browser.\nError: {e}")
            print(f"Error opening HTML file: {e}")



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
                                 command=self.master.show_menu_screen)
        back_button.grid(row=4, column=0, pady=(10, 20), sticky="n")


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
            difficulty_label = tk.Label(self.scores_frame, text=f"{difficulty.capitalize()} ", font=("Arial Rounded MT Bold", 26, "bold"), bg="white")
            difficulty_label.grid(row=row_counter, column=0, columnspan=2, pady=(15, 5))
            row_counter += 1

            # Create header labels for the columns
            player_header = tk.Label(self.scores_frame, text="Player Name", font=("Arial Rounded MT Bold", 20, "bold"), bg="white")
            player_header.grid(row=row_counter, column=0, padx=10, pady=2, sticky="w")
            score_header = tk.Label(self.scores_frame, text="Score", font=("Arial Rounded MT Bold", 20, "bold"), bg="white")
            score_header.grid(row=row_counter, column=1, padx=10, pady=2, sticky="w")
            row_counter += 1
            
            # Display the scores for each player
            for player in players:
                player_name_label = tk.Label(self.scores_frame, text=player["player_name"], font=("Arial Rounded MT Bold", 18, "bold"), bg="white")
                player_name_label.grid(row=row_counter, column=0, padx=10, pady=2, sticky="w")
                
                score_label = tk.Label(self.scores_frame, text=player["score"], font=("Arial Rounded MT Bold", 18, "bold"), bg="white")
                score_label.grid(row=row_counter, column=1, padx=10, pady=2, sticky="w")
                
                row_counter += 1



class MenuScreen(tk.Frame):
    '''initial screen with option for new game'''
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

        title_label.grid(row=0, column=0, pady=(50, 20), sticky="s") # padded at top, sticks to south

        # new game button
        new_game_button = tk.Button(self, text="New Game",
                                     font=("Arial Rounded MT Bold", 20), bg="darkolivegreen3", fg="black",
                                     activebackground="darkolivegreen4", activeforeground="white",
                                     width=12, height=2, relief="raised", bd=4,
                                     command=self.master.show_new_game_screen)
        new_game_button.grid(row=1, column=0, pady=10)


        # highscores button
        highscores_button = tk.Button(self, text="Leaderboard",
                                     font=("Arial Rounded MT Bold", 20), bg="goldenrod3", fg="black",
                                     activebackground="goldenrod4", activeforeground="white",
                                     width=12, height=1, relief="raised", bd=4,
                                     command=self.master.show_high_score_screen)
        highscores_button.grid(row=2, column=0, pady=10, sticky="s")


        # help button
        help_button = tk.Button(self, text="Help",
                                     font=("Arial Rounded MT Bold", 20), bg="steelblue3", fg="black",
                                     activebackground="steelblue4", activeforeground="white",
                                     width=12, height=1, relief="raised", bd=4,
                                     command=self.master.show_help_screen)
        help_button.grid(row=3, column=0, pady=10, sticky="n")


    #exit game button
        exit_game_button = tk.Button(self, text="Exit",
                                     font=("Arial Rounded MT Bold", 20), bg="coral1", fg="black",
                                     activebackground="coral3", activeforeground="white",
                                     width=12, height=1, relief="raised", bd=4,
                                     command=self.master.exit_game)
        exit_game_button.grid(row=4, column=0, pady=10, sticky="n")




class NewGameScreen(tk.Frame):
    '''for entering difficulty'''
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

        # Easy Game Button
        standard_button = tk.Button(difficulty_buttons_frame, text="Standard",
                                     font=("Arial Rounded MT Bold", 16), bg="light blue", fg="black",
                                     activebackground="dark blue", activeforeground="white",
                                     width=10, height=1, relief="raised", bd=3,
                                     command=lambda: self.master.show_game(DIFFICULTY_STANDARD))
        standard_button.pack(side=tk.LEFT, padx=10)

        # Hard Game Button
        standard_button = tk.Button(difficulty_buttons_frame, text="Hard",
                                     font=("Arial Rounded MT Bold", 16), bg="light blue", fg="black",
                                     activebackground="dark blue", activeforeground="white",
                                     width=10, height=1, relief="raised", bd=3,
                                     command=lambda: self.master.show_game(DIFFICULTY_HARD))
        standard_button.pack(side=tk.LEFT, padx=10)

        # back button
        back_button = tk.Button(self, text="Back",
                                 font=("Arial Rounded MT Bold", 14), bg="light blue", fg="black",
                                 activebackground="dark blue", activeforeground="white",
                                 width=15, relief="flat", bd=2,
                                 command=self.master.show_menu_screen)
        back_button.grid(row=4, column=0, pady=(10, 20), sticky="n")




class Highscores:
    def __init__(self, filename=HIGH_SCORE_FILE):
        self.filename = filename

    def load_highscores(self):
        try:
            with open(self.filename, 'r') as f:
                content = f.read()
                if not content:
                    return {}
                return json.loads(content)
        except FileNotFoundError:
            return {}

    def save_highscores(self, highscores):
        with open(self.filename, 'w') as f:
            json.dump(highscores, f, indent=4)
            

            #for sorting order
    def get_score_key(self, score_entry):
        return score_entry['score']

    def add_new_score(self, player_name, score, mode):
        highscores_by_mode = self.load_highscores()

        #check if mode exists, else creates new list
        if mode not in highscores_by_mode:
            highscores_by_mode[mode] = []

        #add new score
        highscores_by_mode[mode].append({"player_name": player_name, "score": score})
        #puts scores in order of highest to lowest
        highscores_by_mode[mode].sort(key=self.get_score_key, reverse=True)
        #only contains top ten scores
        highscores_by_mode[mode] = highscores_by_mode[mode][:10]
        self.save_highscores(highscores_by_mode)

    def get_highscores(self, mode=None):
        all_highscores = self.load_highscores()
        if mode:
            return all_highscores.get(mode, [])
        return all_highscores

# run game
if __name__ == "__main__":
    app = HexGame()
    app.mainloop()