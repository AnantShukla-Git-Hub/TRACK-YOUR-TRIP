import { useState } from 'react';
import * as storage from '../services/storage';
import { formatCurrency, rupeesToPaise } from '../utils';

export default function ExpenseSection({ members, expenses, onExpensesChange }) {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    description: '',
    amount: '',
    payers: {},
    splitAmong: [],
  });
  const [error, setError] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const payerIds = Object.keys(formData.payers).filter(id => formData.payers[id]);
    
    if (!formData.description.trim() || !formData.amount || payerIds.length === 0 || formData.splitAmong.length === 0) {
      setError('Please fill all fields');
      return;
    }

    const totalPaise = rupeesToPaise(formData.amount);
    const totalPaid = payerIds.reduce((sum, id) => sum + rupeesToPaise(formData.payers[id]), 0);

    if (totalPaid !== totalPaise) {
      setError(`Total paid (Rs ${(totalPaid / 100).toFixed(2)}) must equal expense amount (Rs ${formData.amount})`);
      return;
    }
    
    try {
      storage.addExpense(
        formData.description.trim(),
        totalPaise,
        payerIds.map(memberId => ({
          memberId: parseInt(memberId),
          amount: rupeesToPaise(formData.payers[memberId])
        })),
        formData.splitAmong.map(id => parseInt(id))
      );
      
      setFormData({
        description: '',
        amount: '',
        payers: {},
        splitAmong: [],
      });
      setShowForm(false);
      setError(null);
      onExpensesChange();
    } catch (err) {
      setError(err.message);
    }
  };

  const togglePayer = (memberId) => {
    setFormData(prev => {
      const newPayers = { ...prev.payers };
      if (newPayers[memberId]) {
        delete newPayers[memberId];
      } else {
        newPayers[memberId] = '';
      }
      return { ...prev, payers: newPayers };
    });
  };

  const updatePayerAmount = (memberId, amount) => {
    setFormData(prev => ({
      ...prev,
      payers: { ...prev.payers, [memberId]: amount },
    }));
  };

  const toggleSplitMember = (memberId) => {
    setFormData(prev => ({
      ...prev,
      splitAmong: prev.splitAmong.includes(memberId)
        ? prev.splitAmong.filter(id => id !== memberId)
        : [...prev.splitAmong, memberId],
    }));
  };

  const selectAllPayers = () => {
    if (!formData.amount) return;
    const equalAmount = (parseFloat(formData.amount) / members.length).toFixed(2);
    const newPayers = {};
    members.forEach(m => {
      newPayers[m.id] = equalAmount;
    });
    setFormData(prev => ({ ...prev, payers: newPayers }));
  };

  const clearAllPayers = () => {
    setFormData(prev => ({ ...prev, payers: {} }));
  };

  const selectAllParticipants = () => {
    setFormData(prev => ({ ...prev, splitAmong: members.map(m => m.id) }));
  };

  const clearAllParticipants = () => {
    setFormData(prev => ({ ...prev, splitAmong: [] }));
  };

  const getMemberName = (memberId) => {
    return members.find(m => m.id === memberId)?.name || 'Unknown';
  };

  const getPayersText = (payers) => {
    if (payers.length === 1) {
      return `Paid by ${getMemberName(payers[0].memberId)}`;
    }
    return `Paid by ${payers.length} members`;
  };

  const selectedPayerIds = Object.keys(formData.payers).filter(id => formData.payers[id]);
  const totalPaidSoFar = selectedPayerIds.reduce((sum, id) => {
    const amount = parseFloat(formData.payers[id]) || 0;
    return sum + amount;
  }, 0);
  const remainingToPay = parseFloat(formData.amount) - totalPaidSoFar;

  return (
    <div className="perforation">
      <h2>Expenses</h2>

      {!showForm && (
        <button 
          className="primary" 
          onClick={() => setShowForm(true)}
          style={{ marginBottom: 'var(--space-md)' }}
        >
          Add Expense
        </button>
      )}

      {showForm && (
        <div className="form-section" style={{ marginBottom: 'var(--space-lg)' }}>
          <h3>New Expense</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="description">Description</label>
              <input
                id="description"
                type="text"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="e.g., Hotel booking, Lunch"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="amount">Amount (₹)</label>
              <input
                id="amount"
                type="number"
                step="0.01"
                min="0"
                value={formData.amount}
                onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                placeholder="0.00"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-xs)' }}>
                <label>Paid by (select multiple)</label>
                <div style={{ display: 'flex', gap: 'var(--space-xs)' }}>
                  <button 
                    type="button" 
                    onClick={selectAllPayers}
                    disabled={!formData.amount}
                    style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                  >
                    All
                  </button>
                  <button 
                    type="button" 
                    onClick={clearAllPayers}
                    style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                  >
                    Clear
                  </button>
                </div>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)' }}>
                {members.map(member => (
                  <div key={member.id} style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)', cursor: 'pointer', flex: '0 0 150px' }}>
                      <input
                        type="checkbox"
                        checked={!!formData.payers[member.id]}
                        onChange={() => togglePayer(member.id)}
                      />
                      <span>{member.name}</span>
                    </label>
                    {formData.payers[member.id] !== undefined && (
                      <input
                        type="number"
                        step="0.01"
                        min="0"
                        value={formData.payers[member.id]}
                        onChange={(e) => updatePayerAmount(member.id, e.target.value)}
                        placeholder="Amount"
                        style={{ width: '120px' }}
                      />
                    )}
                  </div>
                ))}
              </div>
              {formData.amount && selectedPayerIds.length > 0 && (
                <div style={{ marginTop: 'var(--space-sm)', fontSize: '0.875rem' }}>
                  {remainingToPay > 0.01 ? (
                    <span style={{ color: 'var(--rust-red)' }}>
                      Remaining: ₹{remainingToPay.toFixed(2)}
                    </span>
                  ) : remainingToPay < -0.01 ? (
                    <span style={{ color: 'var(--rust-red)' }}>
                      Overpaid by: ₹{Math.abs(remainingToPay).toFixed(2)}
                    </span>
                  ) : (
                    <span style={{ color: 'var(--moss-green)' }}>
                      ✓ Total matches
                    </span>
                  )}
                </div>
              )}
            </div>

            <div className="form-group">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-xs)' }}>
                <label>Split among (select multiple)</label>
                <div style={{ display: 'flex', gap: 'var(--space-xs)' }}>
                  <button 
                    type="button" 
                    onClick={selectAllParticipants}
                    style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                  >
                    All
                  </button>
                  <button 
                    type="button" 
                    onClick={clearAllParticipants}
                    style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                  >
                    Clear
                  </button>
                </div>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)' }}>
                {members.map(member => (
                  <label 
                    key={member.id} 
                    style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: 'var(--space-xs)',
                      cursor: 'pointer' 
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={formData.splitAmong.includes(member.id)}
                      onChange={() => toggleSplitMember(member.id)}
                    />
                    <span>{member.name}</span>
                  </label>
                ))}
              </div>
            </div>

            {error && (
              <p style={{ color: 'var(--rust-red)', marginBottom: '1rem' }}>
                {error}
              </p>
            )}

            <div className="form-actions">
              <button type="submit" className="primary">
                Add Expense
              </button>
              <button type="button" onClick={() => setShowForm(false)}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {expenses.length > 0 ? (
        <>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            padding: 'var(--space-md)',
            background: 'rgba(228, 169, 63, 0.1)',
            borderRadius: '4px',
            marginBottom: 'var(--space-md)'
          }}>
            <strong>Grand Total</strong>
            <strong className="mono" style={{ fontSize: '1.25rem', color: 'var(--marigold)' }}>
              {formatCurrency(expenses.reduce((sum, e) => sum + e.amount, 0))}
            </strong>
          </div>
          <div className="expense-list">
          {expenses.map(expense => (
            <div key={expense.id} className="expense-item">
              <div className="expense-desc">
                <strong>{expense.description}</strong>
                <div style={{ fontSize: '0.875rem', opacity: 0.7, marginTop: '0.25rem' }}>
                  {getPayersText(expense.payers)}
                </div>
              </div>
              <div className="expense-amount mono">
                {formatCurrency(expense.amount)}
              </div>
            </div>
          ))}
        </div>
        </>
      ) : !showForm && (
        <div className="empty-state">
          <p>No expenses yet</p>
        </div>
      )}
    </div>
  );
}
