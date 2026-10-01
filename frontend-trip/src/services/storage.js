// Local storage manager for trip data
// All amounts stored in paise (1 rupee = 100 paise) to avoid decimal errors

const STORAGE_KEY = 'trip_data';

function getData() {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : {
      trip: null,
      members: [],
      expenses: [],
      nextMemberId: 1,
      nextExpenseId: 1
    };
  } catch {
    return {
      trip: null,
      members: [],
      expenses: [],
      nextMemberId: 1,
      nextExpenseId: 1
    };
  }
}

function saveData(data) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

export function createTrip(name) {
  const data = getData();
  data.trip = {
    name,
    createdAt: new Date().toISOString()
  };
  saveData(data);
  return data.trip;
}

export function getTrip() {
  return getData().trip;
}

export function clearTrip() {
  localStorage.removeItem(STORAGE_KEY);
}

export function addMember(name) {
  const data = getData();
  const member = {
    id: data.nextMemberId++,
    name
  };
  data.members.push(member);
  saveData(data);
  return member;
}

export function getMembers() {
  return getData().members;
}

export function deleteMember(memberId) {
  const data = getData();
  
  // Check if member is used in any expense
  const isUsed = data.expenses.some(exp => 
    exp.payers.some(p => p.memberId === memberId) ||
    exp.participants.includes(memberId)
  );
  
  if (isUsed) {
    throw new Error('Cannot delete member who is part of an expense');
  }
  
  data.members = data.members.filter(m => m.id !== memberId);
  saveData(data);
}

export function addExpense(description, amount, payers, participants) {
  const data = getData();
  
  // Validate total paid equals expense amount
  const totalPaid = payers.reduce((sum, p) => sum + p.amount, 0);
  if (totalPaid !== amount) {
    throw new Error('Total paid must equal expense amount');
  }
  
  const expense = {
    id: data.nextExpenseId++,
    description,
    amount,
    payers,
    participants,
    createdAt: new Date().toISOString()
  };
  
  data.expenses.push(expense);
  saveData(data);
  return expense;
}

export function getExpenses() {
  return getData().expenses;
}

export function getAllData() {
  return getData();
}
