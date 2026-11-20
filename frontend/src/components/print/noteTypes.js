import { formatDate } from "../../utils/formatters";

const RESOLUTION_LABELS = { repair: "Send to repair", available: "Return to available" };

function capitalize(value) {
  return value ? value.charAt(0).toUpperCase() + value.slice(1) : "";
}

// A cancelled record keeps its note, so the note must say so.
function statusText(record, activeLabel) {
  const cancelled = record.status === "cancelled" || record.isactive === false;
  if (!cancelled) return activeLabel;
  return record.cancel_reason ? `Cancelled - ${record.cancel_reason}` : "Cancelled";
}

// Per-type content of the printable operational note. RecordNote renders the same layout
// for every type; this config only says what to show. Adding a type = one entry here plus
// a Print button on its detail page. Only operational fields belong here: the note is
// never a financial document.
export const NOTE_TYPES = {
  receiving: {
    title: "Receiving Note",
    dateLabel: "Received date",
    itemsLabel: "Received items",
    getNumber: (record) => record.receiving_number,
    getDate: (record) => record.received_date,
    party: [
      { label: "Supplier", get: (record) => record.supplier_name || "Manual source" },
      { label: "Prepared by", get: (record) => record.created_by_name },
      { label: "Status", get: (record) => statusText(record, "Recorded") }
    ],
    getNotes: (record) => record.notes
  },
  delivery: {
    title: "Delivery Note",
    dateLabel: "Delivery date",
    itemsLabel: "Delivered items",
    getNumber: (record) => record.delivery_number,
    getDate: (record) => record.delivery_date,
    party: [
      { label: "Client", get: (record) => record.client_name || record.customer_name },
      { label: "Receiver", get: (record) => record.receiver_name },
      { label: "From reservation", get: (record) => record.from_reservation_number },
      { label: "From repair", get: (record) => record.from_repair_number },
      { label: "Prepared by", get: (record) => record.created_by_name },
      { label: "Status", get: (record) => statusText(record, record.status === "draft" ? "Draft" : "Delivered") }
    ],
    getNotes: (record) => record.notes
  },
  issue: {
    title: "Assignment Note",
    dateLabel: "Assignment date",
    itemsLabel: "Assigned items",
    getNumber: (record) => record.issue_number,
    getDate: (record) => record.issue_date,
    party: [
      {
        label: "Assigned to",
        get: (record) => {
          const party = record.assigned_to_party;
          if (!party?.name) return "";
          return party.kind_label ? `${party.name} (${party.kind_label})` : party.name;
        }
      },
      { label: "Expected return", get: (record) => (record.expected_return_date ? formatDate(record.expected_return_date) : "") },
      { label: "Reason", get: (record) => record.reason },
      { label: "Assigned by", get: (record) => record.issued_by_name },
      { label: "Status", get: (record) => statusText(record, capitalize(record.status)) },
      { label: "Returned date", get: (record) => (record.returned_date ? formatDate(record.returned_date) : "") },
      { label: "Return reason", get: (record) => record.return_reason }
    ],
    getNotes: (record) => record.notes
  },
  client_return: {
    title: "Client Return Note",
    dateLabel: "Return date",
    itemsLabel: "Returned items",
    getNumber: (record) => record.return_number,
    getDate: (record) => record.return_date,
    party: [
      { label: "Client", get: (record) => record.client_name || record.customer_name },
      { label: "Received from", get: (record) => record.received_from },
      { label: "Original delivery", get: (record) => record.delivery_number },
      { label: "Reason", get: (record) => record.reason },
      { label: "Resolution", get: (record) => RESOLUTION_LABELS[record.resolution] || record.resolution },
      { label: "Received by", get: (record) => record.received_by_name },
      { label: "Status", get: (record) => statusText(record, "Recorded") }
    ],
    getNotes: (record) => record.notes
  }
};
