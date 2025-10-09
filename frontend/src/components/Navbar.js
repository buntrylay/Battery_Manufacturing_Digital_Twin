import React from "react";
import { Link } from "react-router-dom";
//Navbar component with links to different pages
const Navbar = () => (
  <nav className="nav-container">
    <ul className="nav-links">
      <li>
        {/* Simulation Flow Page*/}
        <Link to="/">Simulation</Link>
      </li>
      {/* Live Logs of Simulation Page */}
      <li>
        <Link to="/logs">Live Logs</Link>
      </li>
      {/* Real-Time Data Page */}
      <li>
        <Link to="/realtime">Simulation Data</Link>
      </li>
    </ul>
  </nav>
);

export default Navbar;
