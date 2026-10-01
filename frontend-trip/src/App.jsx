import { useState, useEffect } from 'react';
import TripLanding from './components/TripLanding';
import TripDashboard from './components/TripDashboard';
import './App.css';
import * as storage from './services/storage';

function App() {
  const [currentTrip, setCurrentTrip] = useState(null);

  useEffect(() => {
    const trip = storage.getTrip();
    setCurrentTrip(trip);
  }, []);

  const handleTripCreated = (trip) => {
    setCurrentTrip(trip);
  };

  const handleClearTrip = () => {
    if (confirm('Clear current trip? All data will be lost.')) {
      storage.clearTrip();
      setCurrentTrip(null);
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
