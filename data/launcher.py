import tkinter as tk
import json


class GameLauncher:

    def __init__(self, info):
        self.root = tk.Tk()
        self.root.title("Game Launcher")
        self.root.iconphoto(False, tk.PhotoImage(file='data/icon/icon.png'))
        self.root.geometry("500x300")

        # temp
        active_stat = tk.BooleanVar(self.root)
        active_stat.set(True)

        # game
        self.launch_game = False
        self.x = 0
        self.y = 0
        self.info = info

        message_0 = tk.Label(self.root, text="Greetings from Poland!!!")

        resolution_label = tk.Label(self.root, text="Resolution:")
        resolutions = self.info['resolutions']
        self.resolution = tk.StringVar()
        self.resolution.set(self.info['game']['screen']['resolution'])
        resolution_list = tk.OptionMenu(self.root, self.resolution, *resolutions)

        if self.info['game']['screen']['fullscreen'] == 1:
            self.fullscreen = tk.IntVar(value=1)
        else:
            self.fullscreen = tk.IntVar()
        check_box = tk.Checkbutton(self.root, text="Fullscreen", variable=self.fullscreen)

        # buttons
        start_button = tk.Button(self.root, text="Play", padx="50", command=self.start_game)
        exit_button = tk.Button(self.root, text="Quit", padx="50", command=self.quit)

        message_0.pack(pady=(15, 0))
        resolution_label.pack(pady=(15, 0))
        resolution_list.pack(pady=(5, 0))

        check_box.pack(pady=(5, 0))
        start_button.pack(pady=(15, 0))
        exit_button.pack(pady=(5, 0))

    def start_game(self):

        self.info['game']['screen']['resolution'] = self.resolution.get()
        self.info['game']['screen']['fullscreen'] = self.fullscreen.get()

        with open("startup.json", "w") as write_file:
            json.dump(self.info, write_file)
        write_file.close()
        self.launch_game = True
        self.root.destroy()

    def quit(self):
        self.root.quit()

    def temp(self):
        return self.launch_game