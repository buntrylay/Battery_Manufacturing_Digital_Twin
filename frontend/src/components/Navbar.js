import React from "react";
import { Link } from "react-router-dom";

const Navbar = () => (
  <nav>
    <ul>
      <li>
        <Link to="/">Home</Link>
      </li>
      <li>
        <Link to="/logs">Live Logs</Link>
      </li>
      <li>
        <Link to="/testing">Testing Page</Link>
      </li>
    </ul>
  </nav>
);

export default Navbar;
