import pytest
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import chromedriver_autoinstaller

# Chrome WebDriver automatikus telepítése
chromedriver_autoinstaller.install()

# HTML fájl beolvasása
def load_html():
    file_path = os.path.abspath("index.html")
    if not os.path.exists(file_path):
        pytest.fail("Az index.html fájl nem található!")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture()
def soup():
    return BeautifulSoup(load_html(), "html.parser")

@pytest.fixture(scope="module")
def browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Futtatás fej nélküli módban
    driver = webdriver.Chrome(options=options)
    file_path = f"file://{os.path.abspath('index.html')}"
    driver.get(file_path)
    yield driver
    driver.quit()

def test_html_structure(soup):
    assert soup.find("html"), "Hiányzik a <html> elem."
    assert soup.find("head"), "Hiányzik a <head> elem."
    assert soup.find("body"), "Hiányzik a <body> elem."

def test_document_language(soup):
    assert soup.html.get("lang") == "hu", "A dokumentum nyelve nem magyar."

def test_meta_charset(soup):
    meta = soup.find("meta", charset=True)
    assert meta and meta.get("charset", "").lower() == "utf-8", "A karakterkódolás nem UTF-8."

def test_title(soup):
    title = soup.find("title")
    assert title and title.text.strip() == "Kék téglalapok", "Az oldal címe nem megfelelő."

def test_container_exists(soup):
    assert soup.find("div", class_="container"), "Hiányzik a container div."

def test_rectangles(soup):
    container = soup.find("div", class_="container")
    assert container and len(container.find_all("div", class_="rectangle")) == 6, "Nem megfelelő számú téglalap található az oldalon."

def test_container_styles(browser):
    container = browser.find_element(By.CLASS_NAME, "container")
    assert "600px" in container.value_of_css_property("width"), "A container szélessége nem megfelelő."
    assert "600px" in container.value_of_css_property("max-width"), "A container maximális szélessége nem megfelelő."
    assert "50px" in container.value_of_css_property("margin-top"), "A container felső margója nem megfelelő."

def test_rectangle_styles(browser):
    rectangles = browser.find_elements(By.CLASS_NAME, "rectangle")
    assert len(rectangles) == 6, "Nem megfelelő számú téglalap van az oldalon."
    for rect in rectangles:
        assert "600px" in rect.value_of_css_property("width"), "A téglalap szélessége nem megfelelő."
        assert "rgba(0, 0, 255, 1)" in rect.value_of_css_property("background-color"), "A téglalap háttérszíne nem megfelelő."
        assert "3px" in rect.value_of_css_property("border-width"), "A téglalap határoló vonala nem megfelelő vastagságú."
        assert "rgb(173, 216, 230)" in rect.value_of_css_property("border-color"), "A téglalap határoló vonala nem megfelelő színű."


@pytest.hookimpl(tryfirst=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    total_tests = len(terminalreporter.stats.get("passed", []))
    print(f"\nÖsszes pontszám: {total_tests * 2}/20")
