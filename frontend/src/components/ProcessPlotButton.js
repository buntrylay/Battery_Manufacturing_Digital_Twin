// import React, { useState } from "react";
// // import { API_URL } from "../services/api"; // your API base URL

// function ProcessPlotButton({ processName }) {
//   const [imageUrl, setImageUrl] = useState(null);

//   const handleGenerate = async () => {
//     try {
//       const response = await fetch(`${API_URL}/plots/process/${processName}`);
//       if (!response.ok) throw new Error("Failed to fetch plot");

//       const blob = await response.blob();
//       const url = URL.createObjectURL(blob);
//       setImageUrl(url);
//     } catch (err) {
//       console.error(err);
//     }
//   };

//   return (
//     <div>
//       <button onClick={handleGenerate}>Generate Plot</button>
//       {imageUrl && <img src={imageUrl} alt={`${processName} plot`} />}
//     </div>
//   );
// }

// export default ProcessPlotButton;
