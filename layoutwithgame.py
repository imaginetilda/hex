import tkinter as tk
import random
from tkinter import *
import re #regular expression module

# main
class HexGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Game Menu")
        self.geometry("500x900")
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

        self.targetColour = "grey"
        self.guessColour = "grey"
        self.focus = 0

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

        # # create a button widget
        # button = tk.Button(self, text="Click Me!", command=self.button_click)
        # button.grid(row=2, column=1, columnspan=6, padx=5, pady=10, sticky='w') # sticky='ew' makes it stretch horizontally

        # create a StringVar to hold the entry's text
        # self.r1Guess = tk.StringVar()
        # self.r2Guess = tk.StringVar()
        # self.g1Guess = tk.StringVar()
        # self.g2Guess = tk.StringVar()
        # self.b1Guess = tk.StringVar()
        # self.b2Guess = tk.StringVar()

        # register the validation command
        # the %P is a special Tkinter placeholder that represents the value of the entry
        # if the edit is allowed.
        vcmd = self.register(self.validate_single_char)

        # create the entry widget
        # the validate='key' means validation will occur on every key press.
        # the validatecommand is the function to call for validation.
        """ entryR1 = tk.Entry(self, textvariable=self.r1Guess, validate='key', validatecommand=(vcmd, '%P'), width=2, font=("Comic Sans MS", 25))
        entryR1.grid(row=3, column=1, padx=5, pady=2, sticky='ew') # sticky='ew' makes it stretch horizontally
        entryR2 = tk.Entry(self, textvariable=self.r2Guess, validate='key', validatecommand=(vcmd, '%P'), width=2, font=("Comic Sans MS", 25))
        entryR2.grid(row=3, column=2, padx=5, pady=2, sticky='ew')
        entryG1 = tk.Entry(self, textvariable=self.g1Guess, validate='key', validatecommand=(vcmd, '%P'), width=2, font=("Comic Sans MS", 25))
        entryG1.grid(row=3, column=3, padx=5, pady=2, sticky='ew')
        entryG2 = tk.Entry(self, textvariable=self.g2Guess, validate='key', validatecommand=(vcmd, '%P'), width=2, font=("Comic Sans MS", 25))
        entryG2.grid(row=3, column=4, padx=5, pady=2, sticky='ew')
        entryB1 = tk.Entry(self, textvariable=self.b1Guess, validate='key', validatecommand=(vcmd, '%P'), width=2, font=("Comic Sans MS", 25))
        entryB1.grid(row=3, column=5, padx=5, pady=2, sticky='ew')
        entryB2 = tk.Entry(self, textvariable=self.b2Guess, validate='key', validatecommand=(vcmd, '%P'), width=2, font=("Comic Sans MS", 25))
        entryB2.grid(row=3, column=6, padx=5, pady=2, sticky='ew') """

        # optional: set initial focus to the entry widget
        #entryR1.focus_set()


        self.entries = [] # To store references to our Entry widgets
        self.entry_vars = [] # To store their associated StringVars
        for i in range(6):
            # Create a StringVar for each entry
            var = tk.StringVar()
            self.entry_vars.append(var)

            # Create the Entry widget
            entry = tk.Entry(self, textvariable=var, validate='key', validatecommand=(vcmd, '%P'), width=2, font=("Helvetica", 25))
            entry.grid(row=3, column=i+1, padx=5, pady=2, sticky='ew')
            self.entries.append(entry)

            # Bind the <KeyRelease> event to our advance_focus function
            # <KeyRelease> is generally preferred over <KeyPress> because
            # the textvariable will have been updated by the time KeyRelease fires.
            entry.bind("<KeyRelease>", lambda event, idx=i: self.advance_focus(event, idx))

            # Optional: Bind <BackSpace> or <Delete> to move backward
            entry.bind("<BackSpace>", lambda event, idx=i: self.regress_focus(event, idx))
            entry.bind("<Delete>", lambda event, idx=i: self.regress_focus(event, idx))


        # Set initial focus to the first entry
        self.entries[0].focus_set()
        
       
    def play_game(self):
        pass

    def button_click(self):
        print("Button clicked!")
        self.update_guess_box()

    def create_canvas(self):
        self.colourCanvas = tk.Canvas(self, width=400, height=200, bg="white", highlightbackground="black", highlightthickness=2)
        self.colourCanvas.grid(row=0, column=1, columnspan=6, padx=5, pady=10, sticky='w')

    def create_target_box(self):
        
        # define the color for the box
        box_color = self.targetColour # can change this to any valid color name or hex code (e.g., "#00FF00" for green)

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

        self.targetBox = self.colourCanvas.create_rectangle(0, 0, 190,190, fill=box_color, outline="", width=0)


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

        # Optional: You might want to prevent typing more than one character.
        # You can combine this with validation as shown in previous answers.
        # For this example, we're just checking the length for advancement.

    def regress_focus(self, event, current_idx):
        # If Backspace or Delete was pressed and the entry is empty (or about to become empty)
        if not self.entry_vars[current_idx].get() and current_idx > 0:
            # Move focus to the previous entry
            self.entries[current_idx - 1].focus_set()
            # Optionally move cursor to end of previous box
            self.entries[current_idx - 1].icursor(tk.END)

    def create_guess_grid(self):
        #For each guess line there's an indicator row (up or down), and a row below that contains the guess
        self.guesses = [] # To store references to our Entry widgets
        self.guess_vars = [] # To store their associated StringVars
        for i in range(8):
            #up/down indicators
            for j in range(3):
                label = tk.Label(self, text="<<<<>>>>")
                label.grid(row=(2*i)+4, column=(2*j)+1,  columnspan=2, padx=5, pady=2, sticky='ew')
            for j in range(6):
                # Create a StringVar for each entry
                var = tk.StringVar()
                self.guess_vars.append(var)

                # Create the Entry widget
                guess = tk.Entry(self, textvariable=var, state="disabled", width=2, font=("Helvetica", 25))
                guess.grid(row=(2*i)+5, column=j+1, padx=5, pady=2, sticky='ew')
                self.guesses.append(guess)       



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
                               font=("Comic Sans MS", 36, "bold"), fg="black", bg="white")
        title_label.grid(row=0, column=0, pady=(50, 20), sticky="s") # padded at top, sticks to south

        # new game button
        new_game_button = tk.Button(self, text="New Game",
                                     font=("Comic Sans MS", 20), bg="light green", fg="black",
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
                                     font=("Comic Sans MS", 16), bg="light blue", fg="black",
                                     activebackground="dark blue", activeforeground="white",
                                     width=10, height=1, relief="raised", bd=3,
                                     command=lambda: self.master.show_standard_game())
        standard_button.pack(side=tk.LEFT, padx=10)

        # back button
        back_button = tk.Button(self, text="Back",
                                 font=("Comic Sans MS", 14), bg="light blue", fg="black",
                                 activebackground="dark blue", activeforeground="white",
                                 width=15, relief="flat", bd=2,
                                 command=self.master.show_menu_screen)
        back_button.grid(row=4, column=0, pady=(10, 20), sticky="n")

# run game
if __name__ == "__main__":
    app = HexGame()
    app.mainloop()
