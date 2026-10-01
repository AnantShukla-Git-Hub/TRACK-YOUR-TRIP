import { useState } from 'react';
import * as storage from '../services/storage';
import { getInitials, getColorForMember } from '../utils';

export default function MemberSection({ members, onMembersChange }) {
  const [showForm, setShowForm] = useState(false);
  const [memberName, setMemberName] = useState('');
  const [error, setError] = useState(null);

  const handleAddMember = (e) => {
    e.preventDefault();
    if (!memberName.trim()) return;

    setError(null);

    try {
      storage.addMember(memberName.trim());
      setMemberName('');
      setShowForm(false);
      onMembersChange();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDeleteMember = (memberId) => {
    if (!confirm('Remove this member?')) return;

    try {
      storage.deleteMember(memberId);
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
              />
            </div>

            {error && (
              <p style={{ color: 'var(--rust-red)', marginBottom: '1rem' }}>
                {error}
              </p>
            )}

            <div className="form-actions">
              <button type="submit" className="primary" disabled={!memberName.trim()}>
                Add Member
              </button>
              <button type="button" onClick={() => setShowForm(false)}>
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
