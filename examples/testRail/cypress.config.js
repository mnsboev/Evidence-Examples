const { defineConfig } = require("cypress");

module.exports = defineConfig({
  projectId: "my-example", // Replace with your actual project ID
  fixturesFolder: false,
  reporter: "cypress-multi-reporters",
  reporterOptions: {
    reporterEnabled: "mochawesome, mocha-junit-reporter",
    mochawesomeReporterOptions: {
      reportDir: "reports",
      reportFilename: "test-results.json",
      overwrite: false,
      html: false,
      json: true
    },
    mochaJunitReporterReporterOptions: {
      mochaFile: "reports/junit-results-[hash].xml",
      toConsole: false
    }
  },
  e2e: {
    supportFile: 'tests/support/e2e.js',
    setupNodeEvents(on, config) {},
    baseUrl: "http://localhost:3000",
    specPattern: "tests/e2e/*.cy.js"
  },
});
