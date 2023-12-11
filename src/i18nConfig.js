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

i18n.use(initReactI18next).init({
  resources,
  lng: "en", // Default language
  fallbackLng: "en", // Fallback language
  keySeparator: false, // We do not use keys in form messages.welcome

  interpolation: {
    escapeValue: false, // React already safes from xss
  },
});

export default i18n;
