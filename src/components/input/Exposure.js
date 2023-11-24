import React from "react";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";

const Exposure = (props) => {
  return (
    <Box sx={{ minWidth: 250, maxWidth: 350, margin: 4 }}>
      <Typography
        id="exposure-dropdown"
        gutterBottom
        variant="h6"
        sx={{ fontWeight: "bold" }}
      >
        Exposure
      </Typography>

      <Box sx={{ display: "flex", gap: 2, justifyContent: "flex-start" }}>
        <Button
          variant="contained"
          sx={{ bgcolor: "#2A4D69", "&:hover": { bgcolor: "5C87B1" } }}
          onClick={props.onFetchChange}
        >
          Fetch
        </Button>

        <label
          htmlFor="exposure-contained-button-file"
          style={{ display: "inline-flex", alignItems: "center" }}
        >
          <Button
            component="span"
            variant="contained"
            sx={{ bgcolor: "#2A4D69", "&:hover": { bgcolor: "5C87B1" } }}
          >
            Load
          </Button>
          <input
            accept=".xlsx"
            hidden
            id="exposure-contained-button-file"
            multiple={false}
            onChange={props.onLoadChange}
            type="file"
          />
        </label>
      </Box>
    </Box>
  );
};

export default Exposure;
