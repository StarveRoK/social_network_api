import json
import os
from functools import lru_cache
from pathlib import Path

from loguru import logger
import dotenv
import requests
from pydantic import AliasChoices, Field, BaseModel
from requests_toolbelt.sessions import BaseUrlSession

dotenv.load_dotenv()


class Credentials(BaseModel):
    application_key: str = Field(..., validation_alias=AliasChoices('PUBLIC_KEY'))
    application_secret_key: str = Field(..., validation_alias=AliasChoices('SECRET_KEY'))
    access_token: str = Field(..., validation_alias=AliasChoices('TOKEN_OK'))
    group_id: str = Field(..., validation_alias=AliasChoices('GROUP_ID'))

    def __init__(self):
        dotenv.load_dotenv()
        super().__init__(**dotenv.dotenv_values())

    @property
    def params(self):
        return self.model_dump(exclude={'group_id'})


class OkSession(BaseUrlSession):
    def __init__(self):
        super().__init__('https://api.ok.ru/fb.do')
        self._credentials = Credentials()

    def request(self, method, url, **kwargs):
        kwargs['params'] = kwargs.get('params', {}) | self._credentials.params
        return super().request(method, url, **kwargs)


@lru_cache
def ok_session():
    return OkSession()


class ApiOk:

    # def __init__(self, token, app_key, secret_key):
    #
    #     """
    #     StarveR api to connect ok.ru
    #     :param token: Permanent or temporary application token
    #     :param app_key: The public key of the application
    #     :param secret_key: Secret key of the application
    #     """

    # self.params = {
    #     'token': token,
    #     'app_key': app_key,
    #     'secret_key': secret_key,
    # }

    # self.token_ok_ru = token
    # self.app_key = app_key
    # self.secret_key = secret_key
    # self.api_url = 'https://api.ok.ru/fb.do'

    # def close(self):
    #     self.params = {}

    class Market:

        def add_catalog(self, group_id: str, name: str):

            """
            Add new catalog in ok.ru. The output is given the id of the directory
            :param group_id: REQUIRED. Group ID (str)
            :param name: REQUIRED. Catalog name (str)
            :return:
            """

            if not group_id or not name:
                return {'result': 'Error', 'data': '"group_id" or "name" is empty"'}

            return ok_session().post(
                '',
                params={
                    'method': 'market.addCatalog',
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
            :param admin_restricted: NOT REQUIRED. Admin restricted (bool). Flag whether directory modification is
                limited
            to regular users of the group (not administrators)
            :return:
            """

            if not group_id or not catalog_id:
                return {'result': 'Error', 'data': '"group_id" or "catalog_id" is empty"'}

            catalog: dict[str, list[dict[str, str]]] = self.get_catalog(group_id, catalog_id)
            old_name = catalog['catalogs'][0].get('name')

            return ok_session().post(
                '',
                params={
                    'method': 'market.editCatalog',
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

            return ok_session().post(
                '',
                params={
                    'method': 'market.deleteCatalog',
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

            return ok_session().post(
                '',
                params={
                    'method': 'market.getCatalogsByIds',
                    'gid': group_id,
                    'catalog_ids': ','.join(catalog_ids),
                    'fields': fields
                }).json()

        def add_product(self, group_id: str = None, type_product: str = 'GROUP_PRODUCT', catalog_ids: list = None,
                        product_title: str = None, product_description: str = None, images: list = None,
                        price: int = None,
                        lifetime: int = 30, currency: str = 'RUB'):

            """
            The output is the ad id (product_id)
            :param group_id: REQUIRED. Group ID in ok.ru
            :param type_product: REQUIRED. GROUP_PRODUCT - Just product (default); GROUP_SUGGESTED - product for
                moderation;
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

            return ok_session().post(
                '',
                params={
                    'method': 'market.add',
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
            :param images: NOT REQUIRED. List of id(int) or token(str) images uploaded to the group. The past value will
                be accepted if it was
            :param price: NOT REQUIRED. Price of the product. The past value will be accepted if it was
            :param lifetime: NOT REQUIRED. Lifetime of the product in days (default 30 days). The past value will be
                accepted if it was
            :param currency: NOT REQUIRED. Currency of the product (default RUB). The past value will be accepted if it
                was
            :return:
            """

            if not product_id:
                return {'result': 'Error', 'data': '"product_id" is empty"'}

            data: dict[str, list[dict[str, list]]] = self.get_product(product_id)
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

            return ok_session().post(
                '',
                params={
                    'method': 'market.edit',
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

            return ok_session().post(
                '',
                params={
                    'method': 'market.getByIds',
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

            return ok_session().post(
                '',
                params={
                    'method': 'market.delete',
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

            return ok_session().post(
                '',
                params={
                    'method': 'market.pin',
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

            return ok_session().post(
                '',
                params={
                    'method': 'market.reorder',
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

            return ok_session().post(
                '',
                params={
                    'method': 'market.reorderCatalogs',
                    'gid': gid,
                    'catalog_id': catalog_id,
                    'after_catalog_id': after_catalog_id
                }).json()

        def set_status_product(self, product_id: str = None, product_status: str = 'ACTIVE'):

            """
            Set the product status
            :param product_id: REQUIRED. Product ID (str)
            :param product_status: REQUIRED. Product status (str) [ACTIVE, CLOSED, SOLD, OUT_OF_STOCK] (default:
                'ACTIVE')
            :return:
            """

            if not product_id:
                return {'result': 'Error', 'data': '"product_id" is empty"'}
            elif not product_status:
                return {'result': 'Error', 'data': '"product_status" is empty"'}

            return ok_session().post(
                '',
                params={
                    'method': 'market.setStatus',
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

            return ok_session().post(
                '',
                params={
                    'method': 'market.updateCatalogsList',
                    'gid': gid,
                    'product_id': product_id,
                    'catalog_ids': ','.join(catalog_ids),
                }).json()

    class Group:

        def get_counters(self, group_id: str = None, counter_types: list | str = None):

            """
            Returns the main counters of group objects - the number of group members, photos, photo albums, etc.
            :param group_id: REQUIRED. Group ID (str)
            :param counter_types: REQUIRED. Counter types (str | list) (default "*") [ADS_TOPICS, BLACK_LIST, CATALOGS,
                DELAYED_TOPICS, FRIENDS, JOIN_REQUESTS, LINKS, MAYBE, MEMBERS, MODERATORS, MUSIC_TRACKS,
                NEW_PAID_TOPICS, OWN_PRODUCTS, PAID_MEMBERS, PAID_TOPICS, PHOTOS, PHOTO_ALBUMS, PINNED_TOPICS, PRESENTS,
                PRODUCTS, PROMO_TOPICS_ON_MODERATION, SUGGESTED_PRODUCTS, SUGGESTED_TOPICS, THEMES, UNPUBLISHED_TOPICS,
                VIDEOS]
            :return:
            """

            if group_id is None:
                return {'result': 'Error', 'data': '"group_id" is empty"'}
            elif counter_types is None:
                return {'result': 'Error', 'data': '"counter_types" is empty"'}

            if isinstance(counter_types, str):
                counter_types = [counter_types]

            return ok_session().post(
                '',
                params={
                    'method': 'group.getCounters',
                    'group_id': group_id,
                    'counterTypes': ','.join(counter_types),
                }).json()

        def get_info(self, group_ids: str | list = None, counter_types: list | str = None):

            """
            Getting information about groups.
            :param group_ids: REQUIRED. Group ID (str | list)
            :param counter_types: REQUIRED. Counter types (str | list) (default "*") [ABBREVIATION, ACCESS_TYPE,
                ADDRESS, ADD_CHANNEL_ALLOWED, ADD_PAID_THEME_ALLOWED, ADD_PHOTOALBUM_ALLOWED, ADD_THEME_ALLOWED,
                ADD_VIDEO_ALLOWED, ADMIN_ID, ADS_MANAGER_ALLOWED, ADVANCED_PUBLICATION_ALLOWED, AGE_RESTRICTED, BLOCKED,
                BOOKMARKED, BUSINESS, CALL_ALLOWED, CAN_MANAGE_VIDEO_REVENUE, CATALOG_CREATE_ALLOWED, CATEGORY,
                CHANGE_AVATAR_ALLOWED, CHANGE_TYPE_ALLOWED, CITY, COMMENT_AS_OFFICIAL, COMMUNITY, CONTENT_AS_OFFICIAL,
                COUNTRY, COVER, COVER_BUTTONS, COVER_SERIES, CREATED_MS, CREATE_ADS_ALLOWED, DAILY_PHOTO_POST_ALLOWED,
                DELETE_ALLOWED, DESCRIPTION, DISABLE_PHOTO_UPLOAD, DISABLE_REASON, EDIT_ALLOWED, EDIT_APPS_ALLOWED,
                END_DATE, FEED_SUBSCRIPTION, FOLLOWERS_COUNT, FOLLOW_ALLOWED, FRIENDS, FRIENDS_COUNT, GOS_ORG,
                GRADUATE_YEAR, GROUP_AGREEMENT, GROUP_CHALLENGE_CREATE_ALLOWED, GROUP_JOURNAL_ALLOWED, GROUP_NEWS,
                HAS_DAILY_PHOTO, HAS_GROUP_AGREEMENT, HOBBY_EXPERT, HOBBY_TOPIC, HOMEPAGE_NAME, HOMEPAGE_URL,
                INVITATIONS_COUNT, INVITATION_SENT, INVITE_ALLOWED, INVITE_FREE_ALLOWED, JOIN_ALLOWED,
                JOIN_REQUESTS_COUNT, LEAVE_ALLOWED, LINK_CAROUSEL_ALLOWED, LINK_POSTING_ALLOWED, LOCATION_ID,
                LOCATION_LATITUDE, LOCATION_LONGITUDE, LOCATION_ZOOM, MAIN_PAGE_TAB, MAIN_PHOTO, MANAGE_MEMBERS,
                MANAGE_MESSAGING_ALLOWED, MEMBERS_COUNT, MEMBER_STATUS, MENTIONS_SUBSCRIPTION,
                MENTIONS_SUBSCRIPTION_ALLOWED, MESSAGES_ALLOWED, MESSAGING_ALLOWED, MESSAGING_ENABLED, MIN_AGE,
                MOBILE_COVER, NAME, NEW_ADVERTS_ALLOWED, NEW_CHATS_COUNT, NOTIFICATIONS_SUBSCRIPTION,
                ONLINE_PAYMENT_ALLOWED, PAID_ACCESS, PAID_ACCESS_DESCRIPTION, PAID_ACCESS_PRICE,
                PAID_CONTENT, PAID_CONTENT_DESCRIPTION, PAID_CONTENT_PRICE, PARTNER_LINK_CREATE_ALLOWED,
                PARTNER_PROGRAM_ALLOWED, PARTNER_PROGRAM_STATUS, PENALTY_POINTS_ALLOWED, PHONE, PHOTOS_TAB_HIDDEN,
                PHOTO_ID, PIC_AVATAR, PIN_NOTIFICATIONS_OFF, POSSIBLE_MEMBERS_COUNT, PREMIUM, PRIVATE,
                PRODUCTS_TAB_HIDDEN, PRODUCT_CREATE_ALLOWED, PRODUCT_CREATE_SUGGESTED_ALLOWED,
                PRODUCT_CREATE_ZERO_LIFETIME_ALLOWED, PROFILE_BUTTONS, PROMO_THEME_ALLOWED,
                PUBLISH_DELAYED_THEME_ALLOWED, REF, REQUEST_SENT, REQUEST_SENT_DATE, SHOP_VISIBLE_PUBLIC,
                RESHARE_ALLOWED, REVENUE_PARTNER_PROGRAM_ENABLED, ROLE, SCOPE_ID, SHOP_VISIBLE_ADMIN,
                SHORTNAME, START_DATE, STATS_ALLOWED, STATUS, SUBCATEGORY, SUBCATEGORY_ID, SUGGEST_THEME_ALLOWED, TAGS,
                TRANSFERS_ALLOWED, UID, UNFOLLOW_ALLOWED, USER_PAID_ACCESS, USER_PAID_ACCESS_TILL, USER_PAID_CONTENT,
                USER_PAID_CONTENT_TILL, VIDEO_TAB_HIDDEN, VIEW_MEMBERS_ALLOWED, VIEW_MODERATORS_ALLOWED,
                VIEW_PAID_THEMES_ALLOWED, WHO_CAN_COMMENT, YEAR_FROM, YEAR_TO]
            :return:
            """

            if group_ids is None:
                return {'result': 'Error', 'data': '"group_id" is empty"'}
            elif counter_types is None:
                return {'result': 'Error', 'data': '"counter_types" is empty"'}

            if isinstance(counter_types, str):
                counter_types = [counter_types]

            if isinstance(group_ids, str):
                group_ids = [group_ids]

            return ok_session().post(
                '',
                params={
                    'method': 'group.getInfo',
                    'uids': ','.join(group_ids),
                    'fields': ','.join(counter_types),
                }).json()

        def get_members(self, group_id: str = None, statuses: list | str = None, count: int = None):

            """
            Getting a list of the group's users. To get all the group members in the order of entry, it is necessary to
            list all statuses (ADMIN, MODERATOR, ACTIVE) as the status's argument. If you pass an empty value, the users
            will return in ascending order of the id.
            :param group_id: REQUIRED. Group ID (str)
            :param statuses: NOT REQUIRED. Statuses (list | str) default ALL [ACTIVE, ADMIN, BLOCKED, FOLLOWER, MAYBE,
                MODERATOR, PASSIVE]
            :param count: NOT REQUIRED. Count of members (int) default ALL
            :return:
            """

            if group_id is None:
                return {'result': 'Error', 'data': '"group_id" is empty"'}

            if isinstance(statuses, str):
                statuses = [statuses]

            return ok_session().post(
                '',
                params={
                    'method': 'group.getMembers',
                    'uid': group_id,
                    'statuses': ','.join(statuses) if statuses else '',
                    'count': count,
                }).json()

        def get_stat_overview(self, group_id: str = None, fields: list | str = None, period: int = None):

            """
            Gets the main statistics counters of the groups
            :param group_id: REQUIRED. GROUP ID (str)
            :param fields: REQUIRED. List of requested fields (list | str) [ACTIVE_USER_SHARE, END_TIME_MS,
                ENGAGEMENT, ENGAGEMENT_PREV, ENGAGEMENT_RATE, ENGAGEMENT_RATE_PREV, FEEDBACK, FEEDBACK_PREV, MONTHS_MS,
                REACH, REACH_PREV, START_TIME_MS]
            :param period: NOT REQUIRED. It may be empty - in this case, the statistics for the week are returned (days)
            :return:
            """

            if group_id is None:
                return {'result': 'Error', 'data': '"group_id" is empty"'}
            elif fields is None:
                return {'result': 'Error', 'data': '"fields" is empty"'}

            if isinstance(fields, str):
                fields = [fields]

            return ok_session().post(
                '',
                params={
                    'method': 'group.getStatOverview',
                    'gid': group_id,
                    'fields': ','.join(fields),
                    'period': period,
                }).json()

        def get_stat_people(self, group_id: str = None, fields: list | str = None, demo_type: list | str = None):

            """
            A method for obtaining statistics on the group's audience: demographics by gender and age, geography by
            country and city, etc.

            The data in the statistics is returned for the last 7 days. Except the demographics by
            participants, it is among all group members (BUT the demographics by coverage and users who gave feedback
            are for the last 7 days).
            :param group_id: REQUIRED. GROUP ID (str)
            :param fields: REQUIRED. List of requested fields (list | str) [CITIES,  COUNTRIES, DEMOGRAPHY_FEMALE,
                DEMOGRAPHY_MALE, REFERENCES]
            :param demo_type: NOT REQUIRED. It can be empty - in this case, the demographics of the group members are
                returned [FEEDBACK, MEMBERS, REACH] (list | str)
            :return:
            """

            if group_id is None:
                return {'result': 'Error', 'data': '"group_id" is empty"'}
            elif fields is None:
                return {'result': 'Error', 'data': '"fields" is empty"'}

            if isinstance(fields, str):
                fields = [fields]
            if isinstance(demo_type, str) and demo_type:
                demo_type = [demo_type]

            return ok_session().post(
                '',
                params={
                    'method': 'group.getStatPeople',
                    'gid': group_id,
                    'demo_type': ','.join(demo_type) if demo_type else '',
                    'fields': ','.join(fields),
                }).json()

        def get_stat_topic(self, topic_id: str = None, fields: list | str = "*"):

            """
            A method for getting statistics on a topic using its identifier
            :param topic_id: REQUIRED. Topic ID (str)
            :param fields: NOT REQUIRED. List of requested fields (list | str) [COMMENTS, COMPLAINTS, CONTENT_OPENS,
                CREATED_MS, ENGAGEMENT, EXTERNAL_ID, FEEDBACK, FEEDBACK_TOTAL, HIDES_FROM_FEED, ID, LIKES, LINK_CLICKS,
                MUSIC_PLAYS, NEGATIVES, PROMO_FROM, PROMO_TO, REACH, REACH_EARNED, REACH_OWN, RENDERINGS,
                RENDERINGS_EARNED, RENDERINGS_OWN, RESHARES, VIDEO_PLAYS, VIEWS] default "*"
            :return:
            """

            if topic_id is None:
                return {'result': 'Error', 'data': '"topic_id" is empty"'}

            if isinstance(fields, str):
                fields = [fields]

            return ok_session().post(
                '',
                params={
                    'method': 'group.getStatTopic',
                    'topic_id': topic_id,
                    'fields': ','.join(fields),
                }).json()

        def get_stat_topics(self, group_id: str = None, fields: list | str = "*", count: int = None, start: int = None,
                            end: int = None):

            """
            A method for obtaining statistics on topics. Returns a list of topics from the group for the selected range
            with statistics.
            :param group_id: REQUIRED. GROUP ID (str)
            :param fields: NOT REQUIRED. List of requested fields (list | str) [COMMENTS, COMPLAINTS, CONTENT_OPENS,
                CREATED_MS, ENGAGEMENT, EXTERNAL_ID, FEEDBACK, FEEDBACK_TOTAL, HIDES_FROM_FEED, ID, LIKES, LINK_CLICKS,
                MUSIC_PLAYS, NEGATIVES, PROMO_FROM, PROMO_TO, REACH, REACH_EARNED, REACH_OWN, RENDERINGS,
                RENDERINGS_EARNED, RENDERINGS_OWN, RESHARES, VIDEO_PLAYS, VIEWS] default "*"
            :param count: NOT REQUIRED. The number of results returned (int)
            :param start: NOT REQUIRED. The time in milliseconds of the beginning of the period for which you need to
                get topics. It may be empty - data is returned from the very beginning of collecting statistics for
                this group.
            :param end: NOT REQUIRED. The time in milliseconds of the end of the period for which you need to get
                topics. It can be empty - data is returned up to and including the current date.
            :return:
            """

            if group_id is None:
                return {'result': 'Error', 'data': '"group_id" is empty"'}

            if isinstance(fields, str):
                fields = [fields]

            return ok_session().post(
                '',
                params={
                    'method': 'group.getStatTopics',
                    'gid': group_id,
                    'fields': ','.join(fields),
                    'start_time': start,
                    'end_time': end,
                    'count': count
                }).json()

        def get_stat_trends(self, group_id: str = None, fields: list | str = "*", start: int = None, end: int = None):

            """
            Gets the history of statistics counters by day
            :param group_id: REQUIRED. ID of the group to get statistics for (str)
            :param fields: NOT REQUIRED. List of requested fields (list | str) [COMMENTS, COMPLAINTS, CONTENT_OPENS,
                ENGAGEMENT, FEEDBACK, HIDES_FROM_FEED, LEFT_MEMBERS, LIKES, LINK_CLICKS, MEMBERS_COUNT, MEMBERS_DIFF,
                MUSIC_PLAYS, NEGATIVES, NEW_MEMBERS, NEW_MEMBERS_TARGET, PAGE_VISITS, PHOTO_OPENS, REACH, REACH_EARNED,
                REACH_MOB, REACH_MOBWEB, REACH_OWN, REACH_WEB, RENDERINGS, RESHARES, TOPIC_OPENS, VIDEO_PLAYS, VOTES]
                default "*"
            :param start: NOT REQUIRED. The time in milliseconds of the beginning of the period for which you need to
                get topics. It may be empty - data is returned from the very beginning of collecting statistics for
                this group.
            :param end: NOT REQUIRED. The time in milliseconds of the end of the period for which you need to get
                topics. It can be empty - data is returned up to and including the current date.
            :return:
            """

            if group_id is None:
                return {'result': 'Error', 'data': '"group_id" is empty"'}

            if isinstance(fields, str):
                fields = [fields]

            return ok_session().post(
                '',
                params={
                    'method': 'group.getStatTrends',
                    'gid': group_id,
                    'fields': ','.join(fields),
                    'start_time': start,
                    'end_time': end,
                }).json()

        def get_user_groups_by_ids(self, group_id: str = None, user_ids: list | str = None):

            """
            Getting information about users belonging to a specific group
            :param group_id: REQUIRED. GROUP ID (str)
            :param user_ids: REQUIRED. A comma-separated list of user IDs whose group membership needs to be verified.
                The maximum number of IDs per request is 100.
            :return:
            """

            if group_id is None:
                return {'result': 'Error', 'data': '"group_id" is empty"'}
            if user_ids is None:
                return {'result': 'Error', 'data': '"user_ids" is empty"'}

            if isinstance(user_ids, str):
                user_ids = [user_ids]

            return ok_session().post(
                '',
                params={
                    'method': 'group.getUserGroupsByIds',
                    'group_id': group_id,
                    'uids': ','.join(user_ids),
                }).json()

        def is_messages_allowed(self, group_id: str = None):

            """
            Is message allowed in group
            :param group_id: REQUIRED. GROUP ID (str)
            """

            if group_id is None:
                return {'result': 'Error', 'data': '"group_id" is empty"'}

            return ok_session().post(
                '',
                params={
                    'method': 'group.isMessagesAllowed',
                    'gid': group_id,
                }).json()

        def pin_group_feed(self, pin_id: str = None):

            """
            The operation of attributing or sawing off an event in a group feed
            :param pin_id: REQUIRED. PIN ID (str) The pin ID that can be obtained in the event
            """

            if pin_id is None:
                return {'result': 'Error', 'data': '"pin_id" is empty"'}

            return ok_session().post(
                '',
                params={
                    'method': 'group.pinGroupFeed',
                    'pin_id': pin_id,
                }).json()

        def set_group_image(self, group_id: str = None, image_id: str = None):

            """
            Setting an image group
            :param group_id: REQUIRED. GROUP ID (str)
            :param image_id: REQUIRED. Image ID (str)
            :return:
            """

            if group_id is None:
                return {'result': 'Error', 'data': '"group_id" is empty"'}
            elif image_id is None:
                return {'result': 'Error', 'data': '"image_id" is empty"'}

            return ok_session().post(
                '',
                params={
                    'method': 'group.setMainPhoto',
                    'group_id': group_id,
                    'photo_id': image_id,
                }).json()

        def get_members_from_communities(self, group_id: str = None, start_year: int = 2000, end_year: int = None):

            """
            Getting a list of community members
            :param group_id: REQUIRED. GROUP ID (str)
            :param start_year: NOT REQUIRED. The year of joining the community (int) default 2000
            :param end_year: REQUIRED. The year of leaving the community (int)
            :return:
            """

            if group_id is None:
                return {'result': 'Error', 'data': '"group_id" is empty"'}
            elif end_year is None:
                return {'result': 'Error', 'data': '"end_year" is empty"'}

            return ok_session().post(
                '',
                params={
                    'method': 'communities.getMembers',
                    'group_id': group_id,
                    'start_year': start_year,
                    'end_year': end_year,
                }).json()

    class Images:

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

            response = ok_session().post(
                '', params={
                    'method': 'photosV2.getUploadUrl',
                    'count': str(count)
                }).json()

            photo_ids = response['photo_ids']
            upload_url = response['upload_url']

            response_get_ids = requests.post(upload_url, files=files).json()

            for photo_id in photo_ids:
                token = response_get_ids['photos'][photo_id].get('token')
                response = ok_session().post(
                    '', params={
                        'method': 'photosV2.commit',
                        'photo_id': photo_id,
                        'token': token
                    }).json()

                result.append(response['photos'][0])
                logger.info(f'Result: {response["photos"][0]}')

            return result

        def create_album(self, user_id: str = None, group_id: str = None, title: str = None, description: str = None,
                         type_album: str | list = None):

            """
            Creates a photo album for the specified user or group
            :param user_id: REQUIRED if group_id is None. User ID (str)
            :param group_id: REQUIRED if user_id is None. User ID (str)
            :param title: REQUIRED. Album title (str)
            :param description: NOT REQUIRED. If user_id is not None. Album description (str)
            :param type_album: NOT REQUIRED. If user_id is not None. Album type (list or str) [CLASSMATE, CLOSE_FRIEND,
                COLLEAGUE, COMPANION_IN_ARMS, CURSEMATE, FRIENDS, LOVE, PRIVATE, PUBLIC, RELATIVE, SHARED] default None
            :return:
            """

            if group_id is None and user_id is None:
                return {'result': 'Error', 'data': '"group_id" or "user_id" is empty"'}
            elif title is None:
                return {'result': 'Error', 'data': '"title" is empty"'}

            if isinstance(type_album, str):
                type_album = [type_album]

            return ok_session().post(
                '',
                params={
                    'method': 'photos.createAlbum',
                    'gid': group_id,
                    'uid': user_id,
                    'title': title,
                    'description': description,
                    'type': type_album if type_album else '',
                }).json()

        def delete_album(self, album_id: str = None, group_id: str = None):

            """
            Deletes a photo album
            :param album_id: REQUIRED. Album ID (str)
            :param group_id: NOT REQUIRED. If album in group. Group ID (str)
            :return:
            """

            if album_id is None:
                return {'result': 'Error', 'data': '"album_id" is empty"'}

            return ok_session().post(
                '',
                params={
                    'method': 'photos.deleteAlbum',
                    'gid': group_id,
                    'aid': album_id,
                }).json()

        def delete_images(self, image_id: str = None, group_id: str = None):

            """
            Deletes a photo
            :param image_id: REQUIRED. Image ID (str)
            :param group_id: NOT REQUIRED. If image in group. Group ID (str)
            :return:
            """

            if image_id is None:
                return {'result': 'Error', 'data': '"image_id" is empty"'}

            return ok_session().post(
                '',
                params={
                    'method': 'photos.deletePhoto',
                    'gid': group_id,
                    'photo_id': image_id,
                }).json()

        def delete_tags(self, image_id: str = None, tag_ids: str | list = None):

            """
            Deletes a photo tag
            :param image_id: REQUIRED. Image ID (str)
            :param tag_ids: REQUIRED. Tag IDs (str | list). A comma-separated list of tag IDs to be deleted.
                Maximum of 10 IDs.
            :return:
            """

            if image_id is None:
                return {'result': 'Error', 'data': '"image_id" is empty"'}
            elif tag_ids is None:
                return {'result': 'Error', 'data': '"tag_ids" is empty"'}

            if isinstance(tag_ids, str):
                tag_ids = [tag_ids]

            return ok_session().post(
                '',
                params={
                    'method': 'photos.deleteTags',
                    'photo_id': image_id,
                    'tag_ids': ','.join(tag_ids),
                }).json()

        def edit_album(self, album_id: str = None, group_id: str = None, title: str = None, description: str = None,
                       type_album: str | list = None):

            """
            Creates a photo album for the specified user or group
            :param album_id: REQUIRED. Album ID (str)
            :param group_id: NOT REQUIRED if album in group. User ID (str)
            :param title: REQUIRED. New album title (str)
            :param description: NOT REQUIRED. if album not in group. New album description (str)
            :param type_album: NOT REQUIRED. if album not in group. Album type (list or str) [CLASSMATE, CLOSE_FRIEND,
                COLLEAGUE, COMPANION_IN_ARMS, CURSEMATE, FRIENDS, LOVE, PRIVATE, PUBLIC, RELATIVE, SHARED] default None
            :return:
            """

            if album_id is None:
                return {'result': 'Error', 'data': '"album_id" is empty"'}

            album_type = 'GROUP' if group_id else 'SHARED'
            info: dict[str, dict] = self.get_album_info(album_id=album_id, group_id=group_id, album_type=album_type)
            old_title = info.get('album').get('title')
            old_description = info.get('album').get('description')
            old_type = info.get('album').get('author_type')

            if isinstance(type_album, str):
                type_album = [type_album]

            return ok_session().post(
                '',
                params={
                    'method': 'photos.editAlbum',
                    'gid': group_id,
                    'aid': album_id,
                    'title': title if title else old_title,
                    'description': description if description else old_description,
                    'type': type_album if type_album or group_id else old_type,
                }).json()

        def get_album_info(self, album_id: str = None, friend_id: str = None, group_id: str = None,
                           album_type: str | list = None):

            """
            Getting information about the album
            :param album_id: REQUIRED. Album ID (str)
            :param friend_id: NOT REQUIRED. ID of the friend whose photos you want to get (str)
            :param group_id: NOT REQUIRED. ID of the group whose album you want to request information for (str)
            :param album_type: NOT REQUIRED. Album Type (str | list) [GROUP, SHARED] default *
            :return:
            """

            if album_id is None:
                return {'result': 'Error', 'data': '"album_id" is empty"'}
            if album_type is None:
                return {'result': 'Error', 'data': '"album_type" is empty"'}

            if isinstance(album_type, str):
                album_type = [album_type]

            return ok_session().post(
                '',
                params={
                    'method': 'photos.getAlbumInfo',
                    'gid': group_id,
                    'aid': album_id,
                    'fid': friend_id,
                    'album_type': album_type
                }).json()

        def get_photo_info(self, photo_id: str = None, group_id: str = None):

            """
            Getting information about the photo
            :param photo_id: REQUIRED. Photo ID (str)
            :param group_id: NOT REQUIRED. If image in group. Group ID (str)
            :return:
            """

            if photo_id is None:
                return {'result': 'Error', 'data': '"photo_id" is empty"'}

            return ok_session().post(
                '',
                params={
                    'method': 'photos.getPhotoInfo',
                    'gid': group_id,
                    'photo_id': photo_id,
                }).json()

        def edit_photo(self, photo_id: str = None, group_id: str = None, description: str = None):

            """
            Getting information about the photo
            :param photo_id: REQUIRED. Photo ID (str)
            :param group_id: NOT REQUIRED. If image in group. Group ID (str)
            :param description: REQUIRED. New photo description (str)
            :return:
            """

            if photo_id is None:
                return {'result': 'Error', 'data': '"photo_id" is empty"'}
            elif description is None:
                return {'result': 'Error', 'data': '"description" is empty"'}

            return ok_session().post(
                '',
                params={
                    'method': 'photos.editPhoto',
                    'gid': group_id,
                    'photo_id': photo_id,
                    'description': description
                }).json()

        def get_album_likes(self, album_id: str = None, group_id: str = None, count: int = 100):

            """
            Get a list of users who have assigned a “Like” to an album
            :param album_id: REQUIRED. Album ID (str)
            :param group_id: NOT REQUIRED. If album in group. Group ID (str)
            :param count: NOT REQUIRED. Number of likes to get (int) default 100
            :return:
            """

            if album_id is None:
                return {'result': 'Error', 'data': '"album_id" is empty"'}

            return ok_session().post(
                '',
                params={
                    'method': 'photos.getAlbumLikes',
                    'gid': group_id,
                    'aid': album_id,
                    'count': count,
                }).json()

        def get_albums(self, user_id: str = None, group_id: str = None, count: int = 100,
                       detect_total_count: bool = False, album_type: str | list = "GROUP"):

            """
            Returns a list of the specified user or group photo albums
            :param user_id: REQUIRED. If get album from user. User ID (str)
            :param group_id: REQUIRED. If get album from group. Group ID (str)
            :param count: NOT REQUIRED. Number of photos to get (int) default 100
            :param detect_total_count: NOT REQUIRED An attempt to determine the total number of available albums (bool).
                Default False.
            :param album_type: NOT REQUIRED. Type of album (str | list) [GROUP, SHARED] default "GROUP"
            :return:
            """

            if user_id is None and group_id is None:
                return {'result': 'Error', 'data': '"album_id" or "group_id" is empty"'}

            if user_id is not None and group_id is not None:
                return {'result': 'Error', 'data': '"album_id" and "group_id" is not empty. Choose one value"'}

            if isinstance(album_type, str):
                album_type = [album_type]

            return ok_session().post(
                '',
                params={
                    'method': 'photos.getAlbums',
                    'gid': group_id,
                    'fid': user_id,
                    'detectTotalCount': detect_total_count,
                    'count': count,
                    'album_type': album_type
                }).json()

        def get_info(self, user_id: str = None, group_id: str = None, album_id: str = None, friend_id: str = None,
                     photo_ids: str | list = None):

            """
            Getting information about photos of a user, friend, or group
            :param user_id: NOT REQUIRED. User ID (str)
            :param group_id: NOT REQUIRED. Group ID (str)
            :param album_id: NOT REQUIRED. Album ID (str)
            :param friend_id: NOT REQUIRED. Friend ID (str)
            :param photo_ids: REQUIRED. Photo IDs (list | str) max 100
            :return:
            """

            if user_id is None and group_id is None and friend_id is None:
                return {'result': 'Error', 'data': '"album_id" or "group_id" or "friend_id" is empty"'}

            if isinstance(photo_ids, str):
                photo_ids = [photo_ids]

            if len(photo_ids) > 100:
                return {'result': 'Error', 'data': '"photo_ids" is too long (max 100).'}

            return ok_session().post(
                '',
                params={
                    'method': 'photos.getInfo',
                    'gid': group_id,
                    'fid': friend_id,
                    'aid': album_id,
                    'uid': user_id,
                    'photo_ids': ','.join(photo_ids)
                }).json()

        def get_photo_likes(self, photo_id: str = None, group_id: str = None, count: int = 100):

            """
            Get a list of users who have assigned a “Like" to photos
            :param photo_id: REQUIRED. Photo ID (str)
            :param group_id: NOT REQUIRED. If image in group. Group ID (str)
            :param count: NOT REQUIRED. Number of likes to get (int) default 100
            :return:
            """

            if photo_id is None:
                return {'result': 'Error', 'data': '"photo_id" is empty"'}

            return ok_session().post(
                '',
                params={
                    'method': 'photos.getPhotoLikes',
                    'gid': group_id,
                    'photo_id': photo_id,
                    'count': count
                }).json()

        def get_photo_marks(self, count: int = 20, detect_total_count: bool = False):

            """
            Returns a list of all ratings of the user's photos
            :param count: NOT REQUIRED. The number of results returned (int 1...20) default 20
            :param detect_total_count: NOT REQUIRED. An attempt to determine the total number of photo ratings (bool).
                Default: False.
            :return:
            """

            return ok_session().post(
                '',
                params={
                    'method': 'photos.getPhotoMarks',
                    'count': count,
                    'detectTotalCount': detect_total_count,
                }).json()

        def get_photos(self, group_id: str = None, friend_id: str = None, album_id: str = None, count: int = 100,
                       detect_total_count: bool = False):

            """
            Getting a list of photos of a user, his friend, or a group
            :param group_id: NOT REQUIRED. ID of the group where the album is hosted (str)
            :param friend_id: NOT REQUIRED. The ID of the friend whose photos you want to get. Ignored if the guid is
                specified. If neither fid nor gid is specified, the photos of the current user will be returned (str).
            :param album_id: REQUIRED. The ID of the album. If not specified, photos from the personal album are
                returned. (str)
            :param count: NOT REQUIRED. The number of results returned (int) default 100
            :param detect_total_count: NOT REQUIRED. An attempt to determine the total number of photo ratings (bool).
                Default: False.
            :return:
            """

            if group_id is None and friend_id is None:
                return {'result': 'Error', 'data': '"group_id" or "friend_id" is empty"'}

            if group_id is not None and friend_id is not None:
                return {'result': 'Error', 'data': '"group_id" and "friend_id" are not empty. Choose one value"'}

            return ok_session().post(
                '',
                params={
                    'method': 'photos.getPhotos',
                    'gid': group_id,
                    'fid': friend_id,
                    'aid': album_id,
                    'count': count,
                    'detectTotalCount': detect_total_count,
                }).json()

        def get_tags(self, photo_id: str = None):

            """
            Getting a list of marked users in a photo
            :param photo_id: REQUIRED. Photo ID (str)
            :return:
            """

            if photo_id is None:
                return {'result': 'Error', 'data': '"photo_id" is empty"'}

            return ok_session().post(
                '',
                params={
                    'method': 'photos.getTags',
                    'photo_id': photo_id,
                }).json()

        def get_user_album_photos(self, album_id: str = None, count: int = 100, detect_total_count: bool = False):

            """
            Returns a list of photos from the specified album (Only USERS albums)
            :param album_id: REQUIRED. Album ID (str)
            :param count: NOT REQUIRED. The number of results returned (int) default 100
            :param detect_total_count: NOT REQUIRED. An attempt to determine the total number of photo ratings (bool).
                Default: False.
            :return:
            """

            if album_id is None:
                return {'result': 'Error', 'data': '"album_id" is empty"'}

            return ok_session().post(
                '',
                params={
                    'method': 'photos.getUserAlbumPhotos',
                    'aid': album_id,
                    'count': count,
                    'detectTotalCount': detect_total_count,
                }).json()

        def get_user_photos(self, user_id: str = None, count: int = 100, photo_ids: str | list = '',
                            detect_total_count: bool = False):

            """
            Returns a list of personal photos of the specified user
            :param user_id: REQUIRED. User ID (str)
            :param count: NOT REQUIRED. The number of results returned (int) default 100
            :param photo_ids: NOT REQUIRED. Photo IDs (list | str) max 100
            :param detect_total_count: NOT REQUIRED. An attempt to determine the total number of photo ratings (bool).
                Default: False.
            :return:
            """

            if user_id is None:
                return {'result': 'Error', 'data': '"user_id" is empty"'}

            if isinstance(photo_ids, str):
                photo_ids = [photo_ids]

            return ok_session().post(
                '',
                params={
                    'method': 'photos.getUserPhotos',
                    'fid': user_id,
                    'count': count,
                    'detectTotalCount': detect_total_count,
                    'photos': ','.join(photo_ids)
                }).json()

        def set_album_main_photo(self, album_id: str = None, photo_id: str = None, group_id: str = None):

            """
            Set a photo as an album cover
            :param album_id: REQUIRED. Album ID (str)
            :param photo_id: REQUIRED. Photo ID (str)
            :param group_id: NOT REQUIRED. If album in group. Group ID (str)
            :return:
            """

            if album_id is None:
                return {'result': 'Error', 'data': '"album_id" is empty"'}
            if photo_id is None:
                return {'result': 'Error', 'data': '"photo_id" is empty"'}

            return ok_session().post(
                '',
                params={
                    'method': 'photos.setAlbumMainPhoto',
                    'aid': album_id,
                    'gid': group_id,
                    'photo_id': photo_id,
                }).json()


ok_sess = ApiOk()
# print(ok_sess.Group().get_counters('70000006834375', ['CATALOGS', 'BLACK_LIST']))
# print(ok_sess.Group().get_info('70000006834375', ['ACCESS_TYPE']))
# print(ok_sess.Group().get_members('70000006834375'))
# print(ok_sess.Group().get_stat_overview('70000006834375', '*'))
# print(ok_sess.Group().get_stat_people('70000006834375', '*'))
# print(ok_sess.Group().get_stat_topic('157112758692807', 'FEEDBACK'))
# print(ok_sess.Group().get_stat_topics('70000006834375', 'FEEDBACK', 10))
# print(ok_sess.Group().get_stat_trends('70000006834375'))
# print(ok_sess.Group().get_user_groups_by_ids('70000006834375', '563439414215'))
# print(ok_sess.Group().is_messages_allowed('70000006834375'))
# print(ok_sess.Group().pin_group_feed()) ???????????????????????
# print(ok_sess.Group().set_group_image('70000006834375', '961020341703'))

# print(ok_sess.Images().create_album(group_id='70000006834375', title='Example album', description='Description'))
# print(ok_sess.Images().delete_album(album_id='961074571207', group_id='70000006834375'))
# print(ok_sess.Images().delete_images(image_id='961020341447'))
# print(ok_sess.Images().delete_tags(image_id='961020341447', tag_ids='')) ????
# print(ok_sess.Images().edit_album(album_id='961075815367', title='Lol', description='Kek'))
# print(ok_sess.Images().get_album_info(album_id='961074757319', group_id='70000006834375', album_type='GROUP'))
# print(ok_sess.Images().get_photo_info('961020341703', '70000006834375'))
# print(ok_sess.Images().edit_photo(photo_id='961015062983',  description='New description'))
# print(ok_sess.Images().get_album_likes(album_id='961075815367'))
# print(ok_sess.Images().get_albums(group_id='70000006834375'))
# print(ok_sess.Images().get_info(group_id='70000006834375', album_id='961012684487', photo_ids='961020341703'))
# print(ok_sess.Images().get_photo_likes(group_id='70000006834375', photo_id='961020341703'))
# print(ok_sess.Images().get_photo_likes(group_id='70000006834375', photo_id='961020341703'))
# print(ok_sess.Images().get_photo_marks())
# print(ok_sess.Images().get_photos(group_id='70000006834375', album_id='961012684487'))
# print(ok_sess.Images().get_tags(photo_id='961015062983'))
# print(ok_sess.Images().get_user_album_photos(album_id='961012684487'))
# print(ok_sess.Images().get_user_photos(user_id='563439414215'))
# print(ok_sess.Images().set_album_main_photo(album_id='961104797639', photo_id='961015062983'))
# ok_sess.Images().upload_image(
#     [
#         Path(r'D:\Desktop\example\WSM00000005195446_orig_03.jpg'),
#         Path(r'D:\Desktop\example\WSM00000005195446_orig_04.jpg')
#      ]
# )

# ok_sess.Market().update_product_catalogs(
#     gid=os.getenv("GROUP_ID_OK"),
#     product_id='157108075031495',
#     catalog_ids=['157108272032711', '157107714059207']
# )
# ok_sess.Market().set_status_product('157108288285639', 'ACTIVE')
# ok_sess.Market().reorder_catalog(os.getenv("GROUP_ID_OK"), '157108272032711', '157107714059207')
# ok_sess.Market().reorder_product(
#     catalog_id='157107714059207',
#     product_id='157108288023495',
#     after_product_id='157108288285639'
# )
# ok_sess.Market().add_catalog(os.getenv("GROUP_ID_OK"), 'Example123')
# ok_sess.Market().add_product(
#     group_id=os.getenv("GROUP_ID_OK"),
#     catalog_ids=['157107714059207'],
#     product_title='Product title',
#     product_description='d' * 1000,
#     price=10000,
#     images=[961015062471, 961015062983]
# )
# ok_sess.Market().get_product(['157108075031495', '157108013820871'])
# ok_sess.Market().delete_product('157107813280711')
# ok_sess.Market().delete_catalog(
#     group_id=os.getenv('GROUP_ID_OK'),
#     catalog_id='157108272229319',
#     delete_products=False
# )
# ok_sess.Market().edit_product(
#     product_id='157108075031495',
#     price=18000
# )
# ok_sess.Market().edit_catalog(os.getenv('GROUP_ID_OK'), '157107714059207', 'New super name')
# ok_sess.Market().pin_product('157107714059207', '157108288023495', False)
