import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { Camera, Check, ScanBarcode, X } from "../../constants/icons";

const SCAN_FORMATS = [
  "code_128",
  "code_39",
  "code_93",
  "codabar",
  "ean_13",
  "ean_8",
  "upc_a",
  "upc_e",
  "itf",
  "qr_code",
  "data_matrix",
  "pdf417"
];
const SCAN_INTERVAL_MS = 200;

let detectorPromise = null;

// Chrome on Android has a built-in BarcodeDetector. Everywhere else (desktop
// Chrome on Windows, iPhone, a plain-HTTP page) the bundled zxing-wasm decoder is
// used instead; it is loaded on first scan so it never slows the normal page load,
// and its .wasm file is served from our own static files, not a CDN.
function getDetector() {
  if (!detectorPromise) {
    detectorPromise = (async () => {
      if ("BarcodeDetector" in window) {
        try {
          const supported = await window.BarcodeDetector.getSupportedFormats();
          const formats = SCAN_FORMATS.filter((format) => supported.includes(format));
          if (formats.includes("code_128")) {
            return new window.BarcodeDetector({ formats });
          }
        } catch {
          // Fall through to the bundled decoder.
        }
      }
      const [{ BarcodeDetector, setZXingModuleOverrides }, { default: wasmUrl }] = await Promise.all([
        import("barcode-detector/ponyfill"),
        import("zxing-wasm/reader/zxing_reader.wasm?url")
      ]);
      setZXingModuleOverrides({
        locateFile: (path, prefix) => (path.endsWith(".wasm") ? wasmUrl : prefix + path)
      });
      return new BarcodeDetector({ formats: SCAN_FORMATS });
    })();
    detectorPromise.catch(() => {
      detectorPromise = null;
    });
  }
  return detectorPromise;
}

function canUseLiveCamera() {
  return Boolean(window.isSecureContext && navigator.mediaDevices?.getUserMedia);
}

// Camera scanner. Every barcode seen is listed and the user taps the one to use,
// because device labels usually carry several (S/N, P/N, UPC). With `multiple`
// the scanner stays open so a whole batch of serials can be scanned in a row.
export function BarcodeScannerModal({ title = "Scan Barcode", multiple = false, onScan, onClose }) {
  const videoRef = useRef(null);
  const fileRef = useRef(null);
  const seenRef = useRef(new Set());
  const [codes, setCodes] = useState([]);
  const [used, setUsed] = useState([]);
  const [mode, setMode] = useState(canUseLiveCamera() ? "starting" : "photo");
  const [message, setMessage] = useState("");
  const [decoding, setDecoding] = useState(false);

  function addCodes(found) {
    const values = found.map((barcode) => String(barcode.rawValue || "").trim()).filter(Boolean);
    if (!values.length) return false;
    const fresh = values.filter((value) => !seenRef.current.has(value));
    if (fresh.length) {
      fresh.forEach((value) => seenRef.current.add(value));
      setCodes((current) => [...new Set([...fresh, ...current])]);
      navigator.vibrate?.(60);
    }
    return true;
  }

  useEffect(() => {
    function handleKeyDown(event) {
      if (event.key === "Escape") onClose();
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  useEffect(() => {
    if (!canUseLiveCamera()) return undefined;
    let cancelled = false;
    let stream = null;
    let timer = null;

    async function scanFrame(detector) {
      if (cancelled) return;
      const video = videoRef.current;
      if (video && video.readyState >= 2) {
        try {
          addCodes(await detector.detect(video));
        } catch {
          // A frame that cannot be read is skipped; the next one is tried.
        }
      }
      if (!cancelled) timer = window.setTimeout(() => scanFrame(detector), SCAN_INTERVAL_MS);
    }

    async function start() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          audio: false,
          video: { facingMode: { ideal: "environment" }, width: { ideal: 1920 }, height: { ideal: 1080 } }
        });
        if (cancelled) return;
        const [track] = stream.getVideoTracks();
        track?.applyConstraints({ advanced: [{ focusMode: "continuous" }] }).catch(() => {});
        const video = videoRef.current;
        video.srcObject = stream;
        await video.play();
        const detector = await getDetector();
        if (cancelled) return;
        setMode("live");
        scanFrame(detector);
      } catch (error) {
        if (cancelled) return;
        setMode("photo");
        setMessage(
          error?.name === "NotAllowedError"
            ? "Camera permission was refused. Allow the camera for this site in Chrome, or take a photo instead."
            : "The live camera could not start. Take a photo of the barcode instead."
        );
      }
    }

    start();
    return () => {
      cancelled = true;
      window.clearTimeout(timer);
      stream?.getTracks().forEach((track) => track.stop());
    };
  }, []);

  async function handlePhoto(event) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    setDecoding(true);
    setMessage("");
    try {
      const detector = await getDetector();
      const image = await createImageBitmap(file);
      const found = await detector.detect(image);
      image.close?.();
      if (!addCodes(found)) {
        setMessage("No barcode found in that photo. Hold the phone closer, keep the label flat and in focus, and try again.");
      }
    } catch {
      setMessage("That photo could not be read. Try again.");
    } finally {
      setDecoding(false);
    }
  }

  function chooseCode(code) {
    onScan(code);
    if (multiple) {
      setUsed((current) => [...current, code]);
    } else {
      onClose();
    }
  }

  const insecureHint = !window.isSecureContext;

  return createPortal(
    <div
      role="dialog"
      aria-modal="true"
      aria-label={title}
      className="fixed inset-0 z-[80] flex items-start justify-center overflow-y-auto bg-black/80 p-4 backdrop-blur-sm"
    >
      <div className="my-4 w-full max-w-md rounded-lg border border-nexus-line bg-nexus-panel shadow-2xl">
        <div className="flex items-start justify-between gap-4 border-b border-nexus-line px-5 py-4">
          <div>
            <h2 className="bim-section-title">{title}</h2>
            <p className="mt-1 text-sm text-zinc-400">
              {multiple ? "Tap each code to add it. Tap Done when finished." : "Point at the barcode, then tap the code to use."}
            </p>
          </div>
          <button type="button" onClick={onClose} aria-label="Close" className="text-zinc-400 hover:text-white">
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="grid gap-4 p-5">
          {mode !== "photo" ? (
            <div className="relative overflow-hidden rounded-lg border border-nexus-line bg-black">
              <video ref={videoRef} muted playsInline className="aspect-[4/3] w-full object-cover" />
              <div className="pointer-events-none absolute inset-x-[8%] top-1/2 h-1/3 -translate-y-1/2 rounded-md border-2 border-[var(--bim-orange-focus)]" />
              {mode === "starting" ? (
                <div className="absolute inset-0 grid place-items-center text-sm font-semibold text-zinc-300">Starting camera...</div>
              ) : null}
            </div>
          ) : null}

          {message ? (
            <div className="rounded-lg border border-[rgb(var(--bim-red-rgb)/60%)] bg-red-500/10 px-4 py-3 text-sm font-semibold text-[var(--tone-red-text)]">
              {message}
            </div>
          ) : null}

          {codes.length ? (
            <div className="overflow-hidden rounded-lg border border-nexus-line">
              {codes.map((code) => {
                const isUsed = used.includes(code);
                return (
                  <button
                    key={code}
                    type="button"
                    disabled={isUsed}
                    onClick={() => chooseCode(code)}
                    className="flex w-full items-center justify-between gap-3 border-b border-nexus-line px-4 py-3 text-left last:border-b-0 hover:bg-nexus-panel2 disabled:opacity-60"
                  >
                    <span className="break-all font-mono text-base font-bold text-white">{code}</span>
                    {isUsed ? (
                      <span className="inline-flex shrink-0 items-center gap-1 text-xs font-semibold text-[var(--tone-green-text)]">
                        <Check className="h-4 w-4" />
                        Added
                      </span>
                    ) : (
                      <span className="shrink-0 text-xs font-semibold text-[var(--bim-orange-text)]">{multiple ? "Add" : "Use"}</span>
                    )}
                  </button>
                );
              })}
            </div>
          ) : mode === "live" ? (
            <p className="text-center text-sm text-zinc-500">Looking for barcodes...</p>
          ) : null}

          <input ref={fileRef} type="file" accept="image/*" capture="environment" className="hidden" onChange={handlePhoto} />
          <div className="flex flex-wrap items-center justify-between gap-3">
            <button
              type="button"
              disabled={decoding}
              onClick={() => fileRef.current?.click()}
              className={
                mode === "photo"
                  ? "inline-flex h-10 items-center gap-2 rounded-md bg-nexus-orange px-4 text-sm font-semibold text-black"
                  : "inline-flex h-9 items-center gap-2 rounded-md px-3 text-sm font-semibold text-zinc-300 hover:bg-nexus-panel2"
              }
            >
              <Camera className="h-4 w-4" />
              {decoding ? "Reading photo..." : mode === "photo" ? "Take Photo of Barcode" : "Take photo instead"}
            </button>
            {multiple ? (
              <button
                type="button"
                onClick={onClose}
                className="inline-flex h-10 items-center gap-2 rounded-md border border-nexus-line px-4 text-sm font-semibold text-zinc-200 hover:bg-nexus-panel2"
              >
                Done
              </button>
            ) : null}
          </div>

          {insecureHint ? (
            <p className="text-xs leading-5 text-zinc-500">
              The live camera needs a secure site. To turn it on in Chrome on Android, open <span className="font-mono">chrome://flags</span>,
              search "Insecure origins treated as secure", add <span className="font-mono">{window.location.origin}</span>, set it to
              Enabled and relaunch Chrome.
            </p>
          ) : null}
        </div>
      </div>
    </div>,
    document.body
  );
}

export function ScanButton({ onScan, multiple = false, title, label = "Scan barcode", className = "" }) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button
        type="button"
        onClick={(event) => {
          event.preventDefault();
          setOpen(true);
        }}
        aria-label={label}
        title={label}
        className={`inline-flex shrink-0 items-center justify-center text-zinc-400 hover:text-[var(--bim-orange-text)] ${className}`.trim()}
      >
        <ScanBarcode className="h-4 w-4" aria-hidden="true" />
      </button>
      {open ? (
        <BarcodeScannerModal title={title} multiple={multiple} onScan={onScan} onClose={() => setOpen(false)} />
      ) : null}
    </>
  );
}
