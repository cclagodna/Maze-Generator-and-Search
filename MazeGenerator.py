# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 14:36:48 2022

@author: Carl
"""

import os
import random
import math
import time
import tracemalloc
from colorama import init
from colorama import Fore, Back, Style

#-----------------------------------------------------------------------------
maze = []

#The heuristic function
def h(a, b):
    #Inputs: the current node coordinates and the end node coordinates
    #Outputs: heuristic value that is an integer >= 0
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
#Checks if character is contained in a 2D array
def isIn2dArray(char, array):
    for row in array:
        if char in row:
            return True
    return False

#Output maze in console
#Uses colorama to make output fancier
def printMaze():
    global maze
    for row in maze:
        #Print each character in a row on one line
        for col in row:
            print(col, end = " ")
        print()
    #Reset colorama styling
    print(Style.RESET_ALL)

#Output maze in console, while also displaying the cost of each node
#Uses colorama to make output fancier
def printMazeWithCosts():
    global maze
    global mazeCosts
    for y in range(height):
        for x in range(width):
            #Print cost of space instead of the char
            #NOTE: the back and fore ground of walls are white
            #   thus costsc won't show
            print(maze[y][x][:-1] + str(mazeCosts[y][x]), end = " ")
        print()
    #Reset colorama styling
    print(Style.RESET_ALL)
    
#Remove search characters from maze so it can be searched again
def resetSearch():
    global maze
    for i in range(width):
        for j in range(height):
            if maze[j][i] not in (cell_, wall_):
                maze[j][i] = cell_
            
#Returns list of nearby cells
def getNearbyCells(point):
    return getNearbyTiles(point, cell_)

#Returns list of nearby walls
def getNearbyWalls(point):
    return getNearbyTiles(point, wall_)

#Returns list of nearby searched cells
def getNearbySearched(point):
    return getNearbyTiles(point, searched_)

#Returns list of nearby paths
def getNearbyPaths(point):
    return getNearbyTiles(point, path_)

#Return list of tiles of a type near a specified tile
def getNearbyTiles(point, tile):
    #Input:
    #   point - the x, y coordinate of tile being checked
    #   tile - character representing a tile of some type
    #Output:
    #   An array of nearby tiles of desired type
    #   Tiles will be ordered in directions E S W N from source
    
    nearTiles = []
    dx = 0
    dy = 0
    
    #Check each tile 1 space in every cardinal direction from source tile
    for i in range(4):
        #cos(i*pi/2) -> 1, 0, -1, 0
        dx = round(math.cos(i * math.pi /2))
        #sin(i*pi/2) -> 0, 1, 0, -1
        dy = round(math.sin(i * math.pi / 2))
        
        x = point[0] + dx
        y = point[1] + dy
        
        #If position of nearby cell is out-of-bounds, skip that cell
        if x < 0 or x >= width or y < 0 or y >= height:
            continue
        
        #Check if nearby tile is that of desired type
        #Make sure to flop x and y when accessing indicies of maze
        if maze[y][x] == tile:
            nearTiles.append((x, y))
      
    return nearTiles


#-----------------------------------------------------------------------------
#Initialize variables

#Start time of program in seconds
timeStart = time.time()
#Start CPU usage tracking module
tracemalloc.start()
#Initialize colorama
init()

#Specify a seed for the RNG if desired
print("Input a seed. If random seed is desired, press enter")
seed = input("Seed: ")
try:
    seed = int(seed)
    random.seed(seed)
except ValueError:
    print("Random seed will be generated")
    
#Character used to designate a wall
wall_ = Back.WHITE + '#'
#Character used to designate an empty cell
cell_ = Back.BLACK + ' '
#Designates path that search algorithm took to find exit
searched_ = Back.BLUE + '.'
#Designates the optimal path from start to end
path_ = Back.CYAN + '.'
#Width and height of maze
width = 30
height = 20
#Initialize maze with walls, size will be width x height
#NOTE: point (x, y) of maze is reached by calling maze[y][x]
#   Essentially, flop the x and y point when referencing "maze"
maze = [[wall_ for x in range(width)] for y in range(height)]
#Randomize cost values for maze
minCost = 1
maxCost = 9
mazeCosts = [[random.randint(minCost, maxCost) for x in range(width)] for y in range(height)]
#Random start space is in top row -> (x, 0)
#Left and right-most spaces of row cannot be chosen
start = ( random.randint(1, width-2), 0)
#Will be overwritten later, declared here for clarity purposes
end = ()

#-----------------------------------------------------------------------------
#Generate the maze

#Initialize array for tiles that need to be checked
tiles = [start]

#Carve path through maze, based on Prim's Algorithm
#Loop while tiles is not empty
while tiles:
    #Pop next tile to check
    tile = tiles.pop( random.randint(0, len(tiles)-1) )
    #Get nearby walls from this tile
    nearbyWalls = getNearbyWalls(tile)
    
    #Tile has 3-4 nearby walls, thus can be made into a cell
    if len(nearbyWalls) >= 3:
        #For each nearby wall, add it to tiles array to check later
        for wall in getNearbyWalls(tile):
            tiles.append(wall)
        #Mark tile at (x, y) as a cell (maze[y][x] is point (x, y))
        maze[tile[1]][tile[0]] = cell_

#Remove some walls to allow multiple paths to exit
for x in range(width):
    for y in range(height):
        #Continue until a wall is found
        if maze[y][x] == cell_:
            continue
        
        nearbyWalls = getNearbyWalls((x, y))
        #If there are exactly two nearby walls
        if len(nearbyWalls) == 2:
            wall1, wall2 = nearbyWalls[0], nearbyWalls[1]
            #If walls are on opposite sides of source
            #   Essentially ignore "elbows" or "turns"
            if wall1[0] == wall2[0] or wall1[1] == wall2[1]:
                maze[y][x] = cell_
            
#Set top and bottom rows of maze to walls (except start and end)
for x in range(width):
    if (x, 0) != start:
        maze[0][x] = wall_
    if (x, height-1) != end:
        maze[height-1][x] = wall_

#Set left and right columns of maze to walls
for y in range(height):
    if (0, y) != start:
        maze[y][0] = wall_
    if (width-1, y) != end:
        maze[y][width-1] = wall_

#Generate maze exit
endPoints = []
for x in range(width):
    #If a space in 2nd to last row is empty, it is valid for an exit
    if maze[height-2][x] == cell_:
        endPoints.append((x, height-1))
        
#Randomly choose valid exit space and set it as a cell
end = endPoints[ random.randint(0, len(endPoints)-1) ]

#Find an exit with similar x position as the start point
#This is to aid in visualization of the search algorithms
#   Otherwise, completely random would be preferred
# closestX = width
# for e in endPoints:
#     xDist = abs(e[0] - start[0])
#     if xDist < closestX:
#         closestX = xDist
#         end = e
        
#Replace wall for the exit
maze[end[1]][end[0]] = cell_

printMaze()

#Get time in seconds
timeEnd = time.time()

print("Maze generated!")
print("Costs also generated, but not (yet) shown")
print("Start: {}\tEnd: {}".format(start, end))
print("Time: {:.6f}s".format(timeEnd - timeStart))
print("CPU usage: {} blocks".format(tracemalloc.get_traced_memory()))
input("Press enter... ")

#-----------------------------------------------------------------------------
#Breadth-First Search

tracemalloc.reset_peak()
timeStart = time.time()

#Iterations taken to find goal
i = 0
#"paths" is a queue (FIFO)
#Array of arrays (paths) holding points of tiles leading to goal
paths = [[start]]
#Initialize starting point
point = start
#Loop until end point is found (and there are paths to check)
while point != end and paths:
    
    #Retrieve next path to check in queue
    curr = paths.pop(0)
    #Get furthest point in path
    point = curr[-1]
    
    #If latest point has already been searched, skip this step
    if maze[point[1]][point[0]] == searched_:
        continue
    
    #Get list of nearby cells from last point in path
    nearbyCells = getNearbyCells(point)
    #For each nearby cell
    for c in nearbyCells:
        #Save a new path with a this nearby cell appended to end
        newPath = curr.copy()
        newPath.append(c)
        #Save this path to check later
        paths.append(newPath)
        
    #Mark space in maze as "searched"
    maze[point[1]][point[0]] = searched_
    #Count this loop
    i += 1

#Once the end point is reached, mark the optimal path taken
for point in curr:
    maze[point[1]][point[0]] = path_
    mazeCosts[point[1]][point[0]] = maxCost

timeEnd = time.time()

print("\n" * 10)
#os.system('cls')
printMaze()
print("Breadth-First Search")
print("Start: {}\tEnd: {}".format(start, end))
depth = len(curr) - 1
print("Depth: {}".format(depth))
print("Iterations: {}".format(i))
if point != end and not paths:
    print("FAILURE: END COULD NOT BE FOUND")
print("Time: {:.6f}s".format(timeEnd - timeStart))
print("CPU usage: {} blocks".format(tracemalloc.get_traced_memory()))
input("\nPress any key...")

#Reset maze to state before any search was done on it
resetSearch()

#-----------------------------------------------------------------------------
#Depth-First Search

tracemalloc.start()
timeStart = time.time()

#Iterations taken to find goal
i = 0
#"paths" is a stack (FILO)
#Array of arrays (paths) holding points of tiles leading to goal
paths = [[start]]
#Initialize starting point
point = start
#Loop until end point is found (and there are paths to check)
while point != end and paths:
    
    #Pop next path to be checked on stack
    curr = paths.pop(-1)
    #Get furthest point in path
    point = curr[-1]
    
    #If latest point has already been searched, skip this step
    if maze[point[1]][point[0]] == searched_:
        continue
    
    #Get list of nearby cells
    nearbyCells = getNearbyCells(point)
    #For each nearby cell, create a new path with it at the end
    for c in nearbyCells:
        #Save a new path with a new cell appended to end
        newPath = curr.copy()
        newPath.append(c)
        #Save this path to check later
        paths.append(newPath)
        
    #Place character for searched space
    maze[point[1]][point[0]] = searched_
    #Count this loop
    i += 1

#Once the end point is reached, mark the optimal path taken
for point in curr:
    maze[point[1]][point[0]] = path_

timeEnd = time.time()

print("\n" * 10)
#os.system('cls')
printMaze()
print("Depth-First Search")
print("Start: {}\tEnd: {}".format(start, end))
length = len(curr) - 1
print("Length: {}".format(length))
print("Iterations: {}".format(i))
if point != end and not paths:
    print("FAILURE: END COULD NOT BE FOUND")
print("Time: {:.6f}s".format(timeEnd - timeStart))
print("CPU usage: {} blocks".format(tracemalloc.get_traced_memory()))
input("\nPress any key...")

#Reset maze to state before any search was done on it
resetSearch()

#-----------------------------------------------------------------------------
#Uniform-Cost Search

tracemalloc.reset_peak()
timeStart = time.time()

#Iterations taken to find goal
i = 0
#Cost of path
cost = 0
#"paths" is a priority queue with [cost, (points of path)]
#Array of dictionaries holding path and it's cost
paths = [{"cost" : cost, "path" : [start]}]
#Initialize starting point
point = start
#Loop until end point is found (and there are paths to check)
while point != end and paths:
    
    #Find the path with the lowest cost
    smallestCost = width * height
    indexOfSmallestCost = 0
    for p in paths:
        if p["cost"] < smallestCost:
            smallestCost = p["cost"]
            indexOfSmallestCost = paths.index(p)
    
    #Pop lowest cost path in priority queue
    curr = paths.pop(indexOfSmallestCost)
    #Get the cost of current path
    cost = curr["cost"]
    #Get furthest point in path
    point = curr["path"][-1]
    
    #If latest point has already been searched, skip this step
    if maze[point[1]][point[0]] == searched_:
        continue
    
    #Get list of nearby cells
    nearbyCells = getNearbyCells(point)
    #For each nearby cell, create a new path with it at the end
    for c in nearbyCells:
        #Make shallow copy of current cost/ path dict
        newPath = curr.copy()
        #Get shallow copy of current path
        #   Since ["path"] is an array itself, must also make shallow copy
        newPath["path"] = curr["path"].copy()
        #Append new cell to this copy
        newPath["path"].append(c)
        #Add cost of new cell to total cost
        newPath["cost"] += mazeCosts[c[1]][c[0]]
        #Save this path to check later
        paths.append(newPath)
        
    #Place character for searched space
    maze[point[1]][point[0]] = searched_
    #Count this loop
    i += 1

#Once the end point is reached, mark the optimal path taken
for point in curr["path"]:
    maze[point[1]][point[0]] = path_

timeEnd = time.time()

print("\n" * 10)
#os.system('cls')
#printMaze()
printMazeWithCosts()
print("Uniform-Cost Search")
print("Start: {}\tEnd: {}".format(start, end))
cost = curr["cost"]
print("Cost: {}".format(cost))
print("Iterations: {}".format(i))
if point != end and not paths:
    print("FAILURE: END COULD NOT BE FOUND")
print("Time: {:.6f}s".format(timeEnd - timeStart))
print("CPU usage: {} blocks".format(tracemalloc.get_traced_memory()))
print("NOTE: The path taken in Breadth-First Search was changed to have a large cost.")
input("\nPress any key...")

#Reset maze to state before any search was done on it
resetSearch()

#-----------------------------------------------------------------------------
#Heuristic Search

tracemalloc.reset_peak()
timeStart = time.time()
    
#Iterations taken to find goal
i = 0
#Cost of path
cost = 0
#Get heuristic value from function
heur = h(start, end)
#"paths" is a priority queue with [cost, (points of path)]
#Array of dictionaries holding path it's cost, and it's heuristic value
paths = [{"heuristic" : heur , "cost" : cost, "path" : [start]}]
#Initialize starting point
point = start
#Loop until end point is found (and there are paths to check)
while point != end and paths:
    
    #Find the path with the lowest cost + heuristic value
    smallestCost = width * height
    indexOfSmallestCost = 0
    for p in paths:
        if p["cost"] + p["heuristic"] < smallestCost:
            smallestCost = p["cost"] + p["heuristic"]
            indexOfSmallestCost = paths.index(p)
    
    #Pop lowest cost path in priority queue
    curr = paths.pop(indexOfSmallestCost)
    #Get the heuristic value
    heur  = curr["heuristic"]
    #Get the cost of current path
    cost = curr["cost"]
    #Get furthest point in path
    point = curr["path"][-1]
    
    #If latest point has already been searched, skip this step
    if maze[point[1]][point[0]] == searched_:
        continue
    
    #Get list of nearby cells
    nearbyCells = getNearbyCells(point)
    #For each nearby cell, create a new path with it at the end
    for c in nearbyCells:
        #Make shallow copy of current cost/ path dict
        newPath = curr.copy()
        #Get shallow copy of current path
        #   Since ["path"] is an array itself, must also make shallow copy
        newPath["path"] = curr["path"].copy()
        #Append new cell to this copy
        newPath["path"].append(c)
        #Add cost of new cell to total cost
        newPath["cost"] += mazeCosts[c[1]][c[0]]
        #Calculate heuristic value
        newPath["heuristic"] = h(c, end)
        #Save this path to check later
        paths.append(newPath)
        
    #Place character for searched space
    maze[point[1]][point[0]] = searched_
    #Count this loop
    i += 1

#Once the end point is reached, mark the optimal path taken
for point in curr["path"]:
    maze[point[1]][point[0]] = path_

timeEnd = time.time()

print("\n" * 10)
#os.system('cls')
#printMaze()
printMazeWithCosts()
print("Heuristic Search")
print("Start: {}\tEnd: {}".format(start, end))
cost = curr["cost"]
print("Cost: {}".format(cost))
print("Iterations: {}".format(i))
if point != end and not paths:
    print("FAILURE: END COULD NOT BE FOUND")
print("Time: {:.6f}s".format(timeEnd - timeStart))
print("CPU usage: {} blocks".format(tracemalloc.get_traced_memory()))
print("h(n) = |x_n - x*| + |y_n - y*|", end = "\t\t")
print("(x_n, y_n) -> node n, (x*, y*) -> goal")
input("\nPress any key...")

#Reset maze to state before any search was done on it
resetSearch()