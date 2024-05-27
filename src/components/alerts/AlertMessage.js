import React, { forwardRef } from "react";
import PropTypes from "prop-types";

import { Snackbar, Stack } from "@mui/material";
import MuiAlert from "@mui/material/Alert";

const Alert = forwardRef(function Alert(props, ref) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

const AlertMessage = ({ handleCloseMessage, message, severity, showMessage }) => {
  return (
    <Stack spacing={2} sx={{ width: "100%" }}>
      <Snackbar
        open={showMessage}
        autoHideDuration={6000}
        onClose={handleCloseMessage}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert onClose={handleCloseMessage} severity={severity} sx={{ width: "100%" }}>
          {message}
        </Alert>
      </Snackbar>
    </Stack>
  );
};

AlertMessage.propTypes = {
  handleCloseMessage: PropTypes.func.isRequired,
  message: PropTypes.string.isRequired,
  severity: PropTypes.oneOf(["error", "warning", "info", "success"]).isRequired,
  showMessage: PropTypes.bool.isRequired,
};

export default AlertMessage;
