import random
import heapq
import psycopg2
import server

class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.obstacles = set()
        self.shelves = {}  # Add a dictionary to store shelves
        self.start = None
        self.goal = None
        self.id = 0

    def assign_id(self):
        server.create_map(self.width,self.height,'warehouse_0')

    def add_obstacle(self, x, y):
        if (x, y) in self.shelves:
            self.remove_shelf(x, y)
            server.remove_shelf(self.id, x, y) 
        self.obstacles.add((x, y))
        server.add_obstacle(self.id, x, y)

    def remove_obstacle(self, x, y):
        if (x, y) in self.obstacles:
            self.obstacles.remove((x, y))
            server.remove_obstacle(self.id, x, y) 

    def add_shelf(self, x, y, flower, color, quantity):  # Modified to include quantity
        self.obstacles.add((x, y))  # Shelf acts as an obstacle
        self.shelves[(x, y)] = {'flower': flower, 'color': color, 'quantity': quantity}
        server.add_shelf(self.id, x, y, flower, color, quantity)

    def remove_shelf(self, x, y):
        if (x, y) in self.shelves:
            del self.shelves[(x, y)]
            self.obstacles.remove((x, y)) # Also remove it as an obstacle
            server.remove_shelf(self.id, x, y)

    def get_shelf(self, x, y):
        nx, ny = x, y
        if (nx, ny) in self.shelves:
            return self.shelves[(nx, ny)]
        else:
            return None
    
    def set_start(self, x, y):
        self.start = (x, y)

    def reset_start(self):
        self.start = None

    def set_goal(self, x, y):
        self.goal = (x, y)

    def reset_goal(self):
        self.goal = None

    def is_valid(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height and (x, y) not in self.obstacles

    def neighbors(self, x, y):
        result = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if self.is_valid(nx, ny):
                result.append((nx, ny))
        return result

    def is_near_shelf(self, x, y):  # New function to check proximity to a shelf
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in self.shelves:
                return True
        return False

    def interact_with_shelf(self, x, y):  # Modified to work in neighborhood
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in self.shelves:
                shelf_info = self.shelves[(nx, ny)]
                return f"You are near shelf '{shelf_info['label']}'. It contains: {shelf_info['quantity']} of {shelf_info['flower']}"
        return "There is no shelf nearby."

    def take_flower(self, x, y, n):  # New function to take flowers from a shelf
        nx, ny = x, y
        if (nx, ny) in self.shelves:
            shelf = self.shelves[(nx, ny)]
            if shelf['quantity'] >= n:
                shelf['quantity'] -= n
                return f"You took {n} of {shelf['flower']} from shelf '{shelf['label']}'."
            else:
                return f"Not enough {shelf['flower']} on shelf '{shelf['label']}'."
        return "No shelf found at this location."

    # Function to query the database and retrieve the Map, Obstacles, and Shelves
def get_map_data(label):
    conn_params = server.load_db_credentials('db_credentials.txt')
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()

        # Check if the map exists
        cur.execute("SELECT map_id, width, height FROM maps WHERE label = %s", (label,))
        map_data = cur.fetchone()
        if map_data:
            map_id, width, height = map_data
            print(f"Map found: ID={map_id}, Width={width}, Height={height}, Label={label}")

            # Create a Map instance
            map_instance = Map(width, height)
            map_instance.id = map_id

            # Get obstacles
            cur.execute("SELECT x, y FROM obstacles WHERE map_id = %s", (map_id,))
            obstacles = cur.fetchall()
            for x, y in obstacles:
                map_instance.add_obstacle(x, y)

            # Get shelves
            cur.execute("SELECT x, y, flower, color, quantity FROM shelves WHERE map_id = %s", (map_id,))
            shelves = cur.fetchall()
            for x, y, flower, color, quantity in shelves:
                map_instance.add_shelf(x, y, flower, color, quantity)

            return map_instance
        else:
            print(f"No map found with label '{label}'")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

def reconstruct_path(came_from, current):
    total_path = [current]
    while current in came_from:
        current = came_from[current]
        total_path.insert(0, current)
    return total_path

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(map):
    open_set = []
    heapq.heappush(open_set, (0, map.start))
    came_from = {}
    cost_so_far = {map.start: 0}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == map.goal:
            return reconstruct_path(came_from, current)

        for neighbor in map.neighbors(*current):
            new_cost = cost_so_far[current] + 1  # Assuming cost of 1 to move to neighbor
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + heuristic(map.goal, neighbor)
                heapq.heappush(open_set, (priority, neighbor))
                came_from[neighbor] = current

    return None  # No path found

def astar_multitarget(map, targets):
    # Handle the case where targets is None or empty
    if targets is None or len(targets) == 0:
        map.set_start(*map.start)  # Ensure start and goal are set correctly
        map.set_goal(*map.goal)
        return astar(map)

    # Calculate pairwise distances
    locations = [map.start] + targets + [map.goal]
    distances = [[heuristic(a, b) for b in locations] for a in locations]

    # Find optimal target order (replace with a more efficient algorithm if needed)
    optimal_order = [0]  # Start with the start position
    remaining_targets = list(range(1, len(locations) - 1))
    while remaining_targets:
        current = optimal_order[-1]
        next_target = min(remaining_targets, key=lambda i: distances[current][i])
        optimal_order.append(next_target)
        remaining_targets.remove(next_target)
    optimal_order.append(len(locations) - 1)  # End with the goal position

    # Perform A* search between consecutive locations
    total_path = []
    for i in range(len(optimal_order) - 1):
        start_idx = optimal_order[i]
        goal_idx = optimal_order[i + 1]
        map.set_start(*locations[start_idx])
        map.set_goal(*locations[goal_idx])
        path = astar(map)
        if path:
            total_path.extend(path[:-1])  # Avoid duplicate nodes
        else:
            return None  # No path found

    total_path.append(locations[-1])  # Add the goal position
    return total_path