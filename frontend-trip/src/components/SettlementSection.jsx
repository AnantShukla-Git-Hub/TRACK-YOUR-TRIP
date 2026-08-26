import { formatCurrency } from '../utils';
import { getSheetPdfUrl } from '../api';

export default function SettlementSection({ tripId, settlement }) {
  if (!settlement) return null;

  const { grand_total_paise, balances, transactions } = settlement;

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
          {formatCurrency(grand_total_paise)}
        </div>
      </div>

      {/* Net Balances */}
      <div style={{ marginBottom: 'var(--space-xl)' }}>
        <h3>Net Balances</h3>
        <div style={{ marginTop: 'var(--space-md)' }}>
          {balances.map(balance => {
            const isPositive = balance.net_balance_paise > 0;
            const isZero = balance.net_balance_paise === 0;
            
            return (
              <div
                key={balance.member_id}
                className={`balance-card ${isPositive ? 'positive' : isZero ? '' : 'negative'}`}
              >
                <span className="balance-name">{balance.member_name}</span>
                <span className={`balance-amount mono ${isPositive ? 'text-green' : isZero ? '' : 'text-red'}`}>
                  {isZero ? 'Settled' : (
                    <>
                      {isPositive ? 'Gets back' : 'Owes'}{' '}
                      {formatCurrency(Math.abs(balance.net_balance_paise))}
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
                    <strong>{txn.debtor_name}</strong>
                    <span className="ticket-stub-arrow">→</span>
                    <strong>{txn.creditor_name}</strong>
                  </div>
                  <div className="ticket-stub-amount mono">
                    {formatCurrency(txn.amount_paise)}
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

      {/* PDF Export */}
      <div style={{ textAlign: 'center' }}>
        <a
          href={getSheetPdfUrl(tripId)}
          target="_blank"
          rel="noopener noreferrer"
          style={{ textDecoration: 'none' }}
        >
          <button className="primary">
            Download PDF Report
          </button>
        </a>
      </div>
    </div>
  );
}
