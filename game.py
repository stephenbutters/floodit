#Author: Hengzhi Wu

import Tkinter as Tk
import argparse
import random
import copy

COLORS = ("white", "black", "red", "green", "blue", "cyan", "yellow", "magenta")

class Box(object):
    def __init__(self, x, y, c):
        self.x = x
        self.y = y
        self.color = self.choose_color(c)

    def choose_color(self, c):
        colors = COLORS[0:c]
        return colors[random.randint(0, c-1)]

    def change_color(self, color):
        self.color = color

    def neighbors(self, width, height):
        if self.x == 0 and self.y == 0:
            return [(self.x+1, self.y), (self.x, self.y+1)]
        elif self.x == 0 and self.y == width-1:
            return [(self.x+1, self.y), (self.x, self.y-1)]
        elif self.x == height-1 and self.y == 0:
            return [(self.x-1, self.y), (self.x, self.y+1)]
        elif self.x == height-1 and self.y == width-1:
            return [(self.x-1, self.y), (self.x, self.y-1)]
        elif self.x == 0 and self.y > 0 and self.y < width-1:
            return [(self.x+1, self.y), (self.x, self.y-1), (self.x, self.y+1)]
        elif self.x == height-1 and self.y > 0 and self.y < width-1:
            return [(self.x-1, self.y), (self.x, self.y-1), (self.x, self.y+1)]
        elif self.x > 0 and self.x < height-1 and self.y == 0:
            return [(self.x, self.y+1), (self.x-1, self.y), (self.x+1, self.y)]
        elif self.x > 0 and self.x < height-1 and self.y == width-1:
            return [(self.x, self.y-1), (self.x-1, self.y), (self.x+1, self.y)]
        else:
            return [(self.x, self.y-1), (self.x-1, self.y), (self.x+1, self.y), (self.x, self.y+1)]

class Game(Tk.Tk):
    def __init__(self, parent):
        Tk.Tk.__init__(self, parent)
        #Parse command line argument
        parser = argparse.ArgumentParser(add_help = False)
        parser.add_argument('--width', type = int, default = 10)
        parser.add_argument('--height', type = int, default = 10)
        parser.add_argument('--color', type = int, default = 5)
        self.args = parser.parse_args()
        if self.args.width > 20 or self.args.width <= 0:
            self.args.width = 10
        if self.args.height > 20 or self.args.height <= 0:
            self.args.height = 10
        if self.args.color > 8 or self.args.color < 2:
            self.args.color = 5
        #Set up main canvas
        self.resizable(False, False)
        self.canvas = Tk.Canvas(self, width = 400, height = 400)
        self.canvas.grid(column = 0, row = 0, columnspan = 11, padx = 5, pady = 5)

        #Grid creation
        self.boxes = [[Box(i, j, self.args.color) for j in range(self.args.width)] for i in range(self.args.height)]
        self.draws = []
        cellw = float(self.canvas['width']) / self.args.width
        cellh = float(self.canvas['height']) / self.args.height
        side = min(cellw, cellh)
        self.canvas.create_line(1, 1, 1, self.args.height*side)
        self.canvas.create_line(1, 1, self.args.width*side, 1)
        for i in range(self.args.height):
            temp = []
            for j in range(self.args.width):
                draw = self.canvas.create_rectangle(j*side, i*side, (j+1)*side, (i+1)*side, fill = self.boxes[i][j].color)
                temp.append(draw)
            self.draws.append(temp)

        #Some useful variables for recording
        self.currentArea = [(0, 0)]
        self.BFS(self.boxes[0][0].color)

        #Count Label
        self.displayCount = Tk.StringVar()
        self.myCount = 0
        self.aiCount = self.aiSteps()
        self.display = Tk.Label(self, textvariable = self.displayCount)
        self.displayCount.set(str(self.myCount) + "/" + str(self.aiCount))
        self.display.grid(column = 0, row = 1, pady = 5)

        #Button creation
        self.buttons = []
        n = 2
        for col in COLORS[0:self.args.color]:
            b = Tk.Button(self, bg = col, activebackground = col, borderwidth = 4)
            b.bind("<Button-1>", lambda e, col = col: self.button_click(e, col))
            b.grid(column = n, row = 1, pady = 5, sticky = 'S')
            n = n + 1
            self.buttons.append(b)

        #Game status info display
        self.statusDisplay = Tk.StringVar()
        self.statusLabel = Tk.Label(self, textvariable = self.statusDisplay)
        self.statusLabel.grid(column = 0, row = 2, columnspan = 11, pady = 5)

        #Configure columns and rows in the grid
        self.grid_columnconfigure(0, weight = 1)
        for i in range(1,11):
            self.grid_columnconfigure(i+1, weight = 0)
        self.grid_columnconfigure(10, weight = 1)
        self.grid_rowconfigure(1, pad = 10)

    def aiSteps(self):
        boxes, currentArea, steps = copy.deepcopy(self.boxes), copy.deepcopy(self.currentArea), 0
        while len(currentArea) != self.args.width * self.args.height:
            area = [[] for _ in range(self.args.color)]
            for i in range(self.args.color):
                area[i].extend(currentArea)
            #Boxes that gained for each color in each step
            for i in range(self.args.color):
                col = COLORS[i]
                for tup in area[i]:
                    boxes[tup[0]][tup[1]].change_color(col)
                visited, stack = set(), [area[i][0]]
                visited.add(area[i][0])
                while stack:
                    top = stack.pop()
                    neig = boxes[top[0]][top[1]].neighbors(self.args.width, self.args.height)
                    for ne in neig:
                        if ne not in visited and boxes[ne[0]][ne[1]].color == col:
                            visited.add(ne)
                            stack.append(ne)
                            if ne not in area[i]:
                                area[i].append(ne)
            l = [len(area[i]) for i in range(self.args.color)]
            idx = l.index(max(l))
            currentArea = area[idx]
            steps = steps + 1
        return steps

    def BFS(self, col):
        #Find out boxes that connected to currentArea and change their color too
        visited, stack = set(), [self.currentArea[0]]
        visited.add(self.currentArea[0])
        while stack:
            top = stack.pop()
            neig = self.boxes[top[0]][top[1]].neighbors(self.args.width, self.args.height)
            for ne in neig:
                if ne not in visited and self.boxes[ne[0]][ne[1]].color == col:
                    visited.add(ne)
                    stack.append(ne)
                    if ne not in self.currentArea:
                        self.currentArea.append(ne)

    def terminate(self, status):
        if status == "win":
            self.statusDisplay.set("Congratulations! You win the game. Now close this window.")
        else:
            self.statusDisplay.set("What a shame! You lose the game. Now close this window.")
        for b in self.buttons:
            b.unbind("<Button-1>")

    def button_click(self, event, col):
        #Change the color of all currentArea boxes
        for tup in self.currentArea:
            self.boxes[tup[0]][tup[1]].change_color(col)
            self.canvas.itemconfig(self.draws[tup[0]][tup[1]], fill = col)
        #Run bredth first search
        self.BFS(col)
        #update counter
        self.myCount = self.myCount + 1
        self.displayCount.set(str(self.myCount) + "/" + str(self.aiCount))
        #Win or lose
        if self.myCount <= self.aiCount and len(self.currentArea) == self.args.width * self.args.height:
            self.terminate("win")
        elif self.myCount == self.aiCount and len(self.currentArea) < self.args.width * self.args.height:
            self.terminate("lose")

def main():
    app = Game(None)
    app.title("Flood it")
    app.mainloop()

if __name__ == "__main__":
    main()
