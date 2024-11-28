import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import translationEN from "./locales/en.json";
import translationAR from "./locales/ar.json";
import translationTH from "./locales/th.json";

const resources = {
  en: {
    translation: translationEN,
  },
  ar: {
    translation: translationAR,
  },
  th: {
    translation: translationTH,
  },
};

// Custom post-processor to handle empty or whitespace-only translations
const fallbackWhitespacePostProcessor = {
  type: "postProcessor",
  name: "fallbackWhitespace",
  process(value, key, options, translator) {
    // Check if the value is null, undefined, empty, or whitespace-only
    if (value === undefined || value === null || /^\s*$/.test(value)) {
      // Fetch the English translation as a fallback
      const fallbackValue = translator(key, { ...options, lng: "en", postProcess: [] });
      return fallbackValue || key; // Return the key if fallback is also missing
    }
    return value; // Return the original value if it's not empty or whitespace
  },
};

// Register the custom post-processor
i18n.use(fallbackWhitespacePostProcessor);

// Initialize i18next with the custom post-processor
i18n.use(initReactI18next).init({
  resources,
  lng: "en", // Default language
  fallbackLng: "en", // Fallback language
  keySeparator: false, // We do not use keys in form messages.welcome

  interpolation: {
    escapeValue: false, // React already safes from xss
  },
  returnEmptyString: false, // Treat empty strings as missing keys
  postProcess: ["fallbackWhitespace"], // Use the custom post-processor
});

export default i18n;
