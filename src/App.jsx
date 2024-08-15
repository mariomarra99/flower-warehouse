import React, { useState } from 'react';
import Grid from './components/Grid';
import './App.css';

const App = () => {
    const [infoText, setInfoText] = useState('');
    const [isPlaceholder, setIsPlaceholder] = useState(true);

    const updateTextBox = (message) => {
        setInfoText(prevText => (prevText ? prevText + '\n' + message : message));
        setIsPlaceholder(false);
    };

    const resetTextBox = () => {
        setInfoText('');
        setIsPlaceholder(true);
    };

    return (
        <div className="app">
	  <div className="text-box-wrapper">
          	<h2>Flower Warehouse</h2>
            		<div className="text-box">
                	<p className={isPlaceholder ? 'placeholder' : ''}>{isPlaceholder ? 'Select a cell in the grid and choose an action.' : infoText}</p>
            	</div>
	   </div>
           <Grid updateTextBox={updateTextBox} resetTextBox={resetTextBox} />
        </div>
    );
};

export default App;