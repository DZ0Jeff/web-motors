import json
import requests
from utils.webdriver_handler import scroll
from utils.setup import setSelenium
from utils.parser_handler import init_parser, remove_duplicates, init_crawler
from utils.file_handler import dataToExcel, load_index, load_links, remove_duplicates_txt, save_index, save_to_json
from time import sleep
import requests
import os

from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, JavascriptException


def get_tag(soap, tag, attribute):
    try:
        text_tag = soap.find(tag, id=attribute).get_text()
        return text_tag

    except AttributeError:
        return ''


def get_tag_class(soap, tag, attribute):
    try:
        text_tag = soap.find(tag, class_=attribute).get_text()
        return text_tag

    except AttributeError:
        return ''


def verbose(text):
    verbose = True
    if verbose:
        print(text)


def getCarsByLink():
    def make_requests(actualPage):
        limit = 24
        url = f'https://www.webmotors.com.br/api/search/car?url=https://www.webmotors.com.br/carros%2Festoque%3F&actualPage={actualPage}&displayPerPage={limit}&order=1&showMenu=true&showCount=true&showBreadCrumb=true&testAB=false&returnUrl=false'
        url_filtro = f"https://www.webmotors.com.br/api/search/car?url=https://www.webmotors.com.br/carros%2Festoque%3Ftipoveiculo%3Dcarros%26precode%3D100000%26anunciante%3DPessoa%2520F%25C3%25ADsica&actualPage={actualPage}&displayPerPage={limit}&order=1&showMenu=true&showCount=true&showBreadCrumb=true&testAB=false&returnUrl=false"
        
        req = requests.get(url_filtro)

        return req


    def extract_link(data):
        cars_link = []
        for car in data["SearchResults"]:
            id = car["UniqueId"]
            make = car["Specification"]['Make']['Value']
            version = car["Specification"]["Version"]["Value"]
            model = car["Specification"]["Model"]["Value"]
            ports = f"{car['Specification']['NumberPorts']}-portas"
            year = car["Specification"]["YearFabrication"]

            link = f"https://www.webmotors.com.br/comprar/{make}/{model}/{version}/{ports}/{year}/{id}"
            cars_link.append(link)
        
        # print(f"{len(cars_link)} Extraídos", end="\r")
        return cars_link

    
    i = 1
    while True:
        
        try:
            req = make_requests(i)
        
        except Exception as error:
            print(f'> {error}')
            break

        data = req.json()
        links = extract_link(data)
        with open('links.txt','a') as file:
            for link in links:
                file.write(f'{link}\n')

        print(f'{i} páginas extraídas!', end="\r")

        i += 1

        if not "SearchResults" in data or len(data["SearchResults"]) == 0:
            break

        # if i < 5:
        #     break

    remove_duplicates_txt()


def getDetails(driver, url):
    try:
        driver.get(url)
        verbose('> Esperando página carregar...')
        driver.implicitly_wait(10)

        remove_cookie_warning(driver)
        button_exists = True
        try:
            # click no botão para mostrar telefone
            verbose('> Clicando no botão do telefone')
            driver.find_element_by_id('CardSellerPhoneViewPrivate').click()
        
        except ElementClickInterceptedException:
            # se existe um pop up remove-lo
            verbose('> tentando remover popup se existe...')
            remove_popups(driver)
            driver.find_element_by_id('CardSellerPhoneViewPrivate').click()
            
        except NoSuchElementException:
            # continua se o botão não existe
            verbose('> Informações não achadas! continuando...')
            button_exists = False
            pass

        finally:
            sleep(5)

        # extrair telefone se o botão existe
        if button_exists:
            time = 0
            while True :
                print('> verificando se o botão esta carregando...', end="\r")
                if time >= 10:
                    verbose('> Erro de rede ou não existe!')
                    break

                try:
                    driver.find_element_by_css_selector('.CardSeller__phone__number.CardSeller__phone__number--active')
                
                except NoSuchElementException:
                    sleep(5)
                    time += 1

                else:
                    verbose('> Telefone achado...')
                    break


        verbose('> Raspando dados...')
        soap = parse_results(driver)

        data = {}

        data['Preço'] = [get_tag(soap, 'strong', 'vehicleSendProposalPrice')]
        data['Modelo'] = [get_tag(soap, 'h1', "VehicleBasicInformationTitle")]
        data['Ano'] = [get_tag(soap, 'strong', "VehiclePrincipalInformationYear")]
        data['KM'] = [get_tag(soap, 'strong','VehiclePrincipalInformatiOnodometer')]
        data['Câmbio'] = [get_tag(soap, 'strong', 'VehiclePrincipalInformationTransmission')]
        data['Chassis'] = [get_tag(soap, 'strong', 'VehiclePrincipalInformationBodyType')]
        data['Combustível'] = [get_tag(soap, 'strong', "VehiclePrincipalInformationFuel")]
        data['Troca?'] = [get_tag(soap, 'strong','VehiclePrincipalInformationFuel')]
        data['Final da placa'] = [get_tag(soap, 'strong', 'VehiclePrincipalInformationFinalPlate')]
        data['Cor'] = [get_tag(soap, 'strong', 'VehiclePrincipalInformationColor')]
        data['Unico dono?'] = [get_tag(soap, 'strong', 'VehicleCharacteristicPos2')]
        data['Licenciado?'] = [get_tag(soap, 'strong', 'VehicleCharacteristicPos1')]
        try:
            data['Items'] = [soap.find('ul', class_='VehicleDetails__list VehicleDetails__list--items').get_text(separator=" ")]
        
        except AttributeError:
            data['Items'] = ""

        data['Nome'] = get_tag(soap, 'h2', 'VehicleSellerPrivateName')
        data['Telefone'] = get_tag_class(soap, 'strong', 'CardSeller__phone__number CardSeller__phone__number--active')
        data['Estado'] = get_tag(soap, 'span', 'VehicleSellerPrivateState')
        data['Link'] = [url.replace('\n','')]

        # print('\n')
        # for key, value in data.items():
        #     print(f'> {key}: {value}')
        # print('\n')

        dataToExcel(data, 'web-motors.csv')

    except Exception as error:
        driver.quit()
        print(f'> {error}')
        raise


def getCars(driver):
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


def parse_results(driver):
    html = driver.find_element_by_tag_name('html')
    src_code = html.get_attribute('outerHTML')
    return init_parser(src_code)


def remove_popups(driver):
    try:
        print('> Removendo Popup')
        modal = driver.find_element_by_xpath('//*[@id="root"]/div[4]/div[2]/div/div[1]/img')
        modal.click()
        # driver.find_element_by_css_selector('img.--close-modal').click()

    except NoSuchElementException:
        try:
            modal = driver.find_element_by_xpath('//*[@id="root"]/div[4]/div[2]/div/div[1]')
            modal.click()

        except Exception:
            print('Unable to get modal')


def remove_cookie_warning(driver):
    try:
        driver.find_element_by_css_selector('.sc-htoDjs.gtMZoW').click()
    
    except ElementClickInterceptedException:
        remove_popups(driver)
        driver.find_element_by_css_selector('.sc-htoDjs.gtMZoW').click()

    except Exception:
        pass


def main():
    '''
    Insert your code here
    '''
    print('~' *40)
    print(str('Web Motors crawler').center(40))
    print('~' *40)

    getCarsByLink()
    links = load_links('links_sanitized')
    
    print(f"> {len(links)} links encontrados!")
    driver = setSelenium(False)
    try:
        for index, link in enumerate(links):
            if index >= int(load_index()):
                print(f'> Extraíndo {index} de {len(links)}')
                getDetails(driver, link)
                save_index(index)

                if index != 0 and index % 1000 == 0:
                    driver.quit()
                    print('> Esperando 1 hora...')
                    sleep(3600)
                    driver = setSelenium(False)
        
        driver.quit()
        print('> Finalizado!')

    except KeyboardInterrupt:
        verbose('> Saindo volte sempre...')
        driver.quit()
        exit()

    os.remove('links_sanitized.txt')
    os.remove('index.txt')

if __name__ == "__main__":
    main()