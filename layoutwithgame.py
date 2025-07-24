import tkinter as tk
import random
from tkinter import *
import re #regular expression module
import math

# main
class HexGame(tk.Tk):
    def __init__(self):
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
        '''removes current frame and switches to new'''
        if self.current_frame:
            self.current_frame.destroy() # remove  old frame
        new_frame = frame_class(self) # make new frame, passing self (the hexgame instance)
        self.current_frame = new_frame
        self.current_frame.grid(row=0, column=0, sticky="nsew") # make new frame
    def show_menu_screen(self):
        '''main menu'''
        self.switch_frame(MenuScreen)

    def show_new_game_screen(self):
        '''new game options screen'''
        self.switch_frame(NewGameScreen)


    def show_standard_game(self):
        '''standard game sreen'''
        self.switch_frame(StandardGame)

class StandardGame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="white")
        self.master = master

        self.windowWidth = 400
        self.windowHeight = 800
        self.canvasWidth = 400
        self.canvasHeight = 200

        self.targetColour = "#888888"
        self.targetRed = "88"
        self.targetGreen = "88"
        self.targetBlue = "88"
        self.guessColour = "#888888"
        self.focus = 0
        self.guess_count = 0
        self.max_allowed_guesses = 8
        self.guessGridGuesses = []

        for i in range(0, 7):
            self.grid_columnconfigure(i, weight=0)
        self.grid_rowconfigure(8, weight=0) # for padding at bottom

        self.grid_columnconfigure(0, weight=1)
        for i in range(1, 7):
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

        self.entries = [] # To store references to our Entry widgets
        self.entry_vars = [] # To store their associated StringVars
        for i in range(6):
            # Create a StringVar for each entry
            var = tk.StringVar()
            self.entry_vars.append(var)

            # Create the Entry widget
            # the validate='key' means validation will occur on every key press.
            # the validatecommand is the function to call for validation.
            entry = tk.Entry(self, textvariable=var, validate='key', validatecommand=(vcmd, '%P'), width=2, font=("Arial Rounded MT Bold", 25))
            entry.grid(row=3, column=i+1, padx=5, pady=2, sticky='ew')
            self.entries.append(entry)

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
        self.entries[0].focus_set()


    def create_canvas(self):
        self.colourCanvas = tk.Canvas(self, width=400, height=200, bg="white", highlightbackground="black", highlightthickness=2)
        self.colourCanvas.grid(row=0, column=1, columnspan=6, padx=5, pady=10, sticky='w')

    def create_target_box(self):
        
        # define the color for the box
        self.targetColour = "#%06x" % random.randint(0, 0xFFFFFF)
        print(self.targetColour)
        #We get the RGB values from index 1, because index 0 is hash #
        self.targetRed = int(self.targetColour[1:3], 16)
        self.targetGreen = int(self.targetColour[3:5], 16)
        self.targetBlue = int(self.targetColour[5:7], 16)

        # draw a rectangle (the "box") on the canvas
        # coordinates are (x1, y1, x2, y2) where (x1, y1) is the top-left corner
        # and (x2, y2) is the bottom-right corner
        # The 'fill' option sets the solid color
        # The 'outline' option sets the border color
        box_width = 200
        box_height = 150
        
        # Calculate coordinates to center the box on the canvas
        canvas_width = 400
        canvas_height = 200
        x1 = 0
        y1 = 0
        x2 = 190
        y2 = y1 + box_height

        self.targetBox = self.colourCanvas.create_rectangle(0, 0, 190,190, fill=self.targetColour, outline="", width=0)


    def create_guess_box(self):
        
        # define the color for the box
        box_color = self.guessColour # You can change this to any valid color name or hex code (e.g., "#00FF00" for green)

        # draw a rectangle (the "box") on the canvas.
        # the coordinates are (x1, y1, x2, y2) where (x1, y1) is the top-left corner
        # and (x2, y2) is the bottom-right corner.
        # the 'fill' option sets the solid color.
        # the 'outline' option sets the border color.
        box_width = 200
        box_height = 150
        
        # calculate coordinates to center the box on the canvas
        
        self.guessBox = self.colourCanvas.create_rectangle(200, 0, 390,190, fill=box_color, outline="", width=0)     

    def update_guess_box(self):
        # generate a random hex color code
        colour = "#%06x" % random.randint(0, 0xFFFFFF)
        self.colourCanvas.itemconfig(self.guessBox, fill=colour)


    def validate_single_char(self, input_text):
        '''validation function to ensure only one character is entered'''
        if (len(input_text) <= 1) and (re.fullmatch(r"^[a-fA-F0-9-]*$", input_text)):
            return True
        else:
            return False

    def get_input(self):
        '''function to retrieve the single character entered'''
        char = self.r1Guess.get()
        print(f"You entered: {char}")

    def advance_focus(self, event, current_idx):
        # Get the current text in the entry
        current_text = self.entry_vars[current_idx].get()

        # If a character was entered (and it's not empty after deletion/backspace)
        # and it's a single character (ensures we don't advance on second char in same box if width > 1)
        # and we are not on the last entry
        if current_text and len(current_text) == 1 and current_idx < len(self.entries) - 1:
            # Move focus to the next entry
            self.entries[current_idx + 1].focus_set()
            # Optionally select the text in the next box for easy overwriting
            self.entries[current_idx + 1].selection_range(0, tk.END)



    def regress_focus(self, event, current_idx):
        # If Backspace or Delete was pressed and the entry is empty (or about to become empty)
        if not self.entry_vars[current_idx].get() and current_idx > 0:
            # Move focus to the previous entry
            self.entries[current_idx - 1].focus_set()
            # Optionally move cursor to end of previous box
            self.entries[current_idx - 1].icursor(tk.END)

    def submit_entry(self, event, current_idx):
        # If Enter was clicked first validate the entries so far to make sure each box has a valid entry,
        #  then if it has update the grid, check if the game has finished, if it hasn't clear the entry boxes
        #print(f"You entered: {char}") 
        print(f"You pressed Enter") 

        #Validate entries are all full
        if (not self.validate_entries()):
            print("Entries are invalid")
            return
        else:
            print("Entries are valid")

            #If everything is ok combine the boxes and check it against the target colours. 
            print(self.entries[0].get(),self.entries[1].get(),self.entries[2].get(),self.entries[3].get(),self.entries[4].get(),self.entries[5].get())
            guessRed = int(f"{self.entries[0].get()}{self.entries[1].get()}", 16)
            guessGreen = int(f"{self.entries[2].get()}{self.entries[3].get()}", 16)
            guessBlue = int(f"{self.entries[4].get()}{self.entries[5].get()}", 16)
           

            #Calculate the error margins for each colour
            differenceRed = guessRed - self.targetRed
            differenceGreen = guessGreen - self.targetGreen
            differenceBlue = guessBlue - self.targetBlue

            errorMarginRed = self.error_margin_indicator(differenceRed)
            errorMarginGreen = self.error_margin_indicator(differenceGreen)
            errorMarginBlue = self.error_margin_indicator(differenceBlue)

            #Move everything in the answer grid down 1, append the latest answer to the grid
            self.update_guess_grid(self.entries, errorMarginRed, errorMarginGreen, errorMarginBlue)


            #If the player has used up their guesses then game over

            #If the game is still going then put focus back into the first box

    def validate_entries(self):
        return True    



        

    def create_guess_grid(self):
        #initialize the grid array
        self.guessGridStructure = []
        guessLineStructure = []
        #For each guess line there's an indicator row (up or down), and a row below that contains the guess
        self.guesses = [] # To store references to our Entry widgets
        self.guess_vars = [] # To store their associated StringVars

        # We store 3 tuplets for each guess - The first is the errorMargin for the guess, then the 2 associated digits for each colour. 
        for i in range(self.max_allowed_guesses):
            guessLineStructure = []
            #up/down indicators
            for j in range(3):
                labelElement = tk.Label(self, text="<<<<>>>>")
                labelElement.grid(row=(2*i)+4, column=(2*j)+1,  columnspan=2, padx=5, pady=2, sticky='ew')
                guessLineStructure.append(labelElement)
            for j in range(6):
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



    def update_guess_grid(self, entries, errorMarginRed, errorMarginGreen, errorMarginBlue ):

        newGuessLine = [errorMarginRed, errorMarginGreen, errorMarginBlue,entries[0].get(),entries[1].get(),entries[2].get(),entries[3].get(),entries[4].get(),entries[5].get()]
        self.guessGridGuesses.insert(0, newGuessLine)
        #For each guess line there's an indicator row (up or down), and a row below that contains the guess
        self.guesses = [] # To store references to our Entry widgets
        self.guess_vars = [] # To store their associated StringVars

        for i in range(len(self.guessGridGuesses)):
            guessLineStructure = self.guessGridStructure[i]
            #up/down indicators
            for j in range(3):
                guessLineStructure[j]['text'] = self.error_margin_symbols(self.guessGridGuesses[i][j])
            for j in range(6):
                guessLineStructure[j+3].set(self.guessGridGuesses[i][j+3])   
        


                  
    def error_margin_indicator(self, number):
        # Calculates the base-3 logarithm of the absolute of a number and rounds it up to the next integer.
        # If the original number is negative it then returns this value as a negative. 
        # Need to add 1, since if you are out by 1 then log3 will be zero, and the guess is still not quite correct
        if number == 0:
            return 0
        elif number < 0:
            return -1 * math.ceil(math.log2(abs(number))) + 1
        else:
            return math.ceil(math.log2(number)) + 1


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





# main menu
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
        title_label = tk.Label(self, text="HEX-A-GUESS-A",
                               font=("Arial Rounded MT Bold", 36, "bold"), fg="black", bg="white")
        title_label.grid(row=0, column=0, pady=(50, 20), sticky="s") # padded at top, sticks to south

        # new game button
        new_game_button = tk.Button(self, text="New Game",
                                     font=("Arial Rounded MT Bold", 20), bg="light green", fg="black",
                                     activebackground="dark green", activeforeground="white",
                                     width=15, height=2, relief="raised", bd=4,
                                     command=self.master.show_new_game_screen)
        new_game_button.grid(row=1, column=0, pady=10)


# new game
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
