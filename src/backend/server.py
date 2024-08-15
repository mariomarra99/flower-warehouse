import psycopg2
import map

# Function to load database credentials from a file
def load_db_credentials(file_path):
    with open(file_path, 'r') as file:
        line = file.readline().strip()
        credentials = line.split(',')
        return {
            'dbname': credentials[0],
            'user': credentials[1],
            'password': credentials[2],
            'host': credentials[3],
            'port': credentials[4]
        }

# Load credentials from db_credentials.txt
conn_params = load_db_credentials('db_credentials.txt')

def create_tables():
    conn_params = load_db_credentials('db_credentials.txt')
    # Connect to your PostgreSQL database
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    # Check if the "maps" table exists
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'maps'
        );
    """)
    maps_exists = cur.fetchone()[0]
    # Check if the "obstacles" table exists
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'obstacles'
        );
    """)
    obstacles_exists = cur.fetchone()[0]
    # Check if the "shelves" table exists
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'shelves'
        );
    """)
    shelves_exists = cur.fetchone()[0]
    # Create the "maps" table if it doesn't exist
    if not maps_exists:
        cur.execute("""
            CREATE TABLE maps (
                map_id SERIAL PRIMARY KEY,
                width INT NOT NULL,
                height INT NOT NULL,
                label VARCHAR(255)
            );
        """)
        print("Table 'maps' created successfully.")
    # Create the "obstacles" table if it doesn't exist
    if not obstacles_exists:
        cur.execute("""
            CREATE TABLE obstacles (
                obstacle_id SERIAL PRIMARY KEY,
                map_id INT REFERENCES maps(map_id) ON DELETE CASCADE,
                x INT NOT NULL,
                y INT NOT NULL,
                UNIQUE(map_id, x, y)
            );
        """)
        print("Table 'obstacles' created successfully.")
    # Create the "shelves" table if it doesn't exist
    if not shelves_exists:
        cur.execute("""
            CREATE TABLE shelves (
                shelf_id SERIAL PRIMARY KEY,
                map_id INT REFERENCES maps(map_id) ON DELETE CASCADE,
                x INT NOT NULL,
                y INT NOT NULL,
                flower VARCHAR(100),
                color VARCHAR(50),
                quantity INT NOT NULL,
                UNIQUE(map_id, x, y),
                CONSTRAINT fk_obstacle FOREIGN KEY (map_id, x, y)
                REFERENCES obstacles(map_id, x, y) ON DELETE CASCADE
            );
        """)
        print("Table 'shelves' created successfully.")

    # Commit the transaction and close the connection
    conn.commit()
    cur.close()
    conn.close()

# Function to create a new map
def create_map(width, height, label=None):
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO maps (width, height, label) VALUES (%s, %s, %s) RETURNING map_id",
            (width, height, label)
        )
        map_id = cur.fetchone()[0]
        conn.commit()
        print(f"Map created with ID: {map_id}")
        return map_id
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

# Function to delete a map
def delete_map(map_id):
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        cur.execute("DELETE FROM maps WHERE map_id = %s", (map_id,))
        conn.commit()
        print(f"Map with ID {map_id} deleted")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

# Function to add an obstacle
def add_obstacle(map_id, x, y):
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO obstacles (map_id, x, y) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
            (map_id, x, y)
        )
        conn.commit()
        print(f"Obstacle added at ({x}, {y}) on map {map_id}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

# Function to remove an obstacle
def remove_obstacle(map_id, x, y):
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM obstacles WHERE map_id = %s AND x = %s AND y = %s",
            (map_id, x, y)
        )
        conn.commit()
        print(f"Obstacle removed from ({x}, {y}) on map {map_id}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

# Function to add a shelf
def add_shelf(map_id, x, y, flower, color, quantity):
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        # Add obstacle first
        cur.execute(
            "INSERT INTO obstacles (map_id, x, y) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
            (map_id, x, y)
        )
        # Add shelf
        cur.execute(
            '''
            INSERT INTO shelves (map_id, x, y, flower, color, quantity)
            VALUES (%s, %s, %s, %s, %s, %s)
            ''',
            (map_id, x, y, flower, color, quantity)
        )
        conn.commit()
        print(f"Shelf added at ({x}, {y}) on map {map_id}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

# Function to remove a shelf
def remove_shelf(map_id, x, y):
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM shelves WHERE map_id = %s AND x = %s AND y = %s",
            (map_id, x, y)
        )
        # Also remove the obstacle
        cur.execute(
            "DELETE FROM obstacles WHERE map_id = %s AND x = %s AND y = %s",
            (map_id, x, y)
        )
        conn.commit()
        print(f"Shelf and obstacle removed from ({x}, {y}) on map {map_id}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

# Function to reset a map by deleting all obstacles and shelves
def reset_map(map_id):
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        
        # Delete all shelves associated with the map
        cur.execute("DELETE FROM shelves WHERE map_id = %s", (map_id,))
        
        # Delete all obstacles associated with the map
        cur.execute("DELETE FROM obstacles WHERE map_id = %s", (map_id,))
        
        conn.commit()
        print(f"Map with ID {map_id} has been reset (all obstacles and shelves deleted).")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()
        
# Function to query and verify operations
def query_map(map_id):
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        cur.execute("SELECT * FROM maps WHERE map_id = %s", (map_id,))
        map_data = cur.fetchone()
        print(f"Map: {map_data}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

def query_obstacles(map_id):
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        cur.execute("SELECT * FROM obstacles WHERE map_id = %s", (map_id,))
        obstacles = cur.fetchall()
        print(f"Obstacles on map {map_id}: {obstacles}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

def query_shelves(map_id):
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        cur.execute("SELECT * FROM shelves WHERE map_id = %s", (map_id,))
        shelves = cur.fetchall()
        print(f"Shelves on map {map_id}: {shelves}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

# Example usage with verification
if __name__ == "__main__":
    create_tables()

    # Create a new map
    map_id = create_map(10, 15, 'Test Map')
    query_map(map_id)

    # Add obstacles
    add_obstacle(map_id, 3, 4)
    add_obstacle(map_id, 5, 6)
    query_obstacles(map_id)

    # Add a shelf
    add_shelf(map_id, 7, 8, 'Rose', 'Red', 100)
    query_shelves(map_id)

    # Remove a shelf
    remove_shelf(map_id, 7, 8)
    query_shelves(map_id)
    query_obstacles(map_id)

    # Delete the map
    delete_map(map_id)
    query_map(map_id)
