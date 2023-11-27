import csv
import time

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By


def slow_scroll_mouse(scroll_length, max_range, browser):
    current_scroll_length = scroll_length
    for _ in range(max_range):
        browser.execute_script(f'window.scrollTo(0, {current_scroll_length})')
        # Увеличиваем позицию прокрутки на заданную длину
        current_scroll_length += scroll_length
        # Задержка для создания эффекта медленной прокрутки
        time.sleep(0.3)


def find_table_rows(browser):
    table_rows = browser.find_elements(By.CSS_SELECTOR,
                                       '#livePreTable > tbody > tr')
    return table_rows


def create_list(table_rows):
    name_price_list = []
    for row in table_rows:
        columns = row.find_elements(By.CSS_SELECTOR, 'td')
        name = columns[1].text

        if 'Total' not in name:
            price = columns[6].text
            name_price_list.append([name, price])

    return name_price_list


def writing_table_items(lists_name_price):
    for element_name_price in lists_name_price:
        with open('data.csv', 'a', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(
                element_name_price
            )


# Пользовательский сценарий по своему желанию.
def simulate_user_screnario(browser):
    # Заходим на главную страницу.
    browser.get("https://www.nseindia.com")
    time.sleep(16)

    # Листаем вниз, чтобы было видно View all
    slow_scroll_mouse(50, 10, browser)

    # Находим view all, удаляем куки, кликаем.
    view_all_button = browser.find_element(By.CSS_SELECTOR, "div.link-wrap a")
    browser.delete_all_cookies()
    view_all_button.click()

    # Имитируем ожидание и скроллинг таблицы.
    time.sleep(3)
    slow_scroll_mouse(70, 10, browser)
    time.sleep(5)

    browser.quit()


def setup_browser():
    options = webdriver.ChromeOptions()
    options.add_argument(
        '--user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) '
        'Gecko/20100101 Firefox/89.0')
    webdriver.Chrome(options=options)
    browser = webdriver.Chrome()
    browser.get('https://www.nseindia.com')
    browser.implicitly_wait(2)
    return browser


def navigate_to_pre_open_market(browser):
    time.sleep(16)
    browser.delete_all_cookies()
    market_data_hover = browser.find_element(By.CSS_SELECTOR,
                                             'a#link_2')
    pre_open_market_click = browser.find_element(By.CSS_SELECTOR,
                                                 'ul.nav.flex-column a.nav-link')

    actions = ActionChains(browser)
    actions.move_to_element(market_data_hover).move_to_element(
        pre_open_market_click).click().perform()
    time.sleep(2)


def main():
    browser = setup_browser()
    navigate_to_pre_open_market(browser)
    slow_scroll_mouse(30, 10, browser)
    table_rows = find_table_rows(browser)
    table_items = create_list(table_rows)
    writing_table_items(table_items)
    browser.delete_all_cookies()
    simulate_user_screnario(browser)


if __name__ == "__main__":
    main()
