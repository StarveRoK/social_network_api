import json
from pathlib import Path
import vk_api

from loguru import logger
import os
from dotenv import load_dotenv
import requests

load_dotenv()


class ApiOk:

    def __init__(self, token, app_key, secret_key):

        """
        StarveR api to connect ok.ru
        :param token: Permanent or temporary application token
        :param app_key: The public key of the application
        :param secret_key: Secret key of the application
        """

        self.token_ok_ru = token
        self.app_key = app_key
        self.secret_key = secret_key
        self.api_url = 'https://api.ok.ru/fb.do'

    def add_catalog(self, group_id: str, name: str):

        """
        Add new catalog in ok.ru. The output is given the id of the directory
        :param group_id: REQUIRED. Group ID (str)
        :param name: REQUIRED. Catalog name (str)
        :return:
        """

        if not group_id or not name:
            return {'result': 'Error', 'data': '"group_id" or "name" is empty"'}

        return requests.get(self.api_url, params={
            'method': 'market.addCatalog',
            'access_token': self.token_ok_ru,
            'application_key': self.app_key,
            'application_secret_key': self.secret_key,
            'gid': group_id,
            'name': name,
        }).json()

    def edit_catalog(self, group_id: str = None, catalog_id: str = None, name: str = None, photo_id: str = None,
                     admin_restricted: bool = True):

        """
        Edit catalog in ok.ru
        :param group_id: REQUIRED. Group ID (str)
        :param catalog_id: REQUIRED. Catalog ID (str)
        :param name: NOT REQUIRED. Name of the catalog (str)
        :param photo_id: NOT REQUIRED. Photo ID (str)
        :param admin_restricted: NOT REQUIRED. Admin restricted (bool). Flag whether directory modification is limited
        to regular users of the group (not administrators)
        :return:
        """

        if not group_id or not catalog_id:
            return {'result': 'Error', 'data': '"group_id" or "catalog_id" is empty"'}

        catalog = self.get_catalog(group_id, catalog_id)
        old_name = catalog['catalogs'][0].get('name')

        return requests.get(self.api_url, params={
            'method': 'market.editCatalog',
            'access_token': self.token_ok_ru,
            'application_key': self.app_key,
            'application_secret_key': self.secret_key,
            'gid': group_id,
            'catalog_id': catalog_id,
            'name': name if name else old_name,
            'photo_id': photo_id if photo_id else '',
            'admin_restricted': admin_restricted,
        }).json()

    def delete_catalog(self, group_id: str, catalog_id: str, delete_products: bool = False):

        """
        Remove catalog in ok.ru
        :param group_id: REQUIRED. Group ID (str)
        :param catalog_id: REQUIRED. Catalog ID (str)
        :param delete_products: NOT REQUIRED. Delete all products from this catalog (default False)
        :return:
        """

        if not group_id or not catalog_id:
            return {'result': 'Error', 'data': '"group_id" or "name" is empty"'}

        return requests.get(self.api_url, params={
            'method': 'market.deleteCatalog',
            'access_token': self.token_ok_ru,
            'application_key': self.app_key,
            'application_secret_key': self.secret_key,
            'gid': group_id,
            'catalog_id': catalog_id,
            'delete_products': delete_products
        }).json()

    def get_catalog(self, group_id: str = None, catalog_ids: list | str = None, fields: str = '*'):

        """
        Get catalogs in ok.ru
        :param group_id: REQUIRED. Group ID (str)
        :param catalog_ids: REQUIRED. Catalog IDs (list(str) | str)
        :param fields: NOT REQUIRED. Field names (str) default *
        :return:
        """

        if not group_id or not catalog_ids:
            return {'result': 'Error', 'data': '"group_id" or "catalog_ids" is empty"'}

        if isinstance(catalog_ids, str):
            catalog_ids = [catalog_ids]

        return requests.get(self.api_url, params={
            'method': 'market.getCatalogsByIds',
            'access_token': self.token_ok_ru,
            'application_key': self.app_key,
            'application_secret_key': self.secret_key,
            'gid': group_id,
            'catalog_ids': ','.join(catalog_ids),
            'fields': fields
        }).json()

    def add_product(self, group_id: str = None, type_product: str = 'GROUP_PRODUCT', catalog_ids: list = None,
                    product_title: str = None, product_description: str = None, images: list = None, price: int = None,
                    lifetime: int = 30, currency: str = 'RUB'):

        """
        The output is the ad id (product_id)
        :param group_id: REQUIRED. Group ID in ok.ru
        :param type_product: REQUIRED. GROUP_PRODUCT - Just product (default); GROUP_SUGGESTED - product for moderation;
        :param catalog_ids: NOT REQUIRED. The IDs of the catalogs for adding the product
        :param product_title: REQUIRED. Product title
        :param product_description: REQUIRED. Product description
        :param images: NOT REQUIRED. List of id(int) or token(str) images uploaded to the group.
        :param price: REQUIRED. Price of the product
        :param lifetime: REQUIRED. Lifetime of the product in days (default 30 days)
        :param currency: REQUIRED. Currency of the product (default RUB)
        :return:
        """

        if not group_id:
            return {'result': 'Error', 'data': '"group_id" is empty"'}
        elif not type_product:
            return {'result': 'Error', 'data': '"type_product" is empty"'}
        elif not product_title:
            return {'result': 'Error', 'data': '"product_title" is empty"'}
        elif not product_description:
            return {'result': 'Error', 'data': '"product_description" is empty"'}
        elif not price:
            return {'result': 'Error', 'data': '"price" is empty"'}

        title = {'type': 'text', 'text': product_title}
        description = {'type': 'text', 'text': product_description}
        images_ = {'type': 'photo', 'list': []}
        other = {'type': 'product', 'price': price, 'currency': currency, 'lifetime': lifetime}

        if images:
            for image in images:
                if isinstance(image, int):
                    images_['list'].append({'existing_photo_id': image})
                else:
                    images_['list'].append({'id': image})

        return requests.get(self.api_url, params={
            'method': 'market.add',
            'access_token': self.token_ok_ru,
            'application_key': self.app_key,
            'application_secret_key': self.secret_key,
            'gid': group_id,
            'type': type_product,
            'attachment': json.dumps({"media": [title, description, images_, other]}),
            'catalog_ids': ','.join(catalog_ids) if catalog_ids else ""
        }).json()

    def edit_product(self, product_id: str = None, catalog_ids: list = None, product_title: str = None,
                     product_description: str = None, images: list = None, price: int = None, lifetime: int = None,
                     currency: str = None):

        """
        The output is the ad id (product_id)
        :param product_id: REQUIRED. Product ID
        :param catalog_ids: NOT REQUIRED. The IDs of the catalogs for adding the product
        :param product_title: NOT REQUIRED. Product title. The past value will be accepted if it was
        :param product_description: NOT REQUIRED. Product description. The past value will be accepted if it was
        :param images: NOT REQUIRED. List of id(int) or token(str) images uploaded to the group. The past value will be accepted if it was
        :param price: NOT REQUIRED. Price of the product. The past value will be accepted if it was
        :param lifetime: NOT REQUIRED. Lifetime of the product in days (default 30 days). The past value will be accepted if it was
        :param currency: NOT REQUIRED. Currency of the product (default RUB). The past value will be accepted if it was
        :return:
        """

        if not product_id:
            return {'result': 'Error', 'data': '"product_id" is empty"'}

        data = self.get_product(product_id)
        old_price = data['products'][0]['media'][0].get('product_price_number')
        old_title = data['products'][0]['media'][0].get('product_title')
        old_currency = data['products'][0]['media'][0].get('product_ccy')
        old_lifetime = data['products'][0]['media'][0].get('product_lifetime')
        old_description = data['products'][0]['media'][1].get('text')
        old_photo = data['products'][0]['media'][2].get('photo_refs')

        title = {'type': 'text', 'text': product_title if product_title else old_title}
        description = {'type': 'text', 'text': product_description if product_description else old_description}
        images_ = {'type': 'photo', 'list': []}
        other = {
            'type': 'product',
            'price': price if price else int(old_price),
            'currency': currency if currency else old_currency,
            'lifetime': lifetime if lifetime else old_lifetime}

        if images:
            for image in images:
                if isinstance(image, int):
                    images_['list'].append({'existing_photo_id': image})
                else:
                    images_['list'].append({'id': image})
        else:
            images_['list'] = [{'existing_photo_id': item.split(':')[1], 'group': True} for item in old_photo]

        return requests.get(self.api_url, params={
            'method': 'market.edit',
            'access_token': self.token_ok_ru,
            'application_key': self.app_key,
            'application_secret_key': self.secret_key,
            'product_id': product_id,
            'attachment': json.dumps({"media": [title, description, images_, other]}),
            'catalog_ids': ','.join(catalog_ids) if catalog_ids else ""
        }).json()

    def get_product(self, product_id: str | list, fields: str = '*'):

        """
        Get products by ids
        :param product_id: REQUIRED. Products ID (str|list)
        :param fields: NOT REQUIRED. Fields (str) (default *)
        :return:
        """

        if not product_id:
            return {'result': 'Error', 'data': '"product_id" is empty"'}

        if isinstance(product_id, str):
            product_id = [product_id]

        return requests.get(self.api_url, params={
            'method': 'market.getByIds',
            'access_token': self.token_ok_ru,
            'application_key': self.app_key,
            'application_secret_key': self.secret_key,
            'product_ids': ','.join(product_id),
            'fields': fields
        }).json()

    def delete_product(self, product_id: str):

        """
        Remove product in ok.ru
        :param product_id: REQUIRED. Product ID (str)
        :return:
        """

        if not product_id:
            return {'result': 'Error', 'data': '"product_id" is empty"'}

        return requests.get(self.api_url, params={
            'method': 'market.delete',
            'access_token': self.token_ok_ru,
            'application_key': self.app_key,
            'application_secret_key': self.secret_key,
            'product_id': product_id,
        }).json()

    def pin_product(self, catalog_id: str = None, product_id: str = None, on: bool = True):

        """
        Pin an item to the top of the list / unpin an item
        :param catalog_id: REQUIRED. Catalog ID (str)
        :param product_id: REQUIRED. Product ID (str)
        :param on: NOT REQUIRED. Pin an item to the top of the list (true) / unpin an item (false)
        :return:
        """

        if not product_id:
            return {'result': 'Error', 'data': '"product_id" is empty"'}
        elif not catalog_id:
            return {'result': 'Error', 'data': '"catalog_id" is empty"'}

        return requests.get(self.api_url, params={
            'method': 'market.pin',
            'access_token': self.token_ok_ru,
            'application_key': self.app_key,
            'application_secret_key': self.secret_key,
            'catalog_id': catalog_id if catalog_id else '',
            'product_id': product_id,
            'on': on
        }).json()

    def reorder_product(self, gid: str = None, catalog_id: str = None, product_id: str = None,
                        after_product_id: str = None):

        """
        Move an item inside the catalog
        :param gid: NOT REQUIRED. Group ID (str)
        :param catalog_id: REQUIRED. Catalog ID (str)
        :param product_id: REQUIRED. Product ID (str)
        :param after_product_id: REQUIRED. The product ID after which to insert the previous product (str)
        :return:
        """

        if not catalog_id:
            return {'result': 'Error', 'data': '"catalog_id" is empty"'}
        elif not product_id:
            return {'result': 'Error', 'data': '"product_id" is empty"'}
        elif not after_product_id:
            return {'result': 'Error', 'data': '"after_product_id" is empty"'}

        return requests.get(self.api_url, params={
            'method': 'market.reorder',
            'access_token': self.token_ok_ru,
            'application_key': self.app_key,
            'application_secret_key': self.secret_key,
            'gid': gid,
            'catalog_id': catalog_id if catalog_id else '',
            'product_id': product_id,
            'after_product_id': after_product_id
        }).json()

    def reorder_catalog(self, gid: str = None, catalog_id: str = None, after_catalog_id: str = None):

        """
        Move an item inside the catalog
        :param gid: REQUIRED. Group ID (str)
        :param catalog_id: REQUIRED. Catalog ID (str)
        :param after_catalog_id: REQUIRED. The catalog ID after which to insert the previous product (str)
        :return:
        """

        if not catalog_id:
            return {'result': 'Error', 'data': '"catalog_id" is empty"'}
        elif not gid:
            return {'result': 'Error', 'data': '"gid" is empty"'}
        elif not after_catalog_id:
            return {'result': 'Error', 'data': '"after_catalog_id" is empty"'}

        return requests.get(self.api_url, params={
            'method': 'market.reorderCatalogs',
            'access_token': self.token_ok_ru,
            'application_key': self.app_key,
            'application_secret_key': self.secret_key,
            'gid': gid,
            'catalog_id': catalog_id,
            'after_catalog_id': after_catalog_id
        }).json()

    def set_status_product(self, product_id: str = None, product_status: str = 'ACTIVE'):

        """
        Set the product status
        :param product_id: REQUIRED. Product ID (str)
        :param product_status: REQUIRED. Product status (str) [ACTIVE, CLOSED, SOLD, OUT_OF_STOCK] (default: 'ACTIVE')
        :return:
        """

        if not product_id:
            return {'result': 'Error', 'data': '"product_id" is empty"'}
        elif not product_status:
            return {'result': 'Error', 'data': '"product_status" is empty"'}

        return requests.get(self.api_url, params={
            'method': 'market.setStatus',
            'access_token': self.token_ok_ru,
            'application_key': self.app_key,
            'application_secret_key': self.secret_key,
            'product_id': product_id,
            'product_status': product_status,
        }).json()

    def update_product_catalogs(self, gid: str = None, product_id: str = None, catalog_ids: list | str = None):

        """
        Set the list of catalogs in which the product will consist
        :param gid: REQUIRED. Group ID (str)
        :param product_id: REQUIRED. Product ID (str)
        :param catalog_ids: REQUIRED. Catalog IDs (list(str))
        :return:
        """

        if not gid:
            return {'result': 'Error', 'data': '"gid" is empty"'}
        elif not product_id:
            return {'result': 'Error', 'data': '"product_id" is empty"'}
        elif not catalog_ids:
            return {'result': 'Error', 'data': '"catalog_ids" is empty"'}

        if isinstance(catalog_ids, str):
            catalog_ids = [catalog_ids]

        return requests.get(self.api_url, params={
            'method': 'market.updateCatalogsList',
            'access_token': self.token_ok_ru,
            'application_key': self.app_key,
            'application_secret_key': self.secret_key,
            'gid': gid,
            'product_id': product_id,
            'catalog_ids': ','.join(catalog_ids),
        }).json()

    def upload_image(self, path_file: Path | list):

        """
        The output shows the download success, the technical ID (photo_id) and the general ID (existing_photo_id)
        :param path_file: REQUIRED. The expected path to the file (Path) or a list of paths [Path, Path]
        :return:
        """

        if not path_file:
            return {'result': 'Error', 'data': '"path_file" is empty"'}

        files, result = {}, []
        if isinstance(path_file, Path):
            count = 1
            files[Path(path_file).name] = open(Path(path_file), 'rb')
        else:
            count = len(path_file)
            for file in path_file:
                files[Path(file).name] = open(Path(file), 'rb')

        response = requests.post(self.api_url, params={
            'method': 'photosV2.getUploadUrl',
            'access_token': self.token_ok_ru,
            'application_key': self.app_key,
            'application_secret_key': self.secret_key,
            'count': str(count)
        }).json()

        photo_ids = response['photo_ids']
        upload_url = response['upload_url']

        response_get_ids = requests.post(upload_url, files=files).json()

        for photo_id in photo_ids:
            token = response_get_ids['photos'][photo_id].get('token')
            response = requests.post(self.api_url, params={
                'method': 'photosV2.commit',
                'access_token': self.token_ok_ru,
                'application_key': self.app_key,
                'application_secret_key': self.secret_key,
                'photo_id': photo_id,
                'token': token
            }).json()

            result.append(response['photos'][0])
            logger.info(f'Result: {response["photos"][0]}')

        return result

    def close(self):
        self.token_ok_ru = ''
        self.app_key = ''
        self.secret_key = ''


def add_vk_api(): # NOT USE NOW!
    vk_session = vk_api.VkApi(token=os.getenv('TOKEN'))
    response = vk_session.method(
        'wall.post',
        {
            'message': 'HELLO',
            'owner_id': f'{os.getenv("GROUP_ID")}',
            'from_group': '1',
            'v': f'{os.getenv("API_VERSION")}'
        })

    # print(response)


def add_ok_api():
    # ok_session = ApiOk(token=os.getenv("TOKEN_OK"), app_key=os.getenv("PUBLIC_KEY"), secret_key=os.getenv("SECRET_KEY"))

    # print(ApiOk().update_product_catalogs(os.getenv("GROUP_ID_OK"), '157108075031495', ['157108272032711', '157107714059207']))
    # print(ApiOk().set_status_product('157108288285639', 'ACTIVE'))
    # print(ApiOk().reorder_catalog(os.getenv("GROUP_ID_OK"), '157108272032711', '157107714059207'))
    # print(ApiOk().reorder_product(catalog_id='157107714059207', product_id='157108288023495', after_product_id='157108288285639'))
    # print(ApiOk().add_catalog(os.getenv("GROUP_ID_OK"), 'Exxxaaample123'))
    # print(ok_session.add_product(
    #     group_id=os.getenv("GROUP_ID_OK"),
    #     catalog_ids=['157107714059207'],
    #     product_title='Product titleqweqwe',
    #     product_description='d' * 1000,
    #     price=10000,
    #     images=[961015062471, 961015062983]
    # ))
    # print(ApiOk().get_product(['157108075031495', '157108013820871']))
    # print(ApiOk().upload_image([Path(r'D:\Desktop\example\WSM00000005195446_orig_03.jpg'), Path(r'D:\Desktop\example\WSM00000005195446_orig_04.jpg')]))
    # print(ApiOk().delete_product('157107813280711'))
    # print(ApiOk().delete_catalog(group_id=os.getenv('GROUP_ID_OK'), catalog_id='157108272229319', delete_products=False))
    # print(ApiOk().edit_product(
    #     product_id='157108075031495',
    #     price=18000
    # ))
    # print(ApiOk().edit_catalog(os.getenv('GROUP_ID_OK'), '157107714059207', 'New super name'))
    # print(ApiOk().pin_product('157107714059207', '157108288023495', False))
    # ok_session.close()
    pass


if __name__ == '__main__':
    # add_vk_api()
    add_ok_api()

    # WORK_URL!!! = 'https://oauth.vk.com/authorize?client_id=51985608&redirect_url=https://api.vk.com/blank.html&scope=offline,wall&response_type=token'
    # WORK_URL!!! = 'https://oauth.vk.com/authorize?client_id=51985053&redirect_url=https://api.vk.com/blank.html&scope=offline,wall&response_type=token'
