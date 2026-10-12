export function formatCount(value) {
  if (value === null || value === undefined) {
    return "";
  }

  return typeof value === "number" ? value.toLocaleString() : value;
}

const DATE_ONLY_PATTERN = /^(\d{4})-(\d{2})-(\d{2})$/;

// Today's date as YYYY-MM-DD in the browser's local time. new Date().toISOString()
// is UTC, which is still "yesterday" for the first hours of the day in Beirut.
export function todayLocal() {
  const now = new Date();
  const pad = (number) => String(number).padStart(2, "0");
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
}

export function formatDate(value) {
  if (!value) {
    return "-";
  }

  // A bare "YYYY-MM-DD" must be read as a local calendar date; new Date()
  // would treat it as UTC midnight and can shift the day when displayed.
  const dateOnly = typeof value === "string" ? DATE_ONLY_PATTERN.exec(value) : null;
  const date = dateOnly
    ? new Date(Number(dateOnly[1]), Number(dateOnly[2]) - 1, Number(dateOnly[3]))
    : new Date(value);
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
