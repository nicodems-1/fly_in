import tkinter as tk

class MapVisualizer():
    def __init__(self):
        self.root = tk.Tk()
        self.screen_width= self.root.winfo_screenwidth()*0.7
        self.screen_height = self.root.winfo_screenheight()*0.7
        self.canvas = tk.Canvas(self.root, width=self.screen_width, height=self.screen_height, borderwidth=0, highlightthickness=0,
                       bg="white")

    def move_png(self):
        self.canvas.pack()
        img = tk.PhotoImage(file="drone.png")
        image = self.canvas.create_image(100, 100, anchor=tk.NW, image=img)


    def load_map(self, context):
        self.canvas.grid()
        self.move_png()
        self.root.title("FLY IN")
        self.root.mainloop()