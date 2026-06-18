/** @type {import('@commitlint/types').UserConfig} */
export default {
  extends: ["@commitlint/config-conventional"],
  rules: {
    "scope-enum": [
      1,
      "always",
      ["mock-netsuite", "intelligence", "owner-app", "domain", "ci", "docs", "repo"],
    ],
  },
};
