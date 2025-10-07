import React, { useState } from "react";
import "../styles/ToggleSwitch.css";

function ToggleSwitch({ label, infoContent }) {
  const [isToggled, setIsToggled] = useState(false);

  const handleToggle = () => {
    setIsToggled(!isToggled);
  };

  return (
    <div className="toggle-container">
      <div className="toggle-row">
        <button
          className="toggle-icon-btn"
          onClick={handleToggle}
          aria-label={label}
        >
          {isToggled ? (
            <span className="mdi--information-outline"></span>
          ) : (
            <span className="mdi--information"></span>
          )}
        </button>
        <span className="toggle-text">{label}</span>
      </div>
      {isToggled && <div className="info-content">{infoContent}</div>}
    </div>
  );
}
export default ToggleSwitch;
