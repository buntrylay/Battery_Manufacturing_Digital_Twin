import React from "react";
import { Link } from "react-router-dom";

const Navbar = () => (
  <nav className="nav-container">
    <ul className="nav-links">
      <li>
        <Link to="/">Home</Link>
      </li>
      <li>
        <Link to="/logs">Live Logs</Link>
      </li>
      <li>
        <Link to="/testing">Testing Page</Link>
      </li>
      <li>
        <Link to="/flow">Flow Page</Link>
      </li>
      <li>
        <Link to="/realtime">Real-Time Data</Link> {/* ✅ new menu item */}
      </li>
    </ul>
  </nav>
);

export default Navbar;
