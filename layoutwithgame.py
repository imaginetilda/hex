import tkinter as tk
import random
from tkinter import *
from tkinter import messagebox
import re #regular expression module
import math

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
       # self.resizable(False, False)

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


    def show_standard_game(self):
        """standard game screen"""
        self.switch_frame(MainGameGUI)




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

            errorMarginRed = self.error_margin_indicator(differenceRed)
            errorMarginGreen = self.error_margin_indicator(differenceGreen)
            errorMarginBlue = self.error_margin_indicator(differenceBlue)

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
        # x=PhotoImage(file="hexaguessa.png")
        # # resize to 1/4 of original image size
        # x=x.subsample(4)
        # title_label = tk.Label(self, image=x)

        self.photo = PhotoImage(file="hexaguessa.png")
        # resize to 1/4 of original image size
        self.photo = self.photo.subsample(4)
        title_label = tk.Label(self, image=self.photo, bg="white")

        # title_label = tk.Label(self, text="HEX-A-GUESS-A",        
        #                        font=("Arial Rounded MT Bold", 36, "bold"), fg="black", bg="white")
        title_label.grid(row=0, column=0, pady=(50, 20), sticky="s") # padded at top, sticks to south

        # new game button
        new_game_button = tk.Button(self, text="New Game",
                                     font=("Arial Rounded MT Bold", 20), bg="darkolivegreen3", fg="black",
                                     activebackground="darkolivegreen4", activeforeground="white",
                                     width=15, height=2, relief="raised", bd=4,
                                     command=self.master.show_new_game_screen)
        new_game_button.grid(row=1, column=0, pady=10)


    #exit game button
        exit_game_button = tk.Button(self, text="Exit",
                                     font=("Arial Rounded MT Bold", 20), bg="coral1", fg="black",
                                     activebackground="coral3", activeforeground="white",
                                     width=8, height=1, relief="raised", bd=4,
                                     command=self.master.exit_game)
        exit_game_button.grid(row=2, column=0, pady=10)




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

        # standard Button
        standard_button = tk.Button(difficulty_buttons_frame, text="Standard",
                                     font=("Arial Rounded MT Bold", 16), bg="light blue", fg="black",
                                     activebackground="dark blue", activeforeground="white",
                                     width=10, height=1, relief="raised", bd=3,
                                     command=lambda: self.master.show_standard_game())
        standard_button.pack(side=tk.LEFT, padx=10)

        # back button
        back_button = tk.Button(self, text="Back",
                                 font=("Arial Rounded MT Bold", 14), bg="light blue", fg="black",
                                 activebackground="dark blue", activeforeground="white",
                                 width=15, relief="flat", bd=2,
                                 command=self.master.show_menu_screen)
        back_button.grid(row=4, column=0, pady=(10, 20), sticky="n")




# run game
if __name__ == "__main__":
    app = HexGame()
    app.mainloop()