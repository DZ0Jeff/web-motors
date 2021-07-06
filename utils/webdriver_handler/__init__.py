from time import sleep


def scroll(driver):
    SCROLL_PAUSE_TIME = 20

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    # time = 0
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page and increments one more second
        SCROLL_PAUSE_TIME += 1
        sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

        # time += 1

        # if time >= 100:
        #     break


def dynamic_page(driver, url):
    driver.get(url)
    # driver.implicitly_wait(220)
    sleep(10)
    html = driver.find_element_by_tag_name('html')
    return html.get_attribute('outerHTML')


def check_tag(tag):
    try:
        handler = tag
        return handler

    except Exception as error:
        print('Error')
        return 'Não localizado...'
