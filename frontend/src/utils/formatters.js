export function formatCount(value) {
  if (value === null || value === undefined) {
    return "";
  }

  return typeof value === "number" ? value.toLocaleString() : value;
}

export function formatDate(value) {
  if (!value) {
    return "-";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric"
  }).format(date);
}

export function formatCurrency(value) {
  const number = Number(value);
  return Number.isFinite(number) && number > 0 ? `$${number.toFixed(2)}` : "-";
}
