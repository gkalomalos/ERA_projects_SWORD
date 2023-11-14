const rules = require("./webpack.rules");

rules.push({
  test: /\.css$/,
  use: [{ loader: "style-loader" }, { loader: "css-loader" }],
});

rules.push({
  test: /\.(png|jpg|gif|svg)$/,
  loader: "file-loader",
  options: {
    name: "[name].[ext]?[hash]",
  },
});

rules.push({
  test: /\.html$/,
  use: [
    {
      loader: "html-loader",
      options: {
        minimize: true,
      },
    },
  ],
});

module.exports = {
  module: {
    rules,
  },
};
