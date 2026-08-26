import { useState } from 'react';
import { createTrip } from '../api';

export default function TripLanding({ onTripCreated }) {
  const [tripName, setTripName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!tripName.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const trip = await createTrip(tripName.trim());
      onTripCreated(trip);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
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
              disabled={loading}
            />
          </div>

          {error && (
            <p style={{ color: 'var(--rust-red)', marginBottom: '1rem' }}>
              {error}
            </p>
          )}

          <div className="form-actions">
            <button type="submit" className="primary" disabled={loading || !tripName.trim()}>
              {loading ? 'Creating...' : 'Start Trip'}
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
