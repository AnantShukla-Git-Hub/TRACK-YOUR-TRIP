import { useState, useEffect } from 'react';
import * as storage from '../services/storage';
import { getSettlement } from '../services/settlement';
import MemberSection from './MemberSection';
import ExpenseSection from './ExpenseSection';
import SettlementSection from './SettlementSection';

export default function TripDashboard({ trip, onClearTrip }) {
  const [members, setMembers] = useState([]);
  const [expenses, setExpenses] = useState([]);
  const [settlement, setSettlement] = useState(null);

  const loadData = () => {
    const membersData = storage.getMembers();
    const expensesData = storage.getExpenses();
    const settlementData = getSettlement(expensesData);
    
    setMembers(membersData);
    setExpenses(expensesData);
    setSettlement(settlementData);
  };

  useEffect(() => {
    loadData();
  }, []);

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
          <strong>Note:</strong> Data saved locally in browser. Download PDF to keep a permanent record.
        </div>
      </div>

      <MemberSection 
        members={members} 
        onMembersChange={loadData} 
      />

      <ExpenseSection
        members={members}
        expenses={expenses}
        onExpensesChange={loadData}
      />

      {expenses.length > 0 && (
        <SettlementSection
          settlement={settlement}
          members={members}
        />
      )}
    </div>
  );
}
