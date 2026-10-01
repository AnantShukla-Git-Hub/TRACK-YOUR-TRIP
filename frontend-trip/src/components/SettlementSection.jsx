import { formatCurrency } from '../utils';
import * as storage from '../services/storage';

export default function SettlementSection({ settlement, members }) {
  if (!settlement) return null;

  const { balances, transactions, totalExpenses } = settlement;
  
  const getMemberName = (memberId) => {
    return members.find(m => m.id === memberId)?.name || 'Unknown';
  };

  const handleDownloadPDF = async () => {
    try {
      const tripData = storage.getAllData();
      
      const pdfData = {
        tripName: tripData.trip.name,
        members: tripData.members,
        expenses: tripData.expenses,
        balances: Object.entries(balances).map(([memberId, amount]) => ({
          memberId: parseInt(memberId),
          amount
        })),
        transactions: transactions.map(t => ({
          fromId: t.from,
          toId: t.to,
          amount: t.amount
        })),
        totalExpenses
      };

      const response = await fetch('/api/generate-pdf', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(pdfData)
      });

      if (!response.ok) throw new Error('PDF generation failed');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${tripData.trip.name.replace(/\s+/g, '_')}_settlement.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      alert('Failed to generate PDF: ' + error.message);
    }
  };

  return (
    <div className="settlement-section perforation">
      <h2>Settlement</h2>

      {/* Grand Total */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        padding: 'var(--space-lg)',
        background: 'rgba(228, 169, 63, 0.15)',
        borderRadius: '8px',
        border: '2px solid var(--marigold)',
        marginBottom: 'var(--space-xl)'
      }}>
        <div>
          <h3 style={{ margin: 0 }}>Trip Total</h3>
          <p style={{ margin: '0.25rem 0 0', fontSize: '0.875rem', opacity: 0.8 }}>
            Total amount spent
          </p>
        </div>
        <div className="mono" style={{ fontSize: '2rem', fontWeight: '600', color: 'var(--marigold)' }}>
          {formatCurrency(totalExpenses)}
        </div>
      </div>

      {/* Net Balances */}
      <div style={{ marginBottom: 'var(--space-xl)' }}>
        <h3>Net Balances</h3>
        <div style={{ marginTop: 'var(--space-md)' }}>
          {Object.entries(balances).map(([memberId, balance]) => {
            const isPositive = balance > 0;
            const isZero = balance === 0;
            
            return (
              <div
                key={memberId}
                className={`balance-card ${isPositive ? 'positive' : isZero ? '' : 'negative'}`}
              >
                <span className="balance-name">{getMemberName(parseInt(memberId))}</span>
                <span className={`balance-amount mono ${isPositive ? 'text-green' : isZero ? '' : 'text-red'}`}>
                  {isZero ? 'Settled' : (
                    <>
                      {isPositive ? 'Gets back' : 'Owes'}{' '}
                      {formatCurrency(Math.abs(balance))}
                    </>
                  )}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Transactions */}
      <div style={{ marginBottom: 'var(--space-xl)' }}>
        <h3>Who Pays Whom</h3>
        
        {transactions.length > 0 ? (
          <div style={{ marginTop: 'var(--space-md)' }}>
            {transactions.map((txn, index) => (
              <div key={index} className="ticket-stub">
                <div className="ticket-stub-content">
                  <div className="ticket-stub-flow">
                    <strong>{getMemberName(txn.from)}</strong>
                    <span className="ticket-stub-arrow">→</span>
                    <strong>{getMemberName(txn.to)}</strong>
                  </div>
                  <div className="ticket-stub-amount mono">
                    {formatCurrency(txn.amount)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <p>Everyone is already settled!</p>
          </div>
        )}
      </div>

      <div style={{ textAlign: 'center' }}>
        <button className="primary" onClick={handleDownloadPDF}>
          Download PDF Report
        </button>
      </div>
    </div>
  );
}
