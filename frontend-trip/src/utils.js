
export const rupeesToPaise = (rupees) => Math.round(parseFloat(rupees) * 100);


export const paiseToRupees = (paise) => (paise / 100).toFixed(2);


export const formatCurrency = (paise) => {
  const rupees = paiseToRupees(paise);
  return `₹${rupees}`;
};


export const getInitials = (name) => {
  const words = name.trim().split(/\s+/);
  if (words.length === 1) {
    return words[0].substring(0, 2).toUpperCase();
  }
  return words.slice(0, 2).map(w => w[0]).join('').toUpperCase();
};

const colors = [
  '#E4A93F',
  '#4B7A5B',
  '#B5533C',
  '#6B8CAE',
  '#A67C52',
  '#7B5E7B',
];

export const getColorForMember = (index) => {
  return colors[index % colors.length];
};
