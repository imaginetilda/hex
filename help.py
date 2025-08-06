import tkinter as tk
import random
from tkinter import *
from tkinter import messagebox, scrolledtext
import re #regular expression module
import math
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

# The help HTML file to be opened
HTML_FILE_TO_OPEN = "help.html"


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

        # Configure tags for various styles
        self.configure_tags()               
        # Load and parse the file
        self.load_and_display_text("Help Component\help.txt")

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
        

   
# run game
if __name__ == "__main__":
    app = HexGame()
    app.mainloop()