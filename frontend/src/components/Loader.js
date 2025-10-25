import React from "react";

function Loader() {
  const loaderStyle = {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    height: "60vh",
    flexDirection: "column",
    color: "#007bff",
  };

  const spinnerStyle = {
    width: "4rem",
    height: "4rem",
    border: "0.4rem solid rgba(0, 0, 0, 0.1)",
    borderTop: "0.4rem solid #007bff",
    borderRadius: "50%",
    animation: "spin 1s linear infinite",
  };

  return (
    <div style={loaderStyle}>
      <div style={spinnerStyle}></div>
      <p style={{ marginTop: "1rem", fontWeight: "500" }}>Loading...</p>
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
}

export default Loader;
