import React from "react";
import { Link } from "react-router-dom";
//Navbar component with links to different pages
const Navbar = () => (
  <nav className="nav-container">
    <ul className="nav-links">
      <li>
        <Link to="/">Flow Page</Link>
      </li>
      <li>
        <Link to="/logs">Live Logs</Link>
      </li>
      <li>
        <Link to="/realtime">Real-Time Data</Link>
      </li>
    </ul>
  </nav>
);

export default Navbar;
