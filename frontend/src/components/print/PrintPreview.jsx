import { useEffect } from "react";
import { createPortal } from "react-dom";
import RecordNote from "./RecordNote";

// Full-screen white overlay with the A4 sheet, Print and Close. Rendered into document.body
// so the print stylesheet can hide the rest of the app and print only the sheet.
export default function PrintPreview({ open, onClose, ...noteProps }) {
  useEffect(() => {
    if (!open) return undefined;
    function onKey(event) {
      if (event.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  return createPortal(
    <div className="print-portal" role="dialog" aria-modal="true" aria-label="Print preview">
      <div className="print-toolbar">
        <button type="button" className="print-toolbar-primary" onClick={() => window.print()}>
          Print
        </button>
        <button type="button" onClick={onClose}>
          Close
        </button>
      </div>
      <div className="print-stage">
        <RecordNote {...noteProps} />
      </div>
    </div>,
    document.body
  );
}
