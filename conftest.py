import pytest
import allure

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")

        if page is not None:
            allure.attach(
                str(report.longrepr),
                name="Failure details",
                attachment_type=allure.attachment_type.TEXT,
            )
            allure.attach(
                page.screenshot(),
                name="Failure screenshot",
                attachment_type=allure.attachment_type.PNG,
            )