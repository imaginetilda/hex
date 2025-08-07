import json

HIGHSCORE_FILE = "highscores.json"

class Highscores:
    def __init__(self, filename=HIGHSCORE_FILE):
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


high_scores = Highscores()

#example scores for easy mode (mode one)
high_scores.add_new_score("Player 1", 94.3, "mode_one")
high_scores.add_new_score("Player 3", 90.5, "mode_one")

#example scores for easy mode (mode one)
high_scores.add_new_score("Player 2", 87.5, "mode_two")

#show all
print(high_scores.get_highscores())

#show only easy
print("Highscores for easy:")
print(high_scores.get_highscores(mode="mode_one"))