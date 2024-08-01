import React, { forwardRef } from "react";
import PropTypes from "prop-types";

import { Snackbar, Stack } from "@mui/material";
import MuiAlert from "@mui/material/Alert";

import useStore from "../../store";

const Alert = forwardRef(function Alert(props, ref) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

const AlertMessage = () => {
  const { alertMessage, alertSeverity, alertShowMessage, setAlertShowMessage } = useStore();

  const handleCloseMessage = () => {
    setAlertShowMessage(false);
  };

  if (!(alertMessage && alertShowMessage)) {
    return null;
  }

  return (
    <Stack spacing={2} sx={{ width: "100%" }}>
      <Snackbar
        open={alertShowMessage}
        autoHideDuration={6000}
        onClose={handleCloseMessage}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert onClose={handleCloseMessage} severity={alertSeverity} sx={{ width: "100%" }}>
          {alertMessage}
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
