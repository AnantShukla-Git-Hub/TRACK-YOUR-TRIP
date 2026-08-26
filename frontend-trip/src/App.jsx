import { useState, useEffect } from 'react';
import TripLanding from './components/TripLanding';
import TripDashboard from './components/TripDashboard';
import './App.css';

function App() {
  const [currentTrip, setCurrentTrip] = useState(null);

  useEffect(() => {
    // Load trip from localStorage on mount
    const savedTrip = localStorage.getItem('currentTrip');
    if (savedTrip) {
      try {
        setCurrentTrip(JSON.parse(savedTrip));
      } catch (e) {
        localStorage.removeItem('currentTrip');
      }
    }
  }, []);

  const handleTripCreated = (trip) => {
    setCurrentTrip(trip);
    localStorage.setItem('currentTrip', JSON.stringify(trip));
  };

  const handleClearTrip = () => {
    if (confirm('Clear current trip? This will only clear from your browser, data is saved on server.')) {
      setCurrentTrip(null);
      localStorage.removeItem('currentTrip');
    }
  };

  return (
    <>
      {!currentTrip ? (
        <TripLanding onTripCreated={handleTripCreated} />
      ) : (
        <TripDashboard trip={currentTrip} onClearTrip={handleClearTrip} />
      )}
    </>
  );
}

export default App;
