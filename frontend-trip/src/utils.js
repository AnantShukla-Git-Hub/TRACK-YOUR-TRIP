// Utility functions

// Convert rupees to paise (100 paise = 1 rupee)
export const rupeesToPaise = (rupees) => Math.round(parseFloat(rupees) * 100);

// Convert paise to rupees
export const paiseToRupees = (paise) => (paise / 100).toFixed(2);

// Format amount as currency
export const formatCurrency = (paise) => {
  const rupees = paiseToRupees(paise);
  return `₹${rupees}`;
};

// Get initials from name
export const getInitials = (name) => {
  const words = name.trim().split(/\s+/);
  if (words.length === 1) {
    return words[0].substring(0, 2).toUpperCase();
  }
  return words.slice(0, 2).map(w => w[0]).join('').toUpperCase();
};

// Generate random color for member circles
const colors = [
  '#E4A93F', // marigold
  '#4B7A5B', // moss green
  '#B5533C', // rust red
  '#6B8CAE', // steel blue
  '#A67C52', // tan
  '#7B5E7B', // plum
];

export const getColorForMember = (index) => {
  return colors[index % colors.length];
};
