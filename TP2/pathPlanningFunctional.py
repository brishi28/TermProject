#modelled off of code snippets from 
#https://www.laurentluce.com/posts/solving-mazes-using-python-simple-recursivity-and-a-search/

import heapq


class Cell(object):
    '''
    @PARAM:
        x - x coordinate
        y - y coordinate
        valid - if the space is safe to drive on
    @VAR:
        parent - parent cell
        g - cost to move to this cell
        h - cost to move from this cell to the end
        f - heuristic f = g + h
    '''
    def __init__(self, x, y, valid):
        self.x = x
        self.y = y
        self.valid = valid
        self.parent = None
        self.g = 0
        self.h = 0
        self.f = 0

    def __repr__(self):
        return str((self.x, self.y, self.valid))

    def __lt__(self, other):
        return isinstance(other, Cell) and self.f < other.f

class PathPlan(object):
    '''
    @VAR:
        options - (x, y) coordinates that are viable movement options
        visited - visited coordinates
        cells - map of cells
    '''
    def __init__(self):
        #potential moves for the mapping algorithm
        self.options = []
        #add to queue sorted by heursitics
        heapq.heapify(self.options)
        self.visited = set()
        self.cells = []
        self.mapWidth = None
        self.mapHeight = None
    
    '''
    @PARAM:
        width - width of the map
        height - height of the map
        safe - list of safe (x, y) coordinates
        start - starting (x, y) coordinate
        end - ending (x, y) coordinate
    '''
    def initMap(self, width, height, safe, start, end):
        self.mapWidth = width
        self.mapHeight = height
        for y in range(height+1):
            self.cells.append([])
            for x in range(width+1):
                if (x, y) in safe:
                    self.cells[y] += [Cell(x, y, True)]
                else:
                    self.cells[y] += [Cell(x, y, False)]
        print(self.cells)
        self.start = self.cells[start[1]][start[0]]
        self.end = self.cells[end[1]][end[0]]

    '''
    Calculates distance in terms of spaces and multiplies it by distace
    @RETURN: heuristic value, h, for a given cell
    '''
    def getHeuristic(self, cell):
        return 30 * (abs(cell.x - self.end.x) + abs(cell.y - self.end.y))

    '''
    @RETURN: list of adjacent cells including diagonals
    '''
    def getAdjacentCells(self, cell):
        result = []
        if cell.x < self.mapWidth - 1:
            result += [self.cells[cell.y][cell.x + 1]]
        if cell.x < self.mapWidth - 1 and cell.y > 0:
            result += [self.cells[cell.y - 1][cell.x + 1]]
        if cell.y > 0:
            result += [self.cells[cell.y - 1][cell.x]]
        if cell.x > 0 and cell.y > 0:
            result += [self.cells[cell.y - 1][cell.x - 1]]
        if cell.x > 0:
            result += [self.cells[cell.y][cell.x - 1]]
        if cell.x > 0 and cell.y < self.mapHeight - 1:
            result += [self.cells[cell.y + 1][cell.x - 1]]
        if cell.y < self.mapHeight - 1:
            result += [self.cells[cell.y + 1][cell.x]]
        if cell.x < self.mapWidth - 1 and cell.y < self.mapHeight - 1:
            result += [self.cells[cell.y + 1][cell.x + 1]]
        return result

    '''
    Updates the heuristics and parent for an adjacent cell
    '''
    def updateCell(self, adjacent, cell):
        adjacent.g = cell.g + 10
        adjacent.h = self.getHeuristic(adjacent)
        adjacent.parent = cell
        adjacent.f = adjacent.h + adjacent.g

    '''
    Modified from orignal code
    @RETURN: a list of tuples traced back to the beginnign via the parent node
    '''
    def getPath(self):
        cell = self.end
        path = [(cell.x, cell.y)]
        while cell.parent is not self.start:
            cell = cell.parent
            path.append((cell.x, cell.y))

        path.append((self.start.x, self.start.y))
        path.reverse()
        return path

    '''
    Path plan to the given (x, y) coordinate
    Queue places priority on different moves based on their heuristic
    Heapq portions were based off of the example, as I have not worked with it in the past
    '''
    def solve(self):
        #make a queue with the start node as the first option
        heapq.heappush(self.options, (self.start.f, self.start))
        while len(self.options):
            f, cell = heapq.heappop(self.options)
            self.visited.add(cell)
            #base case
            if cell is self.end:
                return self.getPath()
            adjacentCells = self.getAdjacentCells(cell)
            #possible moves
            for adjacentCell in adjacentCells:
                #don't return to previous cells
                if adjacentCell.valid and adjacentCell not in self.visited:
                    #if the cell is a potential option already, determine whether it is more
                        #efficient using this routing
                    if (adjacentCell.f, adjacentCell) in self.options:
                        if adjacentCell.g > cell.g + 10:
                            self.updateCell(adjacentCell, cell)
                    else:
                        #add it to the options queue with a given heuristic
                        self.updateCell(adjacentCell, cell)
                        heapq.heappush(self.options, (adjacentCell.f, adjacentCell))