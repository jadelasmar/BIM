import { useEffect, useRef } from "react";
import JsBarcode from "jsbarcode";
import { Button } from "../../components/ui";

const TEST_PRODUCT_NAME = "Test Product";
const TEST_SKU = "BIM-TEST-0001";

export default function PrintLabelTestPage() {
  const barcodeRef = useRef(null);

  useEffect(() => {
    if (!barcodeRef.current) {
      return;
    }

    JsBarcode(barcodeRef.current, TEST_SKU, {
      format: "CODE128",
      width: 1.5,
      height: 32,
      displayValue: true,
      fontSize: 11,
      margin: 0
    });
  }, []);

  return (
    <div className="print-label-test-page">
      <style>{`
        .print-label-test-page {
          min-height: 100vh;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 1.5rem;
          padding: 2rem 1rem;
          background: #e4e4e7;
        }

        .print-label-test-page__intro {
          max-width: 28rem;
          text-align: center;
          color: #27272a;
        }

        .print-label-test-page__intro h1 {
          font-size: 1.25rem;
          font-weight: 700;
          margin-bottom: 0.5rem;
        }

        .print-label-test-page__intro p {
          font-size: 0.875rem;
          color: #52525b;
        }

        .print-label {
          width: 55mm;
          height: 40mm;
          box-sizing: border-box;
          background: #fff;
          border: 1px solid #d4d4d8;
          border-radius: 4px;
          padding: 2mm;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 1.5mm;
          font-family: Arial, Helvetica, sans-serif;
          color: #000;
        }

        .print-label__name {
          width: 100%;
          font-size: 12pt;
          font-weight: 700;
          text-align: center;
          word-break: break-word;
        }

        .print-label__barcode {
          width: 100%;
          height: auto;
        }

        @media print {
          @page {
            size: 55mm 40mm;
            margin: 0;
          }

          html, body {
            margin: 0;
            padding: 0;
            background: #fff;
          }

          .print-label-test-page {
            min-height: 0;
            padding: 0;
            background: #fff;
          }

          .no-print {
            display: none !important;
          }

          .print-label {
            width: 55mm;
            height: 40mm;
            border: none;
            border-radius: 0;
          }
        }
      `}</style>

      <div className="no-print print-label-test-page__intro">
        <h1>Print Label Test</h1>
        <p>
          Standalone route for validating the label print pipeline. Click Print, or use your
          browser's print preview, to confirm only the label below is rendered.
        </p>
      </div>

      <div className="print-label">
        <div className="print-label__name">{TEST_PRODUCT_NAME}</div>
        <svg ref={barcodeRef} className="print-label__barcode" />
      </div>

      <div className="no-print">
        <Button variant="primary" onClick={() => window.print()}>
          Print
        </Button>
      </div>
    </div>
  );
}
