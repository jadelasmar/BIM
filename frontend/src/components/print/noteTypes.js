import { formatDate } from "../../utils/formatters";

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
      { label: "Prepared by", get: (record) => record.created_by_name }
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
      { label: "Prepared by", get: (record) => record.created_by_name }
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
      { label: "Assigned to", get: (record) => record.assigned_to_party?.name },
      { label: "Expected return", get: (record) => (record.expected_return_date ? formatDate(record.expected_return_date) : "") },
      { label: "Reason", get: (record) => record.reason },
      { label: "Assigned by", get: (record) => record.issued_by_name }
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
      { label: "Received by", get: (record) => record.received_by_name }
    ],
    getNotes: (record) => record.notes
  }
};
