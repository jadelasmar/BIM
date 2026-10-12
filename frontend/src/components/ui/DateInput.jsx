import Input from "./Input";

// The one date input every operation form uses. It takes and returns a plain
// "YYYY-MM-DD" string (the format the API stores), so a form's state can go
// straight into its request body.
export default function DateInput({ value, onChange, disabled = false, min, max }) {
  return (
    <Input
      type="date"
      value={value || ""}
      onChange={(event) => onChange?.(event.target.value)}
      disabled={disabled}
      min={min}
      max={max}
    />
  );
}
