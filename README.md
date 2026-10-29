# QA Automation Practice

> **Work in Progress** — This project is actively being developed as a hands-on learning and portfolio project. Features, test coverage, and CI workflows are evolving.

A practical QA automation project exploring API, UI, database, and authorization testing with Python. It combines automated testing, Keycloak-based authentication, and CI-generated Allure reports.

## Project Status

The core test automation workflow is running in GitHub Actions, with Allure reports published through GitHub Pages. The project is still evolving, with ongoing improvements to test coverage, reporting, and automation practices.

## Tech Stack

- **Language:** Python
- **Test Framework:** pytest
- **API Testing:** Requests
- **UI Automation:** Playwright
- **Backend:** FastAPI
- **Database:** SQLite
- **Authentication & Authorization:** Keycloak, OpenID Connect, OAuth 2.0 Authorization Code Flow with PKCE
- **Test Reporting:** Allure Reports
- **CI/CD:** GitHub Actions
- **Report Publishing:** GitHub Pages

## Current Test Coverage

- API endpoint testing
- Positive and negative authorization scenarios
- Role-based access control (`db_admin`, `db_reader`)
- Keycloak authentication using Authorization Code Flow with PKCE
- UI testing with Playwright
- Database testing
- Audit log testing
- Parameterized test cases
- Page Object Model (POM)
- Automated test execution in GitHub Actions

## Authentication & Authorization

The project uses Keycloak as an identity provider and implements OAuth 2.0 Authorization Code Flow with PKCE to obtain access tokens.

Role-based access control is tested through API requests. The test suite checks that authorized users can perform permitted operations while unauthorized users are denied access.

## Continuous Integration

GitHub Actions runs the automated test suite on pushes to `main` and pull requests targeting `main`.

The current pipeline:
1. Sets up the Python and Java environments.
2. Starts Keycloak and imports the test realm.
3. Creates test users and assigns their roles.
4. Starts the FastAPI application.
5. Executes the automated tests.
6. Generates an Allure HTML report.
7. Publishes the report to GitHub Pages after pushes to `main`.

## Test Report

[View the latest Allure HTML report](https://csposta-ship-it.github.io/qa-practice/)

## Project Goals

This project is an ongoing opportunity to develop practical QA automation skills, experiment with testing approaches, improve test reporting, and build a maintainable CI workflow. The implementation and documentation will continue to evolve as the project develops.
