import js from "@eslint/js"
import globals from "globals"
import react from "eslint-plugin-react"
import reactHooks from "eslint-plugin-react-hooks"

export default [
  { ignores: ["node_modules/**"] },
  js.configs.recommended,
  {
    files: ["**/*.{js,jsx}"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      parserOptions: { ecmaFeatures: { jsx: true } },
      globals: { ...globals.browser },
    },
    settings: { react: { version: "detect" } },
    plugins: { react, "react-hooks": reactHooks },
    rules: {
      ...react.configs.recommended.rules,
      ...react.configs["jsx-runtime"].rules,
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "warn",
      // Props are shaped by Django; there are no PropTypes in this project.
      "react/prop-types": "off",
      "no-unused-vars": ["error", { varsIgnorePattern: "^React$", argsIgnorePattern: "^_" }],
    },
  },
  {
    files: ["*.config.js", "eslint.config.js"],
    languageOptions: { globals: { ...globals.node } },
  },
]
