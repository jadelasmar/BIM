import { forwardRef, useCallback, useEffect, useImperativeHandle, useRef } from "react";

const LOGICAL_WIDTH = 600;
const LOGICAL_HEIGHT = 200;
const INK = "#111827";
const LINE_WIDTH = 2.5;

// Freehand signature canvas. The drawing space is a fixed 600x200 logical grid, scaled
// to the container width (and to the device pixel ratio), so the saved PNG has the same
// proportions on a phone and a desktop. White background and dark ink in both themes.
// Reports a PNG data URL through onChange, or null while nothing is drawn.
const SignaturePad = forwardRef(function SignaturePad({ onChange, disabled = false }, ref) {
  const canvasRef = useRef(null);
  const strokesRef = useRef([]);
  const activeRef = useRef(null);

  const paint = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const scale = canvas.width / LOGICAL_WIDTH;
    ctx.setTransform(scale, 0, 0, scale, 0, 0);
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT);
    ctx.strokeStyle = INK;
    ctx.fillStyle = INK;
    ctx.lineWidth = LINE_WIDTH;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    strokesRef.current.forEach((stroke) => {
      if (stroke.length === 1) {
        ctx.beginPath();
        ctx.arc(stroke[0].x, stroke[0].y, LINE_WIDTH / 2, 0, Math.PI * 2);
        ctx.fill();
        return;
      }
      ctx.beginPath();
      ctx.moveTo(stroke[0].x, stroke[0].y);
      for (let i = 1; i < stroke.length; i += 1) ctx.lineTo(stroke[i].x, stroke[i].y);
      ctx.stroke();
    });
  }, []);

  const report = useCallback(() => {
    if (!onChange) return;
    if (!strokesRef.current.length) {
      onChange(null);
      return;
    }
    onChange(canvasRef.current.toDataURL("image/png"));
  }, [onChange]);

  // Keep the backing store sharp: sized from the rendered width and devicePixelRatio.
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return undefined;
    const resize = () => {
      const width = canvas.getBoundingClientRect().width || LOGICAL_WIDTH;
      const ratio = Math.max(window.devicePixelRatio || 1, 1);
      canvas.width = Math.round(width * ratio);
      canvas.height = Math.round((width * ratio * LOGICAL_HEIGHT) / LOGICAL_WIDTH);
      paint();
    };
    resize();
    if (typeof ResizeObserver === "undefined") return undefined;
    const observer = new ResizeObserver(resize);
    observer.observe(canvas);
    return () => observer.disconnect();
  }, [paint]);

  useImperativeHandle(
    ref,
    () => ({
      clear() {
        strokesRef.current = [];
        activeRef.current = null;
        paint();
        report();
      },
      undo() {
        strokesRef.current = strokesRef.current.slice(0, -1);
        paint();
        report();
      }
    }),
    [paint, report]
  );

  function pointFromEvent(event) {
    const rect = canvasRef.current.getBoundingClientRect();
    return {
      x: ((event.clientX - rect.left) / rect.width) * LOGICAL_WIDTH,
      y: ((event.clientY - rect.top) / rect.height) * LOGICAL_HEIGHT
    };
  }

  function handlePointerDown(event) {
    if (disabled) return;
    event.preventDefault();
    canvasRef.current.setPointerCapture?.(event.pointerId);
    const stroke = [pointFromEvent(event)];
    strokesRef.current.push(stroke);
    activeRef.current = stroke;
    paint();
  }

  function handlePointerMove(event) {
    if (!activeRef.current) return;
    event.preventDefault();
    activeRef.current.push(pointFromEvent(event));
    paint();
  }

  function handlePointerEnd(event) {
    if (!activeRef.current) return;
    activeRef.current = null;
    canvasRef.current.releasePointerCapture?.(event.pointerId);
    report();
  }

  return (
    <canvas
      ref={canvasRef}
      role="img"
      aria-label="Signature drawing area"
      className={`block w-full rounded-lg border border-nexus-line bg-white ${disabled ? "opacity-60" : "cursor-crosshair"}`}
      style={{ aspectRatio: `${LOGICAL_WIDTH} / ${LOGICAL_HEIGHT}`, touchAction: "none" }}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerEnd}
      onPointerCancel={handlePointerEnd}
    />
  );
});

export default SignaturePad;
