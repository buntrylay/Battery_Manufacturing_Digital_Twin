import React from "react";
import swinLogo from "../assets/swinburneLogo.jpg";
import syncLogo from "../assets/syncrowinLogo.jpg";
function Footer() {
  return (
    <footer>
      <div className="footer-title-area">
        <h2>battery manufacturing simulation</h2>
      </div>
      <div className="footer-text-area">
        <div className="footer-logo">
          <img src={swinLogo} alt="Swinburne Logo" />
        </div>
        <p>https://www.syncrowin.com.au/</p>
        <div className="footer-logo">
          <img src={syncLogo} alt="Syncrowin Logo" />
        </div>
      </div>
    </footer>
  );
}

export default Footer;
