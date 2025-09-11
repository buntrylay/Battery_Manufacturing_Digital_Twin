// components/ElectrodeInput.js
export default function ElectrodeInput({ type, data, onChange }) {
  return (
    <div className="input-group">
      <h3>{type} Input</h3>
      {["PVDF", "CA", "AM", "Solvent"].map((field) => (
        <input
          key={field}
          type="number"
          placeholder={`${field} ratio`}
          value={data[field]}
          onChange={(e) => onChange(type, field, e.target.value)}
          step="0.01"
          min="0"
          max="1"
        />
      ))}
    </div>
  );
}
