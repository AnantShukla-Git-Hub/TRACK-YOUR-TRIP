import { useState, useEffect } from 'react';
import { listMembers, listExpenses, getSettlement } from '../api';
import MemberSection from './MemberSection';
import ExpenseSection from './ExpenseSection';
import SettlementSection from './SettlementSection';

export default function TripDashboard({ trip, onClearTrip }) {
  const [members, setMembers] = useState([]);
  const [expenses, setExpenses] = useState([]);
  const [settlement, setSettlement] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const [membersData, expensesData, settlementData] = await Promise.all([
        listMembers(trip.id),
        listExpenses(trip.id),
        getSettlement(trip.id),
      ]);
      setMembers(membersData);
      setExpenses(expensesData);
      setSettlement(settlementData);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [trip.id]);

  if (loading) {
    return (
      <div className="app-container">
        <div className="loading">Loading trip data...</div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <div className="trip-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1>{trip.name}</h1>
          <button 
            onClick={onClearTrip}
            style={{ 
              padding: '0.5rem 1rem', 
              fontSize: '0.875rem',
              background: 'transparent',
              border: '1px solid var(--warm-gray)',
              color: 'var(--ink-navy)'
            }}
          >
            Change Trip
          </button>
        </div>
        <div style={{ 
          marginTop: 'var(--space-sm)', 
          padding: 'var(--space-sm)',
          background: 'rgba(228, 169, 63, 0.1)',
          borderLeft: '3px solid var(--marigold)',
          fontSize: '0.875rem'
        }}>
          <strong>Note:</strong> Data is NOT saved on server. Download PDF to keep a record.
        </div>
      </div>

      <MemberSection 
        tripId={trip.id} 
        members={members} 
        onMembersChange={loadData} 
      />

      <ExpenseSection
        tripId={trip.id}
        members={members}
        expenses={expenses}
        onExpensesChange={loadData}
      />

      {expenses.length > 0 && (
        <SettlementSection
          tripId={trip.id}
          settlement={settlement}
        />
      )}
    </div>
  );
}
