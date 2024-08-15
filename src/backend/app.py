from flask import Flask, request, jsonify
from flask_cors import CORS
from map import Map, get_map_data, astar_multitarget
import server

app = Flask(__name__)
CORS(app)

# Assuming you have some data structure to hold the grid state
grid_state = {
    "obstacles": [],
    "start": None,
    "goal": None
}

shelves = []

# Sample grid size, this should be configurable based on your needs
GRID_WIDTH = 20
GRID_HEIGHT = 20

# Initialize a default map
label = 'warehouse_0'
server.create_tables()
map_instance = get_map_data(label)

if map_instance:
    if map_instance.obstacles is not None and len(grid_state['obstacles']) == 0:
        for e in list(map_instance.obstacles):
            grid_state['obstacles'].append({'col':e[1],'row':e[0]})
    if map_instance.shelves is not None and len(shelves) == 0:
        positions = list(map_instance.shelves.keys())
        for i in range(len(map_instance.shelves)):
            x,y = positions[i][0], positions[i][1]
            shelves.append({
                'position': (x, y),
                'flower': map_instance.shelves[(x, y)]['flower'],
                'color': map_instance.shelves[(x, y)]['color'],
                'quantity': map_instance.shelves[(x, y)]['quantity']
            })
    print(f"Map '{label}' loaded successfully")
else:
    print(f"Map '{label}' does not exist. Creating a new map.")
    map_instance = Map(GRID_WIDTH, GRID_HEIGHT)
    map_instance.assign_id()
    # You can add initial obstacles or shelves to the new map if needed

@app.route('/connect_obs', methods=['GET'])
def connect_obs():
    return grid_state['obstacles']

@app.route('/connect_shel', methods=['GET'])
def connect_shel():
    global shelves
    return shelves

@app.route('/add_obstacle', methods=['POST'])
def add_obstacle():
    data = request.get_json()
    #print("Received data:", data)  # Add this line for debugging
    positions = data.get('positions', [])
    #print("Received positions:", positions)  # Add this line for debugging
    # Update your grid state with the new obstacle positions
    global shelves
    for pos in positions:
        x , y = pos['row'],pos['col']
        shelves = [shelf for shelf in shelves if shelf['position'] != (x,y)]
        map_instance.add_obstacle(x,y)
        grid_state["obstacles"].append(pos)
    return jsonify({"message": "Obstacles added", "obstacles": grid_state["obstacles"]})

@app.route('/remove_obstacle', methods=['POST'])
def remove_obstacle():
    data = request.get_json()
    position = data['position']
    if len(position) == 2:
        x , y = position['row'], position['col']
        map_instance.remove_obstacle(x,y)
    else:
        for pos in position:
            x , y = pos['row'],pos['col']
            map_instance.remove_obstacle(x,y)
    # Remove the obstacle from grid_state
    grid_state['obstacles'] = [obs for obs in grid_state['obstacles'] if obs != position]
    return jsonify({"message": "Obstacle removed", "obstacles": grid_state['obstacles']})

@app.route('/add_shelf', methods=['POST'])
def add_shelf():
    data = request.get_json()
    data = data['details']
    for pos in data:
        print(pos)
        x = pos['row']
        y = pos['col']
        flower = pos['flower']
        color = pos['color']
        quantity = pos['quantity']
        map_instance.add_shelf(x,y,flower,color,quantity)
        shelf = {
            'position': (x,y),
            'flower': flower,
            'color': color,
            'quantity': quantity
        }
        shelves.append(shelf)
    return jsonify({'message': 'Shelf added successfully', 'shelf': shelf}), 200

@app.route('/remove_shelf', methods=['POST'])
def remove_shelf():
    data = request.get_json()
    print(data)
    position = data['position']
    if len(position) == 2:
        x , y = position['row'],position['col']
        map_instance.remove_shelf(x,y)
    else:
        for pos in position:
            x , y = pos['row'],pos['col']
            map_instance.remove_shelf(x,y)
    # Remove the shelf from the shelves list
    global shelves
    shelves = [shelf for shelf in shelves if shelf['position'] != position]
    return jsonify({"message": "Shelf removed", "shelves": shelves})

#adjust this func
@app.route('/get_shelf', methods=['POST'])
def get_shelf():
    ret = []
    data = request.get_json()
    positions = data.get('selectedCells', [])
    #print(positions)
    if len(positions) != 0:
        for pos in positions:
            x , y = pos['row'], pos['col']
            temp = map_instance.get_shelf(x, y)
            print(temp)
            if temp != None:
                ret.append(temp)
            else:
                ret = None
    else:
        ret = shelves
    return jsonify(ret)

@app.route('/set_start_goal', methods=['POST'])
def set_start_goal():
    data = request.get_json()
    start = data.get('start', None)
    goal = data.get('goal', None)
    if start and goal:
        x1, y1 = start['row'], start['col']
        x2, y2 = goal['row'], goal['col']
        map_instance.set_start(x1, y1)
        map_instance.set_goal(x2, y2)
        grid_state["start"] = start
        grid_state["goal"] = goal
        return jsonify({"message": "Start and goal positions set", "start": start, "goal": goal})
    else:
        return jsonify({"message": "Invalid start or goal positions"}), 400

@app.route('/run_simulation', methods=['POST'])
def run_simulation():
    data = request.get_json()
    print(data['goals'])
    print("Obstacles:", map_instance.obstacles)
    print("Shelves:",map_instance.shelves)
    print("Start:", map_instance.start)
    print("Goal:", map_instance.goal)
    goals = [(e['row'],e['col']) for e in data['goals']]
    path = astar_multitarget(map_instance, goals)
    if path:
        return jsonify({'path': path})
    else:
        return jsonify({'message': 'No path found'}), 404

@app.route('/exit_simulation', methods=['POST'])
def exit_simulation():
    map_instance.reset_start()
    map_instance.reset_goal()
    return jsonify({"message": "Exiting the simulation"})

@app.route('/reset_map', methods=['POST'])
def reset_map():
    map_instance.obstacles = set()
    map_instance.shelves = {}
    map_instance.reset_start()
    map_instance.reset_goal()
    global grid_state
    grid_state = {
        "obstacles": [],
        "start": None,
        "goal": None
    }
    shelves = []
    server.reset_map(map_instance.id)
    return jsonify({"message": "Map and state reset"})

if __name__ == '__main__':
    app.run(debug=True)
