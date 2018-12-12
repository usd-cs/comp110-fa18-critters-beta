"""
Module: critters

A Python implementation of Critters!
"""
import random
from tkinter import *
from tkinter.font import Font
from enum import Enum
from copy import deepcopy

food_coma_period = 2 # how many times critter can eat before falling asleep
food_comma_sleep_time = 20  # how long a critter sleeps after eating too much
gestation_period = 40 # how long the mating period is for critters

after_id = None
root = None
world = None

turn_time_ms = 1000

turn_number = 0
turn_string = None

bear_stats_string = None
cheetah_stats_string = None
lion_stats_string = None
torero_stats_string = None

class Direction(Enum):
    NORTH = 1
    EAST = 2
    SOUTH = 3
    WEST = 4
    CENTER = 5

class Attack(Enum):
    ROAR = 1
    POUNCE = 2
    SCRATCH = 3
    FORFEIT = 4


class Critter:
    def __init__(self, location):
        self.x = location[0]
        self.y = location[1]

    def __str__(self):
        """
        Returns a string representation of this critter.
        This representation is used when fighting another critter.
        """
        return "?"

    def get_move(self, neighbors):
        """ Gets the next move the critter wants to make. """
        return Direction.CENTER

    def fight(self, opponent):
        """ Gets the next fight move for the critter. """
        return Attack.FORFEIT

    def eat(self):
        """ Returns True if the critter wants to eat, False otherwise. """
        return False

    def get_color(self):
        return "Blue"

    def move_to(self, x, y):
        """ Changes the location of this Critter. """
        self.x = x
        self.y = y


class Cow(Critter):
    def __init__(self, location):
        super().__init__(location)
        self.dirs = [Direction.NORTH, Direction.SOUTH,
                     Direction.EAST, Direction.WEST]
        self.move_number = 0

    def __str__(self):
        return "M"

    def get_move(self, neighbors):
        i = self.move_number % 4
        self.move_number = self.move_number + 1
        return self.dirs[i]

    def fight(self, opponent):
        return random.choice([Attack.POUNCE, Attack.SCRATCH])

    def get_color(self):
        return "brown"

class ScaredCat(Critter):
    # TODO: implement this

    def __init__(self, location):
        super().__init__(location)

class World:
    """
    Representation of a 2D grid world containing critters.
    """

    def __init__(self, width, height, window, food_probability):
        """
        Initializes our world to have the given dimensions, with each spot
        in the world having a food_probability chance of containing food.

        The world starts out without any critters: use the add_critter method
        to start populating the world.
        """
        self.width = width
        self.height = height
        self.food_probability = food_probability
        self.critter_grid = [[None] * width for _ in range(height)]
        self.critter_location = {}

        # each spot in the world will have food_probability chance of having food
        self.food_grid = [[False] * width for _ in range(height)]
        for x in range(width):
            for y in range(height):
                if random.random() < food_probability:
                    self.food_grid[y][x] = True


        self.sleep_time = {} # map critter to how many more turns to sleep
        self.gestate_time = {} # map critter to how many more turns of mating
        self.pregnant_critters = [] # list of pregnant critters
        self.amount_eaten = {} # map critter to how much they have eaten

        # map from critter type to amount that are alive
        self.num_alive = {"Cow": 0, "ScaredCat": 0, "Cheetah": 0, "Torero": 0}

        # map from critter type to amount they've eaten
        self.num_eaten = {"Cow": 0, "ScaredCat": 0, "Cheetah": 0, "Torero": 0}

        # map from critter type to amount of fights won
        self.num_wins = {"Cow": 0, "ScaredCat": 0, "Cheetah": 0, "Torero": 0}

        # start with no critters and every spot in the world is open
        self.critters = []
        self.open_spots = [(x, y) for x in range(width)
                           for y in range(height)]

        # creates a GUI for us to draw our world on
        self.canvas = Canvas(window, bg="lawn green", height=(14*height),
                             width=(14*width), bd=0, relief='sunken',
                             highlightthickness=0)
        self.canvas.pack()


    def clear(self):
        """
        Clears the world, resetting everything back to an initial state.
        DO NOT USE THIS RIGHT NOW, AS IT HAS NOT BEEN TESTED!
        """
        self.critter_grid = [[None] * self.width for _ in range(self.height)]

        self.food_grid = [[False] * self.width for _ in range(self.height)]
        for x in range(self.width):
            for y in range(self.height):
                if random.random() < self.food_probability:
                    self.food_grid[y][x] = True

        self.sleep_time = {} # map critter to how many more turns to sleep
        self.gestate_time = {} # map critter to how many more turns of mating
        self.pregnant_critters = [] # list of pregnant critters
        self.amount_eaten = {} # map critter to how much they have eaten

        # start with no critters and every spot in the world is open
        self.critters = []
        self.open_spots = [(x, y) for x in range(self.width)
                           for y in range(self.height)]

    def get_stats(self, critter_type):
        """
        Returns a tuple of stats for the given critter type, e.g. "Cow".
        """
        return self.num_alive[critter_type], self.num_wins[critter_type], \
            self.num_eaten[critter_type]

    def get_open_spot(self):
        """ Returns a random open spot in the world. """
        location = random.choice(self.open_spots)
        self.open_spots.remove(location)
        return location

    def add_critter(self, critter, location):
        """ Places a new critter in the world at the given location. """
        self.critters.append(critter)
        self.critter_location[critter] = location
        self.critter_grid[location[1]][location[0]] = critter
        self.amount_eaten[critter] = 0
        self.num_alive[type(critter).__name__] += 1

    def food_at(self, x, y):
        """ Returns True if there is food at the given location, False
        otherwise. """
        x = x % self.width
        y = y % self.height
        return self.food_grid[y][x]

    def feed_critter(self, critter, x, y):
        """
        Feeds the given critter the food at the given location.

        Returns True if the critter fell asleep because of eating, False
        otherwise.
        """
        x = x % self.width
        y = y % self.height
        if not self.food_grid[y][x]:
            raise RuntimeError("Tried removing food where there was none.")
        else:
            self.num_eaten[type(critter).__name__] += 1
            self.food_grid[y][x] = False
            self.amount_eaten[critter] += 1

            if self.amount_eaten[critter] % food_coma_period == 0:
                self.sleep_time[critter] = food_comma_sleep_time
                return True
            else:
                return False

    def rest_critters(self):
        """
        Marks sleeping critters as having rested for an additional turn.
        If they have been sleeping long enough, the critter will be woken up.
        """
        for critter in list(self.sleep_time.keys()):
            if self.sleep_time[critter] == 0:
                del self.sleep_time[critter]
            else:
                self.sleep_time[critter] -= 1

    def mate_critters(self, mother, father):
        """
        Marks two critters as mating, setting one as the mother and the
        other as the father. The mother is the critter that spawn off the baby
        at the end of the gestation period.
        """
        self.pregnant_critters.append(mother)
        self.gestate_time[mother] = gestation_period
        self.gestate_time[father] = gestation_period

    def gestate_critters(self):
        """
        Marks mating critters as having gestated for an additional turn.

        If they have been gestating long enough, they a new baby critter will
        be formed.
        """
        for critter in list(self.gestate_time.keys()):
            if self.gestate_time[critter] == 0:
                del self.gestate_time[critter]

                # if this is the mother, a new baby critter will be added to
                # the world.
                if critter in self.pregnant_critters:
                    self.pregnant_critters.remove(critter)
                    baby = deepcopy(critter)

                    # TODO: get closest open spot to this critter
                    baby_x, baby_y = self.get_open_spot()
                    self.add_critter(baby, (baby_x, baby_y))
                    baby.move_to(baby_x, baby_y)

            else:
                self.gestate_time[critter] -= 1

    def get_critter(self, x, y):
        """ Returns the critter at the given location, or None if one isn't
        there. """
        x = x % self.width
        y = y % self.height
        return self.critter_grid[y][x]

    def move_critter(self, critter, new_x, new_y):
        """ Move the given critter to the given location. """
        new_x = new_x % self.width
        new_y = new_y % self.height

        curr_x, curr_y = self.critter_location[critter]
        self.open_spots.append((curr_x, curr_y))
        self.critter_grid[new_y][new_x] = critter
        self.critter_grid[curr_y][curr_x] = None
        self.critter_location[critter] = (new_x, new_y)
        critter.move_to(new_x, new_y)

    def remove_critter(self, critter):
        """ Remove this critter from the world, for its time has come. """
        curr_x, curr_y = self.critter_location[critter]
        self.open_spots.append((curr_x, curr_y))
        self.critter_grid[curr_y][curr_x] = None
        del self.critter_location[critter]

    def bury_critter(self, critter):
        """ Remove all traces of critter from the world. """
        self.num_alive[type(critter).__name__] -= 1

        world.critters.remove(critter)

        if critter in self.sleep_time:
            del self.sleep_time[critter]
        if critter in self.gestate_time:
            del self.gestate_time[critter]
        if critter in self.pregnant_critters:
            self.pregnant_critters.remove(critter)
        if critter in self.amount_eaten:
            del self.amount_eaten[critter]

    def is_sleeping(self, critter):
        """ Returns True if the critter is sleeping, False otherwise. """
        return critter in self.sleep_time

    def is_mating(self, critter):
        """ Returns True if the critter is mating, False otherwise. """
        return critter in self.gestate_time

    def get_location(self, critter):
        """ Returns the location of the critter in the world. """
        return self.critter_location[critter]

    def draw(self):
        """ Redraws the world on the canvas. """
        regular_font = Font(family="Arial", size=-14)
        small_font = Font(family="Arial", size=-7)
        self.canvas.delete(ALL)
        for y in range(self.height):
            for x in range(self.width):
                # draw food (if any) then critter (if any)
                if self.food_grid[y][x]:
                    self.canvas.create_text(14*x+7, 14*y+7, text=".",
                                            font=regular_font,
                                            fill="DarkOrchid3")

                val = self.critter_grid[y][x]
                if val is not None:
                    self.canvas.create_text(14*x+7, 14*y+7, text=str(val),
                                            font=regular_font,
                                            fill=val.get_color())
                    # add embellishment to indicate critter is sleeping
                    if val in self.sleep_time:
                        self.canvas.create_text(14*x+7, 14*y+7,
                                                text="ZZz",
                                                font=small_font,
                                                fill="black")
                    elif val in self.gestate_time:
                        self.canvas.create_text(14*x+7, 14*y+7,
                                                text="<3",
                                                font=small_font,
                                                fill="red")

def adjust_turn_time(scalar):
    """ Adjusts the amount of ms for each turn. """
    global turn_time_ms
    turn_time_ms = 1000 // int(scalar)


def create_window():
    """ Returns a new GUI window. """
    root = Tk()
    root.title("Critters Simulator")
    root.geometry("975x750")

    # make sure this pops in front of all other windows
    root.lift()
    root.attributes("-topmost", True)
    root.grid_propagate(0)

    # Set up the frame where the world canvase will go
    canvas_frame = Frame(root)
    canvas_frame.grid(row=0, column=0)

    # set up frame with controls and turn count (bottom part of window)
    controls = Frame(root)
    controls.grid(row=1, column=0)

    turn_speed_slider = Scale(controls, from_=1, to=10, label="Turn Speed",
                              showvalue=0, orient=HORIZONTAL,
                              command=adjust_turn_time)
    turn_speed_slider.grid(row=0, column=0)

    global turn_string
    turn_string = StringVar()
    turn_string.set("Turn: 0")
    turn_label = Label(controls, textvariable=turn_string)
    turn_label.grid(row=0, column=1)

    start_button = Button(controls, text="Start", command=sim_loop)
    start_button.grid(row=0, column=2)
    stop_button = Button(controls, text="Stop", command=stop_sim_loop)
    stop_button.grid(row=0, column=3)
    tick_button = Button(controls, text="Tick", command=do_turn)
    tick_button.grid(row=0, column=4)

    #reset_button = Button(controls, text="Reset", command=reset_simulation)
    #reset_button.grid(row=0, column=5)

    # set up the frame with simulation stats, to go on the right side of the
    # window
    stats = Frame(root, width=200)
    stats.grid(row=0, column=1, rowspan=2, padx=15, sticky=N)

    l = LabelFrame(stats, text="Cow", width=100)
    l.pack(fill='x', expand=True)
    global bear_stats_string
    bear_stats_string = StringVar()
    bear_stats_string.set("Alive: \nKills: \nEaten: \nPoints: ")
    bear_stats = Label(l, textvariable=bear_stats_string, justify=LEFT)
    bear_stats.pack(fill='x', expand=True)
    bear_stats.pack_propagate(False)

    l2 = LabelFrame(stats, text="Cheetah", width=100)
    l2.pack(fill='x', expand=True)
    global cheetah_stats_string
    cheetah_stats_string = StringVar()
    cheetah_stats_string.set("Alive: \nKills: \nEaten: \nPoints: ")
    cheetah_stats = Label(l2, textvariable=cheetah_stats_string, justify=LEFT)
    cheetah_stats.pack(fill='x', expand=True)

    l3 = LabelFrame(stats, text="ScaredCat", width=100)
    l3.pack(fill='x', expand=True)
    global lion_stats_string
    lion_stats_string = StringVar()
    lion_stats_string.set("Alive: \nKills: \nEaten: \nPoints: ")
    lion_stats = Label(l3, textvariable=lion_stats_string, justify=LEFT)
    lion_stats.pack(fill='x', expand=True)
    lion_stats.pack_propagate(False)

    l4 = LabelFrame(stats, text="Torero", width=100)
    l4.pack(fill='x', expand=True)
    global torero_stats_string
    torero_stats_string = StringVar()
    torero_stats_string.set("Alive: \nKills: \nEaten: \nPoints: ")
    torero_stats = Label(l4, textvariable=torero_stats_string, justify=LEFT)
    torero_stats.pack(fill='x', expand=True)

    return root, canvas_frame


def sim_loop():
    """
    Starts doing turns of the simulation, waiting turn_time_ms between each
    turn.
    """
    global root
    global after_id
    do_turn()
    after_id = root.after(turn_time_ms, sim_loop)

def stop_sim_loop():
    """ Stops the simulation from doing more turns. """
    global after_id
    if after_id:
        root.after_cancel(after_id)
        after_id = None

def reset_simulation():
    """
    Resets the similator to a beginning state.
    DO NOT USE THIS FUNCTION!
    """
    global world
    global turn_number
    stop_sim_loop()
    num_critters = len(world.critters)
    world.clear()
    initialize_critters(num_critters)
    turn_number = 0
    world.draw()

def battle(critter1, critter2):
    """
    Performs a fight between two critters.

    Returns a tuple of (winner, loser).
    """

    c1_attack = critter1.fight(str(critter2))
    c2_attack = critter2.fight(str(critter1))

    if c1_attack == c2_attack:
        if random.random() < 0.5:
            return critter1, critter2
        else:
            return critter2, critter1
    elif c2_attack == Attack.FORFEIT \
        or c1_attack == Attack.ROAR and c2_attack == Attack.SCRATCH \
        or c1_attack == Attack.SCRATCH and c2_attack == Attack.POUNCE \
        or c1_attack == Attack.POUNCE and c2_attack == Attack.ROAR:
        return critter1, critter2
    else:
        return critter2, critter1

def do_turn():
    """ Performs a single turn of the simulation. """
    global world

    world.rest_critters()
    world.gestate_critters()

    dead_critters = []
    for critter in world.critters:
        if critter in dead_critters:
            continue
        elif world.is_sleeping(critter) or world.is_mating(critter):
            continue

        # check if there's food at the critter's location
        curr_x, curr_y = world.get_location(critter)
        if world.food_at(curr_x, curr_y):
            # if critter wants to eat, feed it
            if critter.eat():
                fell_asleep = world.feed_critter(critter, curr_x, curr_y)
                if fell_asleep:
                    continue

        # Determine who this critter's neighbors are so we can give this
        # information to them when they are going to decide how to move.
        neighbors = {}

        north_neighbor = world.get_critter(curr_x, curr_y-1)
        if north_neighbor is not None:
            north_neighbor = str(north_neighbor)
        neighbors[Direction.NORTH] = north_neighbor

        east_neighbor = world.get_critter(curr_x+1, curr_y)
        if east_neighbor is not None:
            east_neighbor = str(east_neighbor)
        neighbors[Direction.EAST] = east_neighbor

        south_neighbor = world.get_critter(curr_x, curr_y+1)
        if south_neighbor is not None:
            south_neighbor = str(south_neighbor)
        neighbors[Direction.SOUTH] = south_neighbor

        west_neighbor = world.get_critter(curr_x-1, curr_y)
        if west_neighbor is not None:
            west_neighbor = str(west_neighbor)
        neighbors[Direction.WEST] = west_neighbor


        move = critter.get_move(neighbors)

        if move == Direction.NORTH:
            dest_x, dest_y = curr_x, curr_y-1
        elif move == Direction.EAST:
            dest_x, dest_y = curr_x+1, curr_y
        elif move == Direction.SOUTH:
            dest_x, dest_y = curr_x, curr_y+1
        elif move == Direction.WEST:
            dest_x, dest_y = curr_x-1, curr_y
        else:
            # Critter didn't want to move so nothing left to do
            continue

        other_critter = world.get_critter(dest_x, dest_y)
        if other_critter == None:
            world.move_critter(critter, dest_x, dest_y)
        else:
            if type(critter) != type(other_critter):
                # battle if they are different critter types
                if not world.is_sleeping(other_critter):
                    winner, loser = battle(critter, other_critter)
                else:
                    # if other critter was sleeping, they automatically lose
                    winner, loser = critter, other_critter

                # FIXME: make this a world method
                world.num_wins[type(winner).__name__] += 1

                dead_critters.append(loser)
                world.remove_critter(loser)

            else:
                # there is another critter of the same type here.
                if not world.is_mating(other_critter):
                    world.mate_critters(critter, other_critter)
                continue

    for critter in dead_critters:
        world.bury_critter(critter)

    global turn_number
    turn_number += 1
    turn_string.set("Turn: " + str(turn_number))

    # update stats in right side of window
    global bear_stats_string
    alive, kills, eaten = world.get_stats("Cow")
    total_points = alive + kills + eaten
    bear_stats_string.set("Alive: %d\nKills: %d\nEaten: %d\nPoints: %d" %
                          (alive, kills, eaten, total_points))

    global cheetah_stats_string
    alive, kills, eaten = world.get_stats("Cheetah")
    total_points = alive + kills + eaten
    cheetah_stats_string.set("Alive: %d\nKills: %d\nEaten: %d\nPoints: %d" %
                             (alive, kills, eaten, total_points))

    global lion_stats_string
    alive, kills, eaten = world.get_stats("ScaredCat")
    total_points = alive + kills + eaten
    lion_stats_string.set("Alive: %d\nKills: %d\nEaten: %d\nPoints: %d" %
                          (alive, kills, eaten, total_points))

    global torero_stats_string
    alive, kills, eaten = world.get_stats("Torero")
    total_points = alive + kills + eaten
    torero_stats_string.set("Alive: %d\nKills: %d\nEaten: %d\nPoints: %d" %
                            (alive, kills, eaten, total_points))

    world.draw()

def initialize_critters(num_each_type):
    """ Create and randomly place critters. """
    global world
    for i in range(num_each_type * 2):
        critter_loc = world.get_open_spot()
        if i%2 == 0:
            critter = Cow(critter_loc)
        else:
            critter = ScaredCat(critter_loc)
        world.add_critter(critter, critter_loc)


def simulate(world_width, world_height, num_each_type):
    """
    Perform simulation of a world with num_each_type of 4 different types
    of critters.
    """
    global root
    root, canvas_frame = create_window()

    global world
    world = World(world_width, world_height, canvas_frame, 0.05)

    initialize_critters(num_each_type)

    world.draw()
    root.mainloop()

if __name__ == "__main__":
    simulate(60, 50, 25)
