import { useState } from 'react';
import { addMember, deleteMember } from '../api';
import { getInitials, getColorForMember } from '../utils';

export default function MemberSection({ tripId, members, onMembersChange }) {
  const [showForm, setShowForm] = useState(false);
  const [memberName, setMemberName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAddMember = async (e) => {
    e.preventDefault();
    if (!memberName.trim()) return;

    setLoading(true);
    setError(null);

    try {
      await addMember(tripId, memberName.trim());
      setMemberName('');
      setShowForm(false);
      onMembersChange();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteMember = async (memberId) => {
    if (!confirm('Remove this member?')) return;

    try {
      await deleteMember(tripId, memberId);
      onMembersChange();
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div style={{ marginBottom: 'var(--space-xl)' }}>
      <h2>Members</h2>
      
      <div className="members-row">
        {members.map((member, index) => (
          <div
            key={member.id}
            className="member-circle"
            style={{ background: getColorForMember(index) }}
            onClick={() => handleDeleteMember(member.id)}
            title={`${member.name} (click to remove)`}
          >
            {getInitials(member.name)}
          </div>
        ))}
        
        <div
          className="member-circle add-member"
          onClick={() => setShowForm(!showForm)}
          title="Add member"
        >
          +
        </div>
      </div>

      {showForm && (
        <div className="form-section" style={{ marginTop: 'var(--space-md)' }}>
          <form onSubmit={handleAddMember}>
            <div className="form-group">
              <label htmlFor="memberName">Member Name</label>
              <input
                id="memberName"
                type="text"
                value={memberName}
                onChange={(e) => setMemberName(e.target.value)}
                placeholder="Enter name"
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
              <button type="submit" className="primary" disabled={loading || !memberName.trim()}>
                {loading ? 'Adding...' : 'Add Member'}
              </button>
              <button type="button" onClick={() => setShowForm(false)} disabled={loading}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {members.length === 0 && !showForm && (
        <div className="empty-state">
          <p>Add members to start tracking expenses</p>
        </div>
      )}
    </div>
  );
}
