import { useState } from 'react';
import * as storage from '../services/storage';

export default function TripLanding({ onTripCreated }) {
  const [tripName, setTripName] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!tripName.trim()) return;

    setError(null);

    try {
      const trip = storage.createTrip(tripName.trim());
      onTripCreated(trip);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="app-container">
      <div className="trip-header">
        <h1>Trip Expense Splitter</h1>
        <p style={{ marginTop: '0.5rem', opacity: 0.8 }}>
          Track expenses, split bills, settle up
        </p>
      </div>

      <div className="form-section">
        <h2>Create a New Trip</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="tripName">Trip Name</label>
            <input
              id="tripName"
              type="text"
              value={tripName}
              onChange={(e) => setTripName(e.target.value)}
              placeholder="e.g., Goa Trip 2024"
              autoFocus
            />
          </div>

          {error && (
            <p style={{ color: 'var(--rust-red)', marginBottom: '1rem' }}>
              {error}
            </p>
          )}

          <div className="form-actions">
            <button type="submit" className="primary" disabled={!tripName.trim()}>
              Start Trip
            </button>
          </div>
        </form>
      </div>

      <div style={{ textAlign: 'center', marginTop: '2rem', opacity: 0.6, fontSize: '0.875rem' }}>
        <p>Perfect for group trips, shared apartments, or any joint expenses</p>
      </div>
    </div>
  );
}
