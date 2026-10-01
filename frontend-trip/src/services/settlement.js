// Greedy algorithm for optimal expense settlement using heaps
// Time Complexity: O(n log n) where n is number of members

class MinHeap {
  constructor() {
    this.heap = [];
  }

  push(value) {
    this.heap.push(value);
    this.bubbleUp(this.heap.length - 1);
  }

  pop() {
    if (this.heap.length === 0) return null;
    if (this.heap.length === 1) return this.heap.pop();
    
    const min = this.heap[0];
    this.heap[0] = this.heap.pop();
    this.bubbleDown(0);
    return min;
  }

  bubbleUp(index) {
    while (index > 0) {
      const parent = Math.floor((index - 1) / 2);
      if (this.heap[parent][0] <= this.heap[index][0]) break;
      [this.heap[parent], this.heap[index]] = [this.heap[index], this.heap[parent]];
      index = parent;
    }
  }

  bubbleDown(index) {
    while (true) {
      let smallest = index;
      const left = 2 * index + 1;
      const right = 2 * index + 2;

      if (left < this.heap.length && this.heap[left][0] < this.heap[smallest][0]) {
        smallest = left;
      }
      if (right < this.heap.length && this.heap[right][0] < this.heap[smallest][0]) {
        smallest = right;
      }
      if (smallest === index) break;

      [this.heap[index], this.heap[smallest]] = [this.heap[smallest], this.heap[index]];
      index = smallest;
    }
  }

  peek() {
    return this.heap[0] || null;
  }

  size() {
    return this.heap.length;
  }
}

class MaxHeap extends MinHeap {
  bubbleUp(index) {
    while (index > 0) {
      const parent = Math.floor((index - 1) / 2);
      if (this.heap[parent][0] >= this.heap[index][0]) break;
      [this.heap[parent], this.heap[index]] = [this.heap[index], this.heap[parent]];
      index = parent;
    }
  }

  bubbleDown(index) {
    while (true) {
      let largest = index;
      const left = 2 * index + 1;
      const right = 2 * index + 2;

      if (left < this.heap.length && this.heap[left][0] > this.heap[largest][0]) {
        largest = left;
      }
      if (right < this.heap.length && this.heap[right][0] > this.heap[largest][0]) {
        largest = right;
      }
      if (largest === index) break;

      [this.heap[index], this.heap[largest]] = [this.heap[largest], this.heap[index]];
      index = largest;
    }
  }
}

// Calculate how much each participant owes for an expense
function calculateShares(totalAmount, participants) {
  const total = participants.length;
  const baseShare = Math.floor(totalAmount / total);
  const remainder = totalAmount % total;
  
  const shares = {};
  participants.forEach((memberId, index) => {
    shares[memberId] = baseShare + (index < remainder ? 1 : 0);
  });
  
  return shares;
}

// Calculate net balance for each member across all expenses
function calculateNetBalances(expenses) {
  const balances = {};
  
  expenses.forEach(expense => {
    // Calculate shares
    const shares = calculateShares(expense.amount, expense.participants);
    
    // Add what each payer paid
    expense.payers.forEach(payer => {
      balances[payer.memberId] = (balances[payer.memberId] || 0) + payer.amount;
    });
    
    // Subtract what each participant owes
    Object.entries(shares).forEach(([memberId, share]) => {
      balances[memberId] = (balances[memberId] || 0) - share;
    });
  });
  
  return balances;
}

// Minimize transactions using greedy algorithm with heaps
function minimizeTransactions(balances) {
  const debtors = new MinHeap();
  const creditors = new MaxHeap();
  
  Object.entries(balances).forEach(([memberId, balance]) => {
    if (balance < 0) {
      debtors.push([balance, memberId]);
    } else if (balance > 0) {
      creditors.push([balance, memberId]);
    }
  });
  
  const transactions = [];
  
  while (debtors.size() > 0 && creditors.size() > 0) {
    const [debt, debtorId] = debtors.pop();
    const [credit, creditorId] = creditors.pop();
    
    const settleAmount = Math.min(-debt, credit);
    
    transactions.push({
      from: debtorId,
      to: creditorId,
      amount: settleAmount
    });
    
    const remainingDebt = debt + settleAmount;
    const remainingCredit = credit - settleAmount;
    
    if (remainingDebt < 0) {
      debtors.push([remainingDebt, debtorId]);
    }
    if (remainingCredit > 0) {
      creditors.push([remainingCredit, creditorId]);
    }
  }
  
  return transactions;
}

// Main function to get settlement data
export function getSettlement(expenses) {
  if (!expenses || expenses.length === 0) {
    return {
      balances: {},
      transactions: [],
      totalExpenses: 0
    };
  }
  
  const balances = calculateNetBalances(expenses);
  const transactions = minimizeTransactions(balances);
  const totalExpenses = expenses.reduce((sum, exp) => sum + exp.amount, 0);
  
  return {
    balances,
    transactions,
    totalExpenses
  };
}
