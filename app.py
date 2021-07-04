from utils.webdriver_handler import scroll
from utils.setup import setSelenium
from utils.parser_handler import init_parser, remove_duplicates
from utils.file_handler import dataToExcel
from time import sleep

from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException


def verbose(text):
    verbose = True
    if verbose:
        print(text)


def getDetails(url):
    driver = setSelenium(False)
    driver.get(url)
    verbose('> Esperando página carregar...')
    driver.implicitly_wait(10)
    
    button_exists = True
    try:
        # click no botão para mostrar telefone
        verbose('> 1 Click no botão do telefone')
        driver.find_element_by_id('CardSellerPhoneViewPrivate').click()
    
    except ElementClickInterceptedException:
        verbose('> tentando remover popup se existe...')
        remove_popups(driver)
        driver.find_element_by_id('CardSellerPhoneViewPrivate').click()
        
    except NoSuchElementException:
        verbose('> Informações não achadas! continuando...')
        button_exists = False
        pass

    finally:
        sleep(5)

    if button_exists:
        time = 0
        while True :
            verbose('> verificando se o botão esta carregando...')
            if time >= 10:
                print('> Erro de rede ou não existe!')
                break

            try:
                driver.find_element_by_id('VehicleSellerPrivatePhone_0')
            
            except NoSuchElementException:
                sleep(5)
                time += 1

            else:
                verbose('> Telefone achado...')
                break


    verbose('> Raspando dados...')
    soap = parse_results(driver)
    driver.quit()

    data = {}
    data['Nome'] = soap.find('h2', id="VehicleSellerPrivateName").text
    try:
        data['Telefone'] = soap.find('strong', id="VehicleSellerPrivatePhone_0").text

    except AttributeError:
        data['Telefone'] = 'Não existete'

    data['Estado'] = soap.find('span', id="VehicleSellerPrivateState").text
    data['Tipo de pessoa'] = soap.find('p', id="VehicleSellerPrivateTypeAd").text

    print('\n')
    for key, value in data.items():
        print(f'> {key}: {value}')
    print('\n')

    dataToExcel({ 'Nome': [data['Nome']], 'Telefone': [data['Telefone']], 'Estado': [data['Estado']], 'Tipo de pessoa': [data['Tipo de pessoa']] }, 'web-motors.csv')


def parse_results(driver):
    html = driver.find_element_by_tag_name('html')
    src_code = html.get_attribute('outerHTML')
    return init_parser(src_code)


def remove_popups(driver):
    driver.find_element_by_css_selector('.modal--close').click()
    sleep(3)
    driver.find_element_by_css_selector('.sc-htoDjs.gtMZoW').click()


def main():
    '''
    Insert your code here
    '''
    print('~' *40)
    print(str('Web Motors crawler').center(40))
    print('~' *40)

    driver = setSelenium(False)
    
    try:
        driver.get("https://www.webmotors.com.br/carros-usados/estoque?tipoveiculo=carros-usados&precoate=500000&precode=100000&anunciante=Pessoa%20F%C3%ADsica")
        
        verbose('> Selecionando carros...')
        driver.implicitly_wait(10)
        scroll(driver)
        driver.implicitly_wait(20)

        soap = parse_results(driver)
        driver.quit()
        container = soap.find('div', class_="ContainerCardVehicle")

        raw_links = [link['href'] for link in container.find_all('a')]
        links = remove_duplicates(raw_links)

        verbose(f"> {len(links)} Carros encontrados!")
        
        for index, link in enumerate(links):
            verbose(f": Extraindo {index + 1} carro...")
            getDetails(link)
    
    except KeyboardInterrupt:
        verbose('> Saindo volte sempre...')
        driver.quit()

    except Exception:
        driver.quit()
        raise


if __name__ == "__main__":
    main()