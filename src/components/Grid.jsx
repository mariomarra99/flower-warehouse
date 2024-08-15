import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Grid.css';

const Grid = ({ updateTextBox, resetTextBox }) => {
    const initialGridSize = 20;
    const initialGrid = Array(initialGridSize).fill().map(() => Array(initialGridSize).fill(null));
    const [grid, setGrid] = useState(initialGrid);
    const [preSimulationGrid, setPreSimulationGrid] = useState(initialGrid); // State to store grid before simulation
    const [selectedCells, setSelectedCells] = useState([]);
    const [buttonsEnabled, setButtonsEnabled] = useState(false);
    const [simulationStarted, setSimulationStarted] = useState(false);
    const [simulationInProgress, setSimulationInProgress] = useState(false);
    const [start, setStart] = useState({ row: null, col: null });
    const [goal, setGoal] = useState({ row: null, col: null });
    const [goals, setGoals] = useState([]);  // Store multiple goals
    const [path, setPath] = useState([]); 
    const [gridSize, setGridSize] = useState(initialGridSize);
    const [shelfFormVisible, setShelfFormVisible] = useState(false);
    const [shelfPositions, setShelfPositions] = useState([]);
    const [previousGridState, setPreviousGridState] = useState(null); // State to store grid before adding shelf
    const [shelfDetails, setShelfDetails] = useState({
        flower: '',
        color: '',
        quantity: ''
    });
    const [gridDisabled, setGridDisabled] = useState(false);
    const [shelfInfo, setShelfInfo] = useState('');
    const [connected, setConnected] = useState(false); // State to manage connection status

    useEffect(() => {
        const newGrid = Array(gridSize).fill().map(() => Array(gridSize).fill(null));
        setGrid(newGrid);
    }, [gridSize]);

    const handleClick = (rowIndex, colIndex) => {
        if (gridDisabled) return;
        const newGrid = [...grid];
        if (simulationStarted) {
            if (start.row === null && start.col === null) {
                newGrid[rowIndex][colIndex] = 'start';
                setStart({ row: rowIndex, col: colIndex });
            } else {
                const isGoalAlreadySelected = goals.some(goal => goal.row === rowIndex && goal.col === colIndex);
                if (!isGoalAlreadySelected) {
                    newGrid[rowIndex][colIndex] = 'goal';
                    setGoals([...goals, { row: rowIndex, col: colIndex }]);
                    setGoal({ row: rowIndex, col: colIndex });
                } else {
                    // If the goal is already selected, deselect it
                    const updatedGoals = goals.filter(goal => !(goal.row === rowIndex && goal.col === colIndex));
                    newGrid[rowIndex][colIndex] = null;
                    setGoals(updatedGoals);
                }
            }
            setGrid(newGrid);
        } else {
            const cellIndex = selectedCells.findIndex(
                cell => cell.row === rowIndex && cell.col === colIndex
            );
            if (cellIndex === -1) {
                setSelectedCells([...selectedCells, { row: rowIndex, col: colIndex }]);
            } else {
                setSelectedCells(selectedCells.filter((_, i) => i !== cellIndex));
            }
            setButtonsEnabled(true);
        }
    };

    const connectToBackend = async () => {
        try {
            // Fetch data from the backend for both obstacles and shelves
            const [response_obs, response_shel] = await Promise.all([
                axios.get('http://localhost:5000/connect_obs'),  // Fetch obstacles
                axios.get('http://localhost:5000/connect_shel')  // Fetch shelves
            ]);
    
            // Reset the grid to an empty state
            const emptyGrid = Array(gridSize).fill().map(() => Array(gridSize).fill(null));
    
            // Apply obstacles to the grid
            response_obs.data.forEach(entry => {
                const { col, row } = entry;
                if (row < gridSize && col < gridSize) {
                    emptyGrid[row][col] = 'obstacle';
                }
            });
    
            // Apply shelves to the grid
            response_shel.data.forEach(entry => {
                const { position, flower, color, quantity } = entry;
                const [row, col] = position;
                if (row < gridSize && col < gridSize) {
                    emptyGrid[row][col] = 'shelf';
                }
            });
    
            // Update the grid state with the new grid
            setGrid(emptyGrid);
            setConnected(true);
            setButtonsEnabled(true);
            updateTextBox('Connected to backend successfully.');
        } catch (error) {
            console.error('Error connecting to backend:', error);
            updateTextBox('Failed to connect to backend.');
        }
    };
    
    const sendShelfDetails = async (details) => {
        try {
            await axios.post('http://localhost:5000/add_shelf', {details});
        } catch (error) {
            console.error('There was an error adding the shelf!', error);
        }
    };

    const showShelfForm = () => {
        shelfPositions.forEach(cell => {
            grid[cell.row][cell.col] = 'shelf';
        });
        setPreviousGridState([...grid]); // Save current grid state before showing shelf form
        setShelfFormVisible(true);
        setGridDisabled(true);
        setButtonsEnabled(false); // Disable buttons when shelf form is visible
    };

    const handleShelfFormSubmit = async (event) => {
        event.preventDefault();
        const positions = selectedCells.map(cell => ({
            row: cell.row,
            col: cell.col,
            ...shelfDetails
        }));
        await sendShelfDetails(positions);
        const newGrid = [...grid];
        setGrid(newGrid);
        setShelfFormVisible(false);
        setSelectedCells([]);
        setGridDisabled(false);
        setButtonsEnabled(false);
    };

    const handleShelfDetailChange = (event) => {
        const { name, value } = event.target;
        setShelfDetails({
            ...shelfDetails,
            [name]: value
        });
    };

    const cancelShelfForm = () => {
        setGrid(previousGridState); // Restore the grid to its state before adding shelf
        setGridDisabled(false);
        setShelfFormVisible(false);
        setButtonsEnabled(false); // Re-enable buttons
    };
    
    const removeShelfBackend = async (position) => {
        try {
            console.log("Removing shelf from backend at position:", position); // Debugging log
            await axios.post('http://localhost:5000/remove_shelf', { position });
            console.log("Shelf removed from backend successfully."); // Debugging log
        } catch (error) {
            console.error('Error removing shelf from backend:', error);
        }
    };

    const modifyShelf = async () => {
        if (selectedCells.length === 1) {
            const response = await axios.post('http://localhost:5000/get_shelf', {selectedCells});
            if (response.data === null){
                updateTextBox('Error: Please choose a shelf, not an obstacle');
            }else{
                setGridDisabled(true);
                shelfDetails.flower = response.data[0]['flower'];
                shelfDetails.color = response.data[0]['color'];
                shelfDetails.quantity = response.data[0]['quantity'];
                showShelfForm();
                handleShelfFormSubmit();
                setGridDisabled(false);
            }
        } else {
            alert('Please select only one shelf');
        }
    };

    const sendObstaclePosition = async (positions) => {
        try {
            await axios.post('http://localhost:5000/add_obstacle', { positions });
        } catch (error) {
            console.error('Error sending obstacle position:', error);
        }
    };

    const removeObstacleBackend = async (position) => {
        try {
            console.log("Removing obstacle from backend at position:", position); // Debugging log
            await axios.post('http://localhost:5000/remove_obstacle', { position });
            console.log("Obstacle removed from backend successfully."); // Debugging log
        } catch (error) {
            console.error('Error removing obstacle from backend:', error);
        }
    };

    const updateGrid = (action) => {
        const newGrid = grid.map((row, rIdx) =>
            row.map((cell, cIdx) => {
                const isSelected = selectedCells.some(
                    selectedCell => selectedCell.row === rIdx && selectedCell.col === cIdx
                );
                if (isSelected) {
                    if (action === 'add shelf' && selectedCells.length > 0){
                        showShelfForm();
                    }
                    if (action === 'remove shelf' && cell === 'shelf'){
                        removeShelfBackend(selectedCells);
                        return null;
                    }
                    if (action === 'modify shelf'  && cell === 'shelf'){
                        modifyShelf();
                    }
                    if (action === 'add obstacle'){
                        sendObstaclePosition(selectedCells);
                    }
                    if (action === 'remove obstacle' && cell === 'obstacle') {
                        removeObstacleBackend({ row: rIdx, col: cIdx });
                        return null;
                    }
                    if (!action.includes('remove')) return action.split(' ')[1];
                    setGrid(previousGridState);
                }
                return cell;
            })
        );
        setGrid(newGrid);
        if (action !== 'add shelf'){
            setSelectedCells([]);
        }
        setButtonsEnabled(false); // Disable buttons after action
        updateTextBox(`${action} applied to selected cells.`);
    };

    const simulateWithdrawal = () => {
        if (simulationStarted) {
            setGrid(preSimulationGrid); // Restore the grid to its state before simulation
            setSimulationStarted(false);
            setStart({ row: null, col: null });
            setGoal({ row: null, col: null });
        } else {
            if (shelfFormVisible){
                setGridDisabled(false);
                setShelfFormVisible(false);
                setGrid(previousGridState);
            }
            setSelectedCells([]);
            setPreSimulationGrid([...grid]); // Save the current state of the grid
            setSimulationStarted(true);
        }
        setButtonsEnabled(!simulationStarted); // Disable or enable buttons based on simulation state
    };

    const sendStartGoalPositions = async (start, goal) => {
        try {
            console.log("Sending start and goal positions:", { start, goal }); // Debugging log
            await axios.post('http://localhost:5000/set_start_goal', { start, goal });
            console.log("Start and goal positions sent successfully."); // Debugging log
        } catch (error) {
            console.error('Error sending start and goal positions:', error);
        }
    };

    const runSimulation = async () => {
        try {
            if (simulationInProgress) {
                alert('Simulation is already in progress. Please exit before starting a new one.');
                return;
            }
            const response = await axios.post('http://localhost:5000/run_simulation', {goals});
            const { path } = response.data;
            // Handle the path data (e.g., update the grid to show the path)
            setPath(path); // Store the path in state
            updateTextBox(`Simulation completed. Path: ${JSON.stringify(path)}`);
            setSimulationInProgress(true);
        } catch (error) {
            console.error('Error running simulation:', error);
            updateTextBox('Error: No path found.');
        }
    };

    const startSimulation = async () => {
        if (start.row !== null && goal.row !== null) {
            await sendStartGoalPositions(start, goal); // Send start and goal positions to the backend
            setGridDisabled(true);
            runSimulation()
        } else {
            alert('Please set both start and goal points.');
        }
    };

    const exitSimulationBackend = async () =>{
        try{
            await axios.post('http://localhost:5000/exit_simulation');
        } catch (error){
            console.error('Error exit simulation in backend:',error);
        }
    }
    const exitSimulation = async () => {
        const newGrid = preSimulationGrid.map((row, rowIndex) =>
            row.map((cell, colIndex) => {
                if (cell === 'start' || cell === 'goal') {
                    return null;
                }
                return cell;
            })
        );
        setGridDisabled(false);
        setGrid(newGrid); // Restore the grid to its state before simulation
        setSimulationStarted(false);
        setSimulationInProgress(false);
        setStart({ row: null, col: null });
        setGoal({ row: null, col: null });
        setGoals([]);
        setSelectedCells([]);
        setButtonsEnabled(false);
        setPath([]);
        updateTextBox('Exited the simulation');
        await exitSimulationBackend();
    };

    const flowersAvailableAction = async () => {
        try {
            const response = await axios.post('http://localhost:5000/get_shelf', {selectedCells});
            updateTextBox(JSON.stringify(response.data, null, 2));
            setShelfInfo(JSON.stringify(response.data, null, 2));
        } catch (error) {
            setShelfInfo('Error: ' + error.message);
        }
    };

    const resetMapBackend = async () => {
        try {
            await axios.post('http://localhost:5000/reset_map');
        } catch (error) {
            console.error('Error resetting map in backend:', error);
        }
    };

    const restartMap = async () => {
        const confirmed = window.confirm('Are you sure you want to restart the map? This will remove all shelves, obstacles, and flowers.');
        if (confirmed) {
            const newGrid = Array(gridSize).fill().map(() => Array(gridSize).fill(null));
            setGrid(newGrid);
            setPreSimulationGrid(newGrid); // Update preSimulationGrid when map is restarted
            setSimulationInProgress(false);
            setSelectedCells([]);
            setButtonsEnabled(false);
            setShelfFormVisible(false);
            setGridDisabled(false);
            setPath([]); 
            updateTextBox('Map has been restarted.');
            resetTextBox(); // Reset the text box in App.jsx
            if (simulationStarted) {
                setSimulationStarted(false);
                setStart({ row: null, col: null });
                setGoal({ row: null, col: null });
                setGoals([]);
            }
            await resetMapBackend(); // Reset the backend map state
        }
    };
    
    return (
        <div className={`grid-container ${gridDisabled ? 'disabled' : ''}`}>
            <div className={`grid ${simulationStarted ? 'simulated' : ''}`}>
                {grid.map((row, rowIndex) =>
                    row.map((cell, colIndex) => {
                        // Determine cell class
                        let cellClass = `cell ${cell}`;
                        if (
                            path.some(
                                pathCell =>
                                    pathCell[0] === rowIndex && pathCell[1] === colIndex
                            ) &&
                            !(rowIndex === start.row && colIndex === start.col) &&
                            !(rowIndex === goal.row && colIndex === goal.col)
                        ) {
                            cellClass += ' path';
                        }
                        if (selectedCells.some(selectedCell => selectedCell.row === rowIndex && selectedCell.col === colIndex)) {
                            cellClass += ' selected'; // Add 'selected' class if the cell is selected
                        }
                        return (
                            <div
                                key={`${rowIndex}-${colIndex}`}
                                className={cellClass}
                                onClick={() => handleClick(rowIndex, colIndex)}
                            />
                        );
                    })
                )}
            </div>
            {shelfFormVisible && (
                <form onSubmit={handleShelfFormSubmit} className="shelf-form">
                    <label>
                        Flower Type:
                        <input
                            type="text"
                            name="flower"
                            value={shelfDetails.flower}
                            onChange={handleShelfDetailChange}
                            required
                        />
                    </label>
                    <label>
                        Color:
                        <input
                            type="text"
                            name="color"
                            value={shelfDetails.color}
                            onChange={handleShelfDetailChange}
                            required
                        />
                    </label>
                    <label>
                        Quantity:
                        <input
                            type="number"
                            name="quantity"
                            value={shelfDetails.quantity}
                            onChange={handleShelfDetailChange}
                            required
                        />
                    </label>
                    <div className="shelf-form-buttons">
                        <button type="submit" style={{ backgroundColor: 'green', color: 'white' }}>Ok</button>
                        <button type="button" onClick={cancelShelfForm} style={{ backgroundColor: 'red', color: 'white' }}>Cancel</button>
                    </div>
                </form>
            )}
            <div className={`actions ${simulationStarted || shelfFormVisible ? 'disabled' : ''}`}>
                <button onClick={connectToBackend} disabled={connected}>Connect</button>
                <button onClick={() => updateGrid('add shelf')} disabled={!buttonsEnabled || !connected}>Add Shelf</button>
                <button onClick={() => updateGrid('remove shelf')} disabled={!buttonsEnabled || !connected}>Remove Shelf</button>
                <button onClick={modifyShelf} disabled={!buttonsEnabled || !connected}>Modify Shelf</button>
                <button onClick={() => updateGrid('add obstacle')} disabled={!buttonsEnabled || !connected}>Add Obstacle</button>
                <button onClick={() => updateGrid('remove obstacle')} disabled={!buttonsEnabled || !connected}>Remove Obstacle</button>
                <button onClick={flowersAvailableAction} disabled={!connected}>Flowers Available</button>
            </div>
            <div className={`simulation-buttons ${!shelfFormVisible? 'disabled' : ''}`}>
                <button className={`simulate-btn ${simulationStarted || !connected  ? 'disabled' : ''}`} onClick={simulateWithdrawal}>Withdrawal Simulation</button>
                <button className="restart-map-btn" onClick={restartMap}>Restart Map</button>
                {simulationStarted && (
                    <div className="start-goal-inputs">
                        <div className="start-input">
                            <label>
                                Set start:
                                <input
                                    type="text"
                                    value={`${start.row !== null ? start.row : ''}, ${start.col !== null ? start.col : ''}`}
                                    readOnly
                                />
                            </label>
                        </div>
                        <div className="goal-input">
                            <label>
                                Set goal:
                                <input
                                    type="text"
                                    value={`${goal.row !== null ? goal.row : ''}, ${goal.col !== null ? goal.col : ''}`}
                                    readOnly
                                />
                            </label>
                        </div>
                        <div className="simulation-actions">
                            <button onClick={startSimulation} className="start-simulation-btn">Start Simulation</button>
                            <button onClick={exitSimulation} className="exit-btn">Exit</button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Grid;
