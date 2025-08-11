import React from "react";

function TestingPage() {
  const downloadZip = (type) => {
    window.open(`http://localhost:8000/files/${type}`, "_blank");
  };

  const downloadAllResults = () => {
    window.open("http://localhost:8000/files/all", "_blank");
  };

  return (
    <div className="container">
      <h2>Download Results</h2>
      <div className="actions">
        <button onClick={() => downloadZip("Anode")}>
          Download Anode results
        </button>
        <button onClick={() => downloadZip("Cathode")}>
          Download Cathode results
        </button>
        <button onClick={downloadAllResults}>Download All Results</button>
      </div>
    </div>
  );
}

export default TestingPage;
