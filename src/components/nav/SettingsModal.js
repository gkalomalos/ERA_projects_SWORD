import React from "react";

import Modal from "@mui/material/Modal";

const SettingsModal = ({ isSettingsModalOpen, handleCloseSettings }) => {
  const modalStyle = {
    position: "absolute",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    width: 400,
    bgcolor: "background.paper",
    border: "2px solid #000",
    boxShadow: 24,
    p: 4,
  };

  return (
    <Modal
      open={isSettingsModalOpen}
      onClose={handleCloseSettings}
      aria-labelledby="modal-modal-title"
      aria-describedby="modal-modal-description"
    >
      <div style={modalStyle}>
        <h2 id="modal-modal-title">Settings</h2>
        <p id="modal-modal-description">Your settings content goes here.</p>
      </div>
    </Modal>
  );
};

export default SettingsModal;
