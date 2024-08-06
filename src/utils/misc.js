export const generateNumericCode = () => {
  // Get current date
  const date = new Date();
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0"); // Months are 0-based
  const day = String(date.getDate()).padStart(2, "0");
  const dateString = `${year}${month}${day}`;

  // Generate random numeric string
  const digits = "0123456789";
  const randomLength = 3;
  let randomString = "";
  for (let i = 0; i < randomLength; i++) {
    const randomIndex = Math.floor(Math.random() * digits.length);
    randomString += digits[randomIndex];
  }

  // Combine date and random string
  const numericCode = `${dateString}${randomString}`;
  return numericCode; // ex: 202408066967
};
