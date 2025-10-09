import React, { useState } from "react";
import "../styles/ToggleSwitch.css";

function ToggleSwitch({ label, infoContent }) {
  const [isToggled, setIsToggled] = useState(false);

  const handleToggle = () => setIsToggled(!isToggled);

  return (
    <div className="toggle-container">
      <div className="toggle-row">
        <button
          className="toggle-icon-btn"
          onClick={handleToggle}
          aria-label={label}
        >
          <span
            className={
              isToggled ? "mdi--information" : "mdi--information-outline"
            }
          />
        </button>
        <span className="toggle-text">{label}</span>
      </div>
      <div className={`info-content${isToggled ? " visible" : ""}`}>
        {infoContent}
      </div>
    </div>
  );
}

export default ToggleSwitch;
