import logoPrimary from "../../assets/brand/logo-primary.svg";
import { formatDate } from "../../utils/formatters";
import { NOTE_TYPES } from "./noteTypes";

function signedAtText(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "" : date.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

// The one printable A4 layout for Receiving, Delivery, Assignment and Client Return notes.
// groupedItems are the entries from groupGenericItems (real serials one line each, generic
// units one line with a count). The "print-sheet" class forces white/black so the sheet
// never follows the app theme. Restyle the note by editing this file and styles.css only.
export default function RecordNote({ type, record, groupedItems = [], signatures = [] }) {
  const config = NOTE_TYPES[type];
  if (!config || !record) return null;

  const partyRows = config.party
    .map((row) => ({ label: row.label, value: row.get(record) }))
    .filter((row) => row.value);
  const notes = config.getNotes(record);

  return (
    <article className="print-sheet" aria-label={config.title}>
      <header className="print-note-header">
        <img src={logoPrimary} alt="BIMPOS" className="print-note-logo" />
        <div className="print-note-heading">
          <h1>{config.title}</h1>
          <p className="print-note-number">{config.getNumber(record)}</p>
          <p>
            {config.dateLabel}: {formatDate(config.getDate(record))}
          </p>
        </div>
      </header>

      {partyRows.length ? (
        <dl className="print-note-party">
          {partyRows.map((row) => (
            <div key={row.label}>
              <dt>{row.label}</dt>
              <dd>{row.value}</dd>
            </div>
          ))}
        </dl>
      ) : null}

      <table className="print-note-table">
        <caption>{config.itemsLabel}</caption>
        <thead>
          <tr>
            <th>Product</th>
            <th>Serial</th>
            <th className="print-note-qty">Qty</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>
          {groupedItems.length ? (
            groupedItems.map((entry) => {
              const item = entry.item;
              const quantity = entry.items.reduce((total, member) => total + (member.quantity ?? 1), 0);
              const serial = item.serial_number || item.product_unit_serial_number;
              return (
                <tr key={entry.key}>
                  <td>
                    <strong>{item.product_name}</strong>
                    {item.product_sku ? <span className="print-note-sku">{item.product_sku}</span> : null}
                  </td>
                  <td>{entry.generic ? "No serial" : serial || "-"}</td>
                  <td className="print-note-qty">{entry.generic ? entry.count : quantity}</td>
                  <td>{item.notes || ""}</td>
                </tr>
              );
            })
          ) : (
            <tr>
              <td colSpan="4">No items on this record.</td>
            </tr>
          )}
        </tbody>
      </table>

      {notes ? (
        <section className="print-note-notes">
          <h2>Notes</h2>
          <p>{notes}</p>
        </section>
      ) : null}

      <section className="print-note-signatures">
        <h2>Signature</h2>
        {signatures.length ? (
          <div className="print-note-signature-list">
            {signatures.map((signature) => (
              <figure key={signature.id}>
                <img src={signature.image_url} alt={`Signature of ${signature.signer_name}`} />
                <figcaption>
                  <strong>{signature.signer_name || "Unnamed"}</strong>
                  {signature.role_label ? <span>{signature.role_label}</span> : null}
                  <span>
                    Captured by {signature.captured_by || "-"}, {signedAtText(signature.signed_at)}
                  </span>
                </figcaption>
              </figure>
            ))}
          </div>
        ) : (
          <div className="print-note-signature-empty">
            <div className="print-note-line" />
            <p>Signature, printed name and date</p>
          </div>
        )}
      </section>

      <footer className="print-note-footer">Built for BIMPOS</footer>
    </article>
  );
}
