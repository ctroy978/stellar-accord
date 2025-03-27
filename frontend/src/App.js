import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [gameInfo, setGameInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchGameInfo = async () => {
      try {
        console.log('Fetching game info...');
        // Use the full URL in development for debugging
        const response = await axios.get('/api/game-info');
        console.log('Response received:', response.data);
        setGameInfo(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to fetch game information: ' + (err.message || 'Unknown error'));
        setLoading(false);
      }
    };

    fetchGameInfo();
  }, []);

  if (loading) {
    return (
      <div className="app-container">
        <div className="loading">Loading game information...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app-container">
        <div className="error">
          <h2>Error</h2>
          <p>{error}</p>
          <p>Please make sure the backend server is running and accessible.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>{gameInfo?.name || 'Stellar Accord'}</h1>
        <p>{gameInfo?.description || 'Interstellar Diplomacy Simulation Game'}</p>
      </header>
      
      <main className="app-content">
        <section className="civilizations">
          <h2>Civilizations</h2>
          {gameInfo?.civilizations && (
            <ul>
              {gameInfo.civilizations.map((civ, index) => (
                <li key={index}>{civ}</li>
              ))}
            </ul>
          )}
        </section>
      </main>
      
      <footer className="app-footer">
        <p>Stellar Accord - Development Version</p>
      </footer>
    </div>
  );
}

export default App;
