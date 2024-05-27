import React from "react";
import PropTypes from "prop-types";

import Box from "@mui/material/Box";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import Slide from "@mui/material/Slide";

import Loader from "./Loader";
import GearLoader from "../../assets/gear-loader.svg";

const Transition = React.forwardRef(function Transition(props, ref) {
  return <Slide direction="up" ref={ref} {...props} />;
});

const LoadModal = ({ open, message }) => {
  return (
    <>
      <Dialog
        open={open}
        TransitionComponent={Transition}
        keepMounted
        disableEscapeKeyDown={true}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle id="alert-dialog-title" textAlign="center">
          {"Running scenario"}
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description" textAlign="center">
            {message}
          </DialogContentText>
          <Box
            component="img"
            display="block"
            marginLeft="auto"
            marginRight="auto"
            alt="loader"
            src={GearLoader}
          />
        </DialogContent>
        <Box textAlign="center" sx={{ display: "flex", alignItems: "center" }}>
          <Loader />
        </Box>
      </Dialog>
    </>
  );
};

LoadModal.propTypes = {
  open: PropTypes.bool.isRequired,
  message: PropTypes.string.isRequired,
};

export default LoadModal;
