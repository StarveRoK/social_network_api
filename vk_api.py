
from functools import lru_cache
from pathlib import Path

from loguru import logger
import os
import dotenv
from pydantic import AliasChoices, Field, BaseModel
from requests_toolbelt.sessions import BaseUrlSession
from datetime import datetime

dotenv.load_dotenv()

@lru_cache
def vk_session():
    return VkSession()


class Credentials(BaseModel):
    access_token: str = Field(..., validation_alias=AliasChoices('TOKEN_VK'))
    v: str = Field(..., validation_alias=AliasChoices('API_VERSION'))

    def __init__(self):
        dotenv.load_dotenv()
        super().__init__(**dotenv.dotenv_values())

    @property
    def params(self):
        return self.model_dump(exclude={'group_id'})


class VkSession(BaseUrlSession):
    def __init__(self):
        super().__init__('https://api.vk.ru/method/')

        self._credentials = Credentials()

    def request(self, method, url, **kwargs):
        kwargs['params'] = kwargs.get('params', {}) | self._credentials.params
        return super().request(method, url, **kwargs)


class ApiVk:

    def __init__(self, token):

        """
        StarveR api to connect vk.ru
        :param token: Permanent or temporary application token
        """

        self.token = token
        # self.api_url = 'https://api.vk.com/method'

    def add(self, group_id: str = None, name: str = None, description: str = None, category_id: str = None,
            price: int = None, old_price: int = None, deleted: bool = False, main_photo_id: str = None,
            photo_ids: list | str = None, video_ids: list | str = None, url: str = '', is_main_variant: bool = False,
            dimension_width: int = None, dimension_height: int = None, dimension_length: int = None, weight: int = None,
            sku: str = '', stock_amount: int = None, api_version: str = '5.199'):

        """
        The method adds a new product.
        :param group_id: REQUIRED. Group ID (str)
        :param name: REQUIRED. Product name (str)
        :param description: REQUIRED. Product description (str)
        :param category_id: REQUIRED.
        :param price: NOT REQUIRED. Product price (int)
        :param old_price: NOT REQUIRED. Product old price (int)
        :param deleted: NOT REQUIRED. The status of the product. Possible values: True — the product is unavailable.
            False — the product is available.
        :param main_photo_id: NOT REQUIRED. Photo ID (str)
        :param photo_ids: NOT REQUIRED. Photo IDs (list | str)
        :param video_ids: NOT REQUIRED. Video IDs (list | str)
        :param url: NOT REQUIRED. Link to the product's website. Up to 320 characters (str)
        :param is_main_variant: NOT REQUIRED. A sign of whether the product will be the main one in its group (bool)
        :param dimension_width: NOT REQUIRED. Dimension width (int)
        :param dimension_height: NOT REQUIRED. Dimension height (int)
        :param dimension_length: NOT REQUIRED. Dimension length (int)
        :param weight: NOT REQUIRED. Product weight (int)
        :param sku: NOT REQUIRED. The article of the product. Up to 50 characters (str)
        :param stock_amount: NOT REQUIRED. The quantity of the product in stock (for an extended store).
            -1 - unlimited number
            0 - the product is unavailable
            > 0 - the quantity of the product
        :return:
        """

        if group_id is None:
            return {'result': 'Error', 'data': '"group_id" is empty"'}
        if name is None:
            return {'result': 'Error', 'data': '"name" is empty"'}
        if description is None:
            return {'result': 'Error', 'data': '"description" is empty"'}
        if category_id is None:
            return {'result': 'Error', 'data': '"category_id" is empty"'}

        if len(url) > 320:
            return {'result': 'Error', 'data': '"url" is too long"'}
        if len(sku) > 50:
            return {'result': 'Error', 'data': '"sku" is too long"'}

        if isinstance(photo_ids, str):
            photo_ids = [photo_ids]
        if isinstance(video_ids, str):
            video_ids = [video_ids]

        return vk_session().post(
            'market.add',
            params={
                'owner_id': group_id,
                'name': name,
                'description': description,
                'category_id': category_id,
                'price': price,
                'old_price': old_price,
                'deleted': deleted,
                'main_photo_id': main_photo_id,
                'photo_ids': photo_ids,
                'video_ids': video_ids,
                'url': url,
                'is_main_variant': is_main_variant,
                'dimension_width': dimension_width,
                'dimension_height': dimension_height,
                'dimension_length': dimension_length,
                'weight': weight,
                'sku': sku,
                'stock_amount': stock_amount,
                'v': api_version
            }).json()

    class Wall:

        def attachment_create(self, el):
            if el[0] is None:
                return ''
            elif isinstance(el[0], dict):
                if 'owner' in el[0] and 'media' in el[0]:
                    return f'{el[1]}{el[0].get("owner")}_{el[0].get("media")},'
                else:
                    return 'Error. Not found "owner" or "media"'
            elif isinstance(el[0], list):
                result = ''
                for e in el[0]:
                    ans = self.attachment_create((e, el[1]))
                    if 'Error' in ans:
                        return ans
                    else:
                        result += ans
                return result
            else:
                return 'Error. Elem error (not "list" or "dict")'

        def post(self, owner_id: str = None, friends_only: bool = False, from_group: bool = False, message: str = None,
                 services: str = None, signed: bool = False, publish_date: datetime = None, lat: int = None,
                 long: int = None, place_id: str = None, post_id: str = None, guid: str = None,
                 mark_as_ads: bool = False, link_title: str = None, link_photo_id: str = None,
                 close_comments: bool = False, donut_paid_duration: int = None, mute_notifications: bool = False,
                 copyright: str = None, photos: dict | list[dict] = None, videos: dict | list[dict] = None,
                 audios: dict | list[dict] = None, docs: dict | list[dict] = None, pages: dict | list[dict] = None,
                 notes: dict | list[dict] = None, polls: dict | list[dict] = None, albums: dict | list[dict] = None,
                 markets: dict | list[dict] = None, market_albums: dict | list[dict] = None,
                 audio_playlists: dict | list[dict] = None) -> dict:

            """
            Post an entry on the wall
            https://dev.vk.com/ru/method/wall.post
            :param owner_id: REQUIRED. The ID of the user or community on whose wall you want to post the post.
                The community ID must start with a "-" (str)
            :param friends_only: Information about who can access the record. Possible values:
                True — the record is available only to friends.
                False — the record is available to all users. The value is used by default.
            :param from_group: Information about who the record is being published on behalf of. The
                parameter is taken into account if the owner_id is less than 0, in this case the entry is published on
                the group wall. Possible values:
                True — the entry will be published on behalf of the community.
                False — the record will be published on behalf of the user. (default)
            :param message: The text of the message. REQUIRED parameter if the attachments parameter is not specified.
            :param services: A list of services or sites to export the record to, if the user has filled in the
                appropriate setting.
            :param signed: Information about whether to add a signature to an entry posted on behalf of the community.
                The parameter is taken into account only when posting an entry on the community wall and specifying the
                from_group parameter. Possible values:
                True — add a signature (the name of the user who suggested the entry).
                False — do not add a signature. The value is used by default.
            :param publish_date: Date and time of publication of the record (Unix Timestamp). The publication of the
                record will be postponed until the specified time.
            :param lat: Geographic latitude in degrees. The range of values is from -90 to 90. (int)
            :param long: Geographical longitude in degrees. The range of values is from -180 to 180. (int)
            :param place_id: The ID of the location where the user is marked. (str)
            :param post_id: ID of the record to be published. This parameter is used to publish deferred entries and
                suggested news. (str)
            :param guid: A unique identifier designed to prevent the same record from being sent again. Valid for one
                hour. (str)
            :param mark_as_ads: Information about whether to add a mark is an advertisement for an entry posted on
                behalf of the community. The parameter is taken into account only when posting an entry on the community
                wall and specifying the from_group parameter. Possible values:
                True — add a mark. The value is used by default.
                False — do not add a mark.
            :param link_title: The title of the snippet for the attached object. (str)
            :param link_photo_id: ID of the video or photo attached to the post. Specified in the format
                {owner-id}_{photo-id}.
            :param close_comments:
                Information about whether to enable the ability to comment on the record. Possible values:
                True — comments on the post are disabled.
                False — comments on the entry are included. The value is used by default.
            :param donut_paid_duration: The period of time during which the recording will be available only to don —
                paid subscribers of VK Donut. Possible values:
                -1 — exclusively for dons.
                86400 — for 1 day.
                172800 — for 2 days.
                259200 — for 3 days.
                345600 — for 4 days.
                432000 — for 5 days.
                518400 — for 6 days.
                604800 — for 7 days.
            :param mute_notifications: Information about whether notifications are enabled for the publication of the
                record.
                True — Recording notifications are disabled.
                False — notifications for recording are enabled. The value is used by default.
            :param copyright: The source of the material. External and internal links are supported. (str)
            :param photos: Add photos to the post. Example: {'owner': owner_id, 'media': media_id} or
                [{'owner': owner_id_1, 'media': media_id_1}, {'owner': owner_id_2, 'media': media_id_2}] (Attachments)
            :param videos: The format is like the photos (Attachments)
            :param audios: The format is like the photos (Attachments)
            :param docs: The format is like the photos (Attachments)
            :param pages: The format is like the photos (Attachments)
            :param notes: The format is like the photos (Attachments)
            :param polls: The format is like the photos (Attachments)
            :param albums: The format is like the photos (Attachments)
            :param markets: The format is like the photos (Attachments)
            :param market_albums: The format is like the photos (Attachments)
            :param audio_playlists: The format is like the photos (Attachments)
            :return:
            """

            if owner_id is None:
                return {'result': 'error', 'data': '"owner_id" is empty"'}

            attachments = ''
            for el in ((photos, 'photo'), (videos, 'video'), (audios, 'audio'), (docs, 'doc'), (pages, 'page'),
                       (notes, 'note'), (polls, 'poll'), (albums, 'album'), (markets, 'market'),
                       (market_albums, 'market_albums'), (audio_playlists, 'audio_playlist')):
                ans = self.attachment_create(el)
                if 'Error' in ans:
                    return {'result': 'error', 'data': ans}
                else:
                    attachments += ans

            if attachments:
                attachments = attachments[:-1]

            if attachments is None and message is None:
                return {'result': 'error', 'data': '"attachments" and "message" are empty'}

            # if attachments and message:
            #     return {'result': 'error', 'data': '"attachments" and "message" are not empty. Choose one value'}

            if publish_date:
                publish_date = publish_date.timestamp()

            response = vk_session().post(
                'wall.post',
                params={
                    'owner_id': owner_id,
                    'friends_only': 1 if friends_only else 0,
                    'from_group': 1 if from_group else 0,
                    'message': message,
                    'services': services,
                    'signed': 1 if signed else 0,
                    'publish_date': publish_date,
                    'lat': lat,
                    'long': long,
                    'place_id': place_id,
                    'post_id': post_id,
                    'guid': guid,
                    'mark_as_ads': 1 if mark_as_ads else 0,
                    'link_title': link_title,
                    'link_photo_id': link_photo_id,
                    'close_comments': 1 if close_comments else 0,
                    'donut_paid_duration': donut_paid_duration,
                    'mute_notifications': 1 if mute_notifications else 0,
                    'copyright': copyright,
                    'attachments': attachments,
                }).json()

            if 'error' in response:
                return {
                    'result': 'error',
                    'data': f'Code: {response.get("error").get("error_code")}. {response.get("error").get("error_msg")}'

                }
            else:
                return {'result': 'success', 'data': response.get('response')}

        def pin(self, owner_id: str = None, post_id: str = None) -> dict:

            """
            Fixes the post at the top of the page by ID
            https://dev.vk.com/ru/method/wall.pin
            :param owner_id: REQUIRED. The ID of the user or community on whose wall you want to post the post.
                The community ID must start with a "-" (str)
            :param post_id: REQUIRED. The ID of the post you want to pin. (str)
            :return:
            """

            if owner_id is None:
                return {'result': 'error', 'data': '"owner_id" is empty"'}
            elif post_id is None:
                return {'result': 'error', 'data': '"post_id" is empty"'}

            response = vk_session().post(
                'wall.pin',
                params={
                    'owner_id': owner_id,
                    'post_id': post_id,
                }).json()

            if not response.get('response'):
                return {'result': 'error', 'data': f'The post failed to pinned'}
            else:
                return {'result': 'success', 'data': 'The post has been successfully pinned'}

        def unpin(self, owner_id: str = None, post_id: str = None) -> dict:

            """
            Fixes the post at the top of the page by ID
            https://dev.vk.com/ru/method/wall.unpin
            :param owner_id: REQUIRED. The ID of the user or community. The community ID must start with a "-" (str)
            :param post_id: REQUIRED. The ID of the post you want to unpin. (str)
            :return:
            """

            if owner_id is None:
                return {'result': 'error', 'data': '"owner_id" is empty"'}
            elif post_id is None:
                return {'result': 'error', 'data': '"post_id" is empty"'}

            response = vk_session().post(
                'wall.unpin',
                params={
                    'owner_id': owner_id,
                    'post_id': post_id,
                }).json()

            if not response.get('response'):
                return {'result': 'error', 'data': f'The post failed to unpinned'}
            else:
                return {'result': 'success', 'data': 'The post has been successfully unpinned'}

        def report_comment(self, owner_id: str = None, comment_id: str = None, reason: int = None) -> dict:

            """
            Send a complaint for a comment
            https://dev.vk.com/ru/method/wall.reportComment
            :param owner_id: REQUIRED. The ID of the user or community on whose wall you want to post the post.
                The community ID must start with a "-" (str)
            :param comment_id: REQUIRED. The ID of the comment (str)
            :param reason: The reason for the complaint:
                0 — spam;
                1 — Child pornography;
                2 — extremism;
                3 — violence;
                4 — Drug propaganda;
                5 — Adult material;
                6 — insult;
                8 — calls for suicide.
            :return:
            """

            if owner_id is None:
                return {'result': 'error', 'data': '"owner_id" is empty"'}
            elif comment_id is None:
                return {'result': 'error', 'data': '"comment_id" is empty"'}
            elif reason is None:
                return {'result': 'error', 'data': '"reason" is empty"'}

            if 8 < reason < 0:
                return {'result': 'error', 'data': '"reason" must be between 0 and 8'}

            response = vk_session().post(
                'wall.reportComment',
                params={
                    'owner_id': owner_id,
                    'comment_id': comment_id,
                    'reason': reason
                }).json()

            if not response.get('response'):
                return {'result': 'error', 'data': f'The complaint has not been successfully sent'}
            else:
                return {'result': 'success', 'data': 'The complaint has been successfully sent'}

        def report_post(self, owner_id: str = None, post_id: str = None, reason: int = None) -> dict:

            """
            Send a complaint for a comment
            https://dev.vk.com/ru/method/wall.reportPost
            :param owner_id: REQUIRED. The ID of the user or community on whose wall you want to post the post.
                The community ID must start with a "-" (str)
            :param post_id: REQUIRED. The ID of the post (str)
            :param reason: The reason for the complaint:
                0 — spam;
                1 — Child pornography;
                2 — extremism;
                3 — violence;
                4 — Drug propaganda;
                5 — Adult material;
                6 — insult;
                8 — calls for suicide.
            :return:
            """

            if owner_id is None:
                return {'result': 'error', 'data': '"owner_id" is empty"'}
            elif post_id is None:
                return {'result': 'error', 'data': '"post_id" is empty"'}
            elif reason is None:
                return {'result': 'error', 'data': '"reason" is empty"'}

            if 8 < reason < 0:
                return {'result': 'error', 'data': '"reason" must be between 0 and 8'}

            response = vk_session().post(
                'wall.reportPost',
                params={
                    'owner_id': owner_id,
                    'post_id': post_id,
                    'reason': reason
                }).json()

            if not response.get('response'):
                return {'result': 'error', 'data': f'The complaint has not been successfully sent'}
            else:
                return {'result': 'success', 'data': 'The complaint has been successfully sent'}

        def repost(self, object_id: str = None, message: str = None, group_id: str = None, mark_as_ads: bool = False,
                   mute_notifications: bool = False) -> dict:

            """
            Object repost
            https://dev.vk.com/ru/method/wall.repost
            :param object_id: REQUIRED. The string identifier of the object to be placed on the wall, for example,
                wall66748_3675 or wall-1_340364.It is formed from the object type (wall, photo, video, etc.), the 
                identifier of the object owner and the identifier of the object itself. (str) 
            :param message: The accompanying text that will be added to the record with the object.
            :param group_id: The ID of the community on whose wall the entry with the object will be posted. If not
                specified, the entry will be posted on the wall of the current user.
            :param mark_as_ads: 
            :param mute_notifications: Information about whether notifications are enabled for the publication of the
                record.
                True — Recording notifications are disabled.
                False — notifications for recording are enabled.The value is used by default.
            :return: 
            """

            if object_id is None:
                return {'result': 'error', 'data': '"object_id" is empty"'}

            response = vk_session().post(
                'wall.repost',
                params={
                    'object': object_id,
                    'message': message,
                    'group_id': group_id if "-" not in group_id else group_id.replace('-', ''),
                    'mark_as_ads': 1 if mark_as_ads else 0,
                    'mute_notifications': 1 if mute_notifications else 0,
                }).json()

            if 'error' in response:
                return {
                    'result': 'error',
                    'data': f'Code: {response.get("error").get("error_code")}. {response.get("error").get("error_msg")}'
                }
            else:
                return {'result': 'success', 'data': response.get('response')}

        def restore_post(self, owner_id: str = None, post_id: str = None) -> dict:

            """
            Restores a deleted post on a user's or community's wall
            https://dev.vk.com/ru/method/wall.restore
            :param owner_id: REQUIRED. The ID of the user or community on whose wall you want to post the post.
                The community ID must start with a "-" (str)
            :param post_id: REQUIRED. The ID of the post (str)
            :return:
            """

            if owner_id is None:
                return {'result': 'error', 'data': '"owner_id" is empty"'}
            elif post_id is None:
                return {'result': 'error', 'data': '"post_id" is empty"'}

            response = vk_session().post(
                'wall.restore',
                params={
                    'owner_id': owner_id,
                    'post_id': post_id,
                }).json()

            if not response.get('response'):
                return {'result': 'error', 'data': f'The record has not been restored'}
            else:
                return {'result': 'success', 'data': 'The record has been successfully restored'}

        def restore_comment(self, owner_id: str = None, comment_id: str = None) -> dict:

            """
            Restores a deleted post on a user's or community's wall
            https://dev.vk.com/ru/method/wall.restoreComment
            :param owner_id: REQUIRED. The ID of the user or community. The community ID must start with a "-" (str)
            :param comment_id: REQUIRED. The ID of the comment (str)
            :return:
            """

            if owner_id is None:
                return {'result': 'error', 'data': '"owner_id" is empty"'}
            elif comment_id is None:
                return {'result': 'error', 'data': '"comment_id" is empty"'}

            response = vk_session().post(
                'wall.restoreComment',
                params={
                    'owner_id': owner_id,
                    'comment_id': comment_id,
                }).json()

            if not response.get('response'):
                return {'result': 'error', 'data': f'The comment has not been restored'}
            else:
                return {'result': 'success', 'data': 'The comment has been successfully restored'}

        def check_copyright_link(self, link: str = None) -> dict:

            """
            Check if the link is correct
            https://dev.vk.com/ru/method/wall.checkCopyrightLink
            :param link: REQUIRED. Link (str)
            :return:
            """

            if link is None:
                return {'result': 'error', 'data': '"link" is empty"'}

            response = vk_session().post(
                'wall.checkCopyrightLink',
                params={
                    'link': link,
                }).json()

            if not response.get('response'):
                return {'result': 'error', 'data': f'The link is correct'}
            else:
                return {'result': 'success', 'data': 'The link is incorrect'}

        def close_comment_on_post(self, owner_id: str = None, post_id: str = None) -> dict:

            """
            Close comments on post
            https://dev.vk.com/ru/method/wall.closeComments
            :param owner_id: REQUIRED. The ID of the user or community. The community ID must start with a "-" (str)
            :param post_id: REQUIRED. post_id (str)
            :return:
            """

            if owner_id is None:
                return {'result': 'error', 'data': '"owner_id" is empty"'}
            elif post_id is None:
                return {'result': 'error', 'data': '"post_id" is empty"'}

            response = vk_session().post(
                'wall.closeComments',
                params={
                    'owner_id': owner_id,
                    'post_id': post_id
                }).json()

            if not response.get('response'):
                return {'result': 'error', 'data': f'Comments have not been disabled'}
            else:
                return {'result': 'success', 'data': 'Comments have been successfully disabled'}

        def open_comment_on_post(self, owner_id: str = None, post_id: str = None) -> dict:

            """
            Open comments on post
            https://dev.vk.com/ru/method/wall.openComments
            :param owner_id: REQUIRED. The ID of the user or community. The community ID must start with a "-" (str)
            :param post_id: REQUIRED. post_id (str)
            :return:
            """

            if owner_id is None:
                return {'result': 'error', 'data': '"owner_id" is empty"'}
            elif post_id is None:
                return {'result': 'error', 'data': '"post_id" is empty"'}

            response = vk_session().post(
                'wall.openComments',
                params={
                    'owner_id': owner_id,
                    'post_id': post_id
                }).json()

            if not response.get('response'):
                return {'result': 'error', 'data': f'Comments have not been enabled'}
            else:
                return {'result': 'success', 'data': 'Comments have been successfully enabled'}

        def create_comment(self, owner_id: str = None, post_id: str = None, from_group: bool = False,
                           message: str = None, reply_to_comment: str = None, sticker_id: str = None, guid: str = None,
                           photos: dict | list[dict] = None, videos: dict | list[dict] = None,
                           audios: dict | list[dict] = None, docs: dict | list[dict] = None,) -> dict:

            """
            Creates a new comment
            https://dev.vk.com/ru/method/wall.createComment
            :param owner_id: REQUIRED. The ID of the user or community. The community ID must start with a "-" (str)
            :param post_id: REQUIRED. The ID of the post (str)
            :param from_group: Information about who the record is being published on behalf of. The
                parameter is taken into account if the owner_id is less than 0, in this case the entry is published on
                the group wall. Possible values:
                True — the entry will be published on behalf of the community.
                False — the record will be published on behalf of the user. (default)
            :param message: The text of the comment. Required parameter if the attachments parameter is not
                passed.
            :param reply_to_comment: Id of the comment to which a new comment should be added in response.
            :param sticker_id: The sticker ID.
            :param guid: A unique identifier designed to prevent the same comment from being sent again.
            :param photos: photos: Add photos to the post. Example: {'owner': owner_id, 'media': media_id} or
                [{'owner': owner_id_1, 'media': media_id_1}, {'owner': owner_id_2, 'media': media_id_2}] (Attachments)
            :param videos: The format is like the photos (Attachments)
            :param audios: The format is like the photos (Attachments)
            :param docs: The format is like the photos (Attachments)
            :return:
            """

            if owner_id is None:
                return {'result': 'error', 'data': '"owner_id" is empty"'}
            elif post_id is None:
                return {'result': 'error', 'data': '"post_id" is empty"'}

            attachments = ''
            for el in (photos, 'photo'), (videos, 'video'), (audios, 'audio'), (docs, 'doc'):
                ans = self.attachment_create(el)
                if 'Error' in ans:
                    return {'result': 'error', 'data': ans}
                else:
                    attachments += ans

            if attachments:
                attachments = attachments[:-1]

            if attachments is None and message is None:
                return {'result': 'error', 'data': '"attachments" and "message" are empty'}

            response = vk_session().post(
                'wall.createComment',
                params={
                    'owner_id': owner_id,
                    'post_id': post_id,
                    'from_group': 1 if from_group else 0,
                    'message': message,
                    'reply_to_comment': reply_to_comment,
                    'sticker_id': sticker_id,
                    'guid': guid,
                    'attachments': attachments,
                }).json()

            if 'error' in response:
                return {
                    'result': 'error',
                    'data': f'Code: {response.get("error").get("error_code")}. {response.get("error").get("error_msg")}'
                }
            else:
                return {'result': 'success', 'data': response.get('response')}

        def delete_post(self, owner_id: str = None, post_id: str = None) -> dict:

            """
            Delete post
            https://dev.vk.com/ru/method/wall.delete
            :param owner_id: REQUIRED. The ID of the user or community. The community ID must start with a "-" (str)
            :param post_id: REQUIRED. post_id (str)
            :return:
            """

            if owner_id is None:
                return {'result': 'error', 'data': '"owner_id" is empty"'}
            elif post_id is None:
                return {'result': 'error', 'data': '"post_id" is empty"'}

            response = vk_session().post(
                'wall.delete',
                params={
                    'owner_id': owner_id,
                    'post_id': post_id
                }).json()

            if not response.get('response'):
                return {'result': 'error', 'data': f'The post has not been deleted'}
            else:
                return {'result': 'success', 'data': 'Post was successfully deleted'}

        def delete_comment(self, owner_id: str = None, comment_id: str = None) -> dict:

            """
            Delete post
            https://dev.vk.com/ru/method/wall.deleteComment
            :param owner_id: REQUIRED. The ID of the user or community. The community ID must start with a "-" (str)
            :param comment_id: REQUIRED. Comment ID (str)
            :return:
            """

            if owner_id is None:
                return {'result': 'error', 'data': '"owner_id" is empty"'}
            elif comment_id is None:
                return {'result': 'error', 'data': '"comment_id" is empty"'}

            response = vk_session().post(
                'wall.deleteComment',
                params={
                    'owner_id': owner_id,
                    'comment_id': comment_id
                }).json()

            if not response.get('response'):
                return {'result': 'error', 'data': f'Comment has not been deleted'}
            else:
                return {'result': 'success', 'data': 'Comment was successfully deleted'}

        def edit(self, owner_id: str = None, post_id: str = None, friends_only: bool = False, message: str = None,
                 services: str = None, signed: bool = False, publish_date: datetime = None, lat: int = None,
                 long: int = None, place_id: str = None, guid: str = None, mark_as_ads: bool = False,
                 close_comments: bool = False, donut_paid_duration: int = None, mute_notifications: bool = False,
                 copyright: str = None, photos: dict | list[dict] = None, videos: dict | list[dict] = None,
                 audios: dict | list[dict] = None, docs: dict | list[dict] = None, pages: dict | list[dict] = None,
                 notes: dict | list[dict] = None, polls: dict | list[dict] = None, albums: dict | list[dict] = None,
                 markets: dict | list[dict] = None, market_albums: dict | list[dict] = None,
                 audio_playlists: dict | list[dict] = None) -> dict:

            """
            Edit an entry on the wall
            https://dev.vk.com/ru/method/wall.edit
            :param owner_id: REQUIRED. The ID of the user or community on whose wall you want to post the post.
                The community ID must start with a "-" (str)
            :param post_id: REQUIRED. Post ID (str)
            :param friends_only: Information about who can access the record. Possible values:
                True — the record is available only to friends.
                False — the record is available to all users. The value is used by default.
            :param message: The text of the message. REQUIRED parameter if the attachments parameter is not specified.
            :param services: A list of services or sites to export the record to, if the user has filled in the
                appropriate setting.
            :param signed: Information about whether to add a signature to an entry posted on behalf of the community.
                The parameter is taken into account only when posting an entry on the community wall and specifying the
                from_group parameter. Possible values:
                True — add a signature (the name of the user who suggested the entry).
                False — do not add a signature. The value is used by default.
            :param publish_date: Date and time of publication of the record (Unix Timestamp). The publication of the
                record will be postponed until the specified time.
            :param lat: Geographic latitude in degrees. The range of values is from -90 to 90. (int)
            :param long: Geographical longitude in degrees. The range of values is from -180 to 180. (int)
            :param place_id: The ID of the location where the user is marked. (str)
            :param guid: A unique identifier designed to prevent the same record from being sent again. Valid for one
                hour. (str)
            :param mark_as_ads: Information about whether to add a mark is an advertisement for an entry posted on
                behalf of the community. The parameter is taken into account only when posting an entry on the community
                wall and specifying the from_group parameter. Possible values:
                True — add a mark. The value is used by default.
                False — do not add a mark.
            :param close_comments:
                Information about whether to enable the ability to comment on the record. Possible values:
                True — comments on the post are disabled.
                False — comments on the entry are included. The value is used by default.
            :param donut_paid_duration: The period of time during which the recording will be available only to don —
                paid subscribers of VK Donut. Possible values:
                -1 — exclusively for dons.
                86400 — for 1 day.
                172800 — for 2 days.
                259200 — for 3 days.
                345600 — for 4 days.
                432000 — for 5 days.
                518400 — for 6 days.
                604800 — for 7 days.
            :param mute_notifications: Information about whether notifications are enabled for the publication of the
                record.
                True — Recording notifications are disabled.
                False — notifications for recording are enabled. The value is used by default.
            :param copyright: The source of the material. External and internal links are supported. (str)
            :param photos: Add photos to the post. Example: {'owner': owner_id, 'media': media_id} or
                [{'owner': owner_id_1, 'media': media_id_1}, {'owner': owner_id_2, 'media': media_id_2}] (Attachments)
            :param videos: The format is like the photos (Attachments)
            :param audios: The format is like the photos (Attachments)
            :param docs: The format is like the photos (Attachments)
            :param pages: The format is like the photos (Attachments)
            :param notes: The format is like the photos (Attachments)
            :param polls: The format is like the photos (Attachments)
            :param albums: The format is like the photos (Attachments)
            :param markets: The format is like the photos (Attachments)
            :param market_albums: The format is like the photos (Attachments)
            :param audio_playlists: The format is like the photos (Attachments)
            :return:
            """

            if owner_id is None:
                return {'result': 'error', 'data': '"owner_id" is empty"'}

            attachments = ''
            for el in ((photos, 'photo'), (videos, 'video'), (audios, 'audio'), (docs, 'doc'), (pages, 'page'),
                       (notes, 'note'), (polls, 'poll'), (albums, 'album'), (markets, 'market'),
                       (market_albums, 'market_albums'), (audio_playlists, 'audio_playlist')):
                ans = self.attachment_create(el)
                if 'Error' in ans:
                    return {'result': 'error', 'data': ans}
                else:
                    attachments += ans

            if attachments:
                attachments = attachments[:-1]

            if attachments is None and message is None:
                return {'result': 'error', 'data': '"attachments" and "message" are empty'}

            # if attachments and message:
            #     return {'result': 'error', 'data': '"attachments" and "message" are not empty. Choose one value'}

            if publish_date:
                publish_date = publish_date.timestamp()

            response = vk_session().post(
                'wall.edit',
                params={
                    'owner_id': owner_id,
                    'post_id': post_id,
                    'friends_only': 1 if friends_only else 0,
                    'message': message,
                    'services': services,
                    'signed': 1 if signed else 0,
                    'publish_date': publish_date,
                    'lat': lat,
                    'long': long,
                    'place_id': place_id,
                    'guid': guid,
                    'mark_as_ads': 1 if mark_as_ads else 0,
                    'close_comments': 1 if close_comments else 0,
                    'donut_paid_duration': donut_paid_duration,
                    'mute_notifications': 1 if mute_notifications else 0,
                    'copyright': copyright,
                    'attachments': attachments,
                }).json()

            if 'error' in response:
                return {
                    'result': 'error',
                    'data': f'Code: {response.get("error").get("error_code")}. {response.get("error").get("error_msg")}'
                }
            else:
                return {'result': 'success', 'data': response.get('response')}

        def edit_comment(self, owner_id: str = None, comment_id: str = None, message: str = None,
                         photos: dict | list[dict] = None, videos: dict | list[dict] = None,
                         audios: dict | list[dict] = None, docs: dict | list[dict] = None) -> dict:

            """
            Edit a new comment
            https://dev.vk.com/ru/method/wall.editComment
            :param owner_id: REQUIRED. The ID of the user or community. The community ID must start with a "-" (str)
            :param comment_id: Comment ID (str)
            :param message: The text of the comment. Required parameter if the attachments parameter is not
                passed.
            :param photos: photos: Add photos to the post. Example: {'owner': owner_id, 'media': media_id} or
                [{'owner': owner_id_1, 'media': media_id_1}, {'owner': owner_id_2, 'media': media_id_2}] (Attachments)
            :param videos: The format is like the photos (Attachments)
            :param audios: The format is like the photos (Attachments)
            :param docs: The format is like the photos (Attachments)
            :return:
            """

            if owner_id is None:
                return {'result': 'error', 'data': '"owner_id" is empty"'}
            elif comment_id is None:
                return {'result': 'error', 'data': '"comment_id" is empty"'}

            attachments = ''
            for el in (photos, 'photo'), (videos, 'video'), (audios, 'audio'), (docs, 'doc'):
                ans = self.attachment_create(el)
                if 'Error' in ans:
                    return {'result': 'error', 'data': ans}
                else:
                    attachments += ans

            if attachments:
                attachments = attachments[:-1]

            if attachments is None and message is None:
                return {'result': 'error', 'data': '"attachments" and "message" are empty'}

            response = vk_session().post(
                'wall.editComment',
                params={
                    'owner_id': owner_id,
                    'comment_id': comment_id,
                    'message': message,
                    'attachments': attachments,
                }).json()

            if not response.get('response'):
                return {'result': 'error', 'data': f'Comment has not been edited'}
            else:
                return {'result': 'success', 'data': 'Comment was successfully edited'}

        def get(self, owner_id: str = None, count: int = 20, filter_: str = 'all', extended: bool = False) -> dict:

            """
            Getting user or group records
            https://dev.vk.com/ru/method/wall.get
            :param owner_id: REQUIRED. The ID of the user or community. The community ID must start with a "-" (str)
            :param count: Count of records (int) default 20
            :param filter_: Determines which types of wall entries need to be retrieved. Possible values:
                suggests — suggested entries on the community wall (available only when calling with the transfer of access_token);
                postponed — deferred entries (available only when calling with the transfer of access_token);
                owner — records of the wall owner;
                others — entries are not from the owner of the wall;
                all — all entries on the wall (owner + others)
                donut — entries for paid subscribers on the community wall. Learn more about VK Don't API
                By default: all.
            :param extended: True — additional profiles and groups fields containing information about users and
                communities will be returned in the response. By default: False.
            :return:
            """

            if owner_id is None:
                return {'result': 'error', 'data': '"owner_id" is empty"'}

            response = vk_session().post(
                'wall.get',
                params={
                    'owner_id': owner_id,
                    'count': count,
                    'filter': filter_,
                    'extended': 1 if extended else 0,
                }).json()

            if 'error' in response:
                return {
                    'result': 'error',
                    'data': f'Code: {response.get("error").get("error_code")}. {response.get("error").get("error_msg")}'
                }
            else:
                return {'result': 'success', 'data': response.get('response')}

        def get_by_ids(self, posts_ids: str | list | dict = None, extended: bool = False,
                       copy_history_depth: int = None) -> dict:

            """
            Getting posts by ids
            https://dev.vk.com/ru/method/wall.getById
            :param posts_ids: Comma-separated identifiers that represent the IDs of the wall owners and the IDs of the
                wall entries themselves, which are underlined. Maximum of 100 IDs. Examples:
                1) dict: {group_id/user_id: post_id, group_id2/user_id3: post_id2...}
                2) list: [-123456_123456, 123456_123456... / (group_id/user_id)_(post_id)]
                3) str: -123456_123456 / (group_id/user_id)_(post_id)
            :param extended: True — additional profiles and groups fields containing information about users and
                communities will be returned in the response. By default: False.
            :param copy_history_depth: Defines the size of the copy_history array returned in the response if the record
                is a repost of a record from another wall. For example, copy_history_depth=1 — copy_history will
                contain one element with information about the record, the direct repost of which is the current one.
                copy_history_depth=2 — copy_history will contain two elements, information about the record is added,
                the repost of which is the first element, and so on (provided that the hierarchy of reposts of the
                required depth exists for the current record).
            :return:
            """

            if posts_ids is None:
                return {'result': 'error', 'data': '"posts_ids" is empty"'}

            if isinstance(posts_ids, str):
                posts_ids = [posts_ids]
            elif isinstance(posts_ids, dict):
                posts_ids = [f'{key}_{item}' for key, item in posts_ids.items()]

            response = vk_session().post(
                'wall.getById',
                params={
                    'posts': ','.join(posts_ids),
                    'extended': 1 if extended else 0,
                    'copy_history_depth': copy_history_depth
                }).json()

            if 'error' in response:
                return {
                    'result': 'error',
                    'data': f'Code: {response.get("error").get("error_code")}. {response.get("error").get("error_msg")}'
                }
            else:
                return {'result': 'success', 'data': response.get('response')}

        def get_comment(self, owner_id: str = None, comment_id: str = None, extended: bool = False) -> dict:

            """
            Get info about comment by comment id
            https://dev.vk.com/ru/method/wall.getComment
            :param owner_id: REQUIRED. The ID of the user or community. The community ID must start with a "-" (str)
            :param comment_id: REQUIRED. Comment id (str)
            :param extended: True — additional profiles and groups fields containing information about users and
                communities will be returned in the response. By default: False.
            :return:
            """

            if owner_id is None:
                return {'result': 'error', 'data': '"owner_id" is empty"'}
            elif comment_id is None:
                return {'result': 'error', 'data': '"comment_id" is empty"'}

            response = vk_session().post(
                'wall.getComment',
                params={
                    'owner_id': owner_id,
                    'comment_id': comment_id,
                    'extended': 1 if extended else 0,
                }).json()

            if 'error' in response:
                return {
                    'result': 'error',
                    'data': f'Code: {response.get("error").get("error_code")}. {response.get("error").get("error_msg")}'
                }
            else:
                return {'result': 'success', 'data': response.get('response')}

        def get_comments(self, owner_id: str = None, post_id: str = None, need_likes: bool = False,
                         start_comment_id: str = None, count: int = 10, sort: str = None, preview_length: int = None,
                         extended: bool = False, comment_id: str = None) -> dict:

            """
            Getting comments in post
            https://dev.vk.com/ru/method/wall.getComments
            :param owner_id: REQUIRED. The ID of the user or community. The community ID must start with a "-" (str)
            :param post_id: REQUIRED. Post ID (str)
            :param need_likes: True — return information about likes. default False
            :param start_comment_id: ID of the comment to return the list from.
            :param count: The number of comments to receive. Default: 10, maximum value: 100.
            :param sort: The order in which comments are sorted. Possible values:
                ASC — from old to new;
                desc — from new to old.
            :param preview_length: The number of characters to trim the comment text by. Specify 0 if you don't want
                to crop the text
            :param extended: True — additional profiles and groups fields containing information about users and
                communities will be returned in the response. By default: False.
            :param comment_id: Id of the comment whose branch you want to get.
            :return:
            """

            if owner_id is None:
                return {'result': 'error', 'data': '"owner_id" is empty"'}
            elif post_id is None:
                return {'result': 'error', 'data': '"post_id" is empty"'}

            response = vk_session().post(
                'wall.getComments',
                params={
                    'owner_id': owner_id,
                    'post_id': post_id,
                    'need_likes': 1 if need_likes else 0,
                    'start_comment_id': start_comment_id,
                    'count': count,
                    'sort': sort,
                    'preview_length': preview_length,
                    'comment_id': comment_id,
                    'extended': 1 if extended else 0,
                }).json()

            if 'error' in response:
                return {
                    'result': 'error',
                    'data': f'Code: {response.get("error").get("error_code")}. {response.get("error").get("error_msg")}'
                }
            else:
                return {'result': 'success', 'data': response.get('response')}

        def get_reposts(self, owner_id: str = None, post_id: str = None, count: int = 10) -> dict:

            """
            Getting comments in post
            https://dev.vk.com/ru/method/wall.getReposts
            :param owner_id: REQUIRED. The ID of the user or community. The community ID must start with a "-" (str)
            :param post_id: REQUIRED. Post ID (str)
            :param count: The number of comments to receive. Default: 10, maximum value: 100.
            :return:
            """

            if owner_id is None:
                return {'result': 'error', 'data': '"owner_id" is empty"'}
            elif post_id is None:
                return {'result': 'error', 'data': '"post_id" is empty"'}

            response = vk_session().post(
                'wall.getReposts',
                params={
                    'owner_id': owner_id,
                    'post_id': post_id,
                    'count': count,
                }).json()

            if 'error' in response:
                return {
                    'result': 'error',
                    'data': f'Code: {response.get("error").get("error_code")}. {response.get("error").get("error_msg")}'
                }
            else:
                return {'result': 'success', 'data': response.get('response')}

        def parse_attached_link(self, links: str | list = None, extended: bool = False, name_case: str = None,) -> dict:

            """
            Accepts links as input and returns additional information that can be used to create snippets when posting
                links on the user's wall and other resources. For example, a user wants to post a link to a website or
                video on their wall. Publishing a link in text form does not look attractive. In the modern world, site
                visitors expect to see a snippet with a title, image and a short description. This method helps to get
                additional information for creating such a snippet.
                https://dev.vk.com/ru/method/wall.parseAttachedLink
            :param links: REQUIRED. An array containing links. For example:
                1) list: ['https://my-site.ru', 'https://my-site-2.ru']
                2) str: 'https://my-site.ru'
            :param extended: True — additional profiles and groups fields containing information about users and
                communities will be returned in the response. By default: False.
            :param name_case: An indication of the case of the owner's name that should be used in the response.
                Nominative - 'nom'; Genitive - 'gen'; The dative - 'dat'; Accusative - 'acc'; Creative - 'ins';
                Prepositional - 'abl'. Default 'nom'
            :return:
            """

            if links is None:
                return {'result': 'error', 'data': '"links" is empty"'}

            if isinstance(links, str):
                links = [links]

            response = vk_session().post(
                'wall.getReposts',
                params={
                    'links': links,
                    'extended': extended,
                    'name_case': name_case,
                }).json()

            if 'error' in response:
                return {
                    'result': 'error',
                    'data': f'Code: {response.get("error").get("error_code")}. {response.get("error").get("error_msg")}'
                }
            else:
                return {'result': 'success', 'data': response.get('response')}

vk_sess = ApiVk()
# vk_sess.add DONT WORK NOW!
# logger.debug(vk_sess.add(group_id='224804432', name='Example', description='Example description', category_id="1"))


# logger.debug(vk_sess.Wall().post(
#     owner_id=os.getenv('GROUP_ID'),
#     photos={'owner': os.getenv('GROUP_ID'), 'media': '456239018'},
#     from_group=True,
# ))
# logger.debug(vk_sess.Wall().pin(owner_id=os.getenv('GROUP_ID'), post_id='9'))
# logger.debug(vk_sess.Wall().unpin(owner_id=os.getenv('GROUP_ID'), post_id='9'))
# logger.debug(vk_sess.Wall().report_comment(owner_id=os.getenv('GROUP_ID'), comment_id='', reason=0))
# logger.debug(vk_sess.Wall().report_post(owner_id=os.getenv('GROUP_ID'), comment_id='', reason=0))
# logger.debug(vk_sess.Wall().repost(object_id='wall-52620949_4773386', message='Example', group_id=os.getenv('GROUP_ID')))
# logger.debug(vk_sess.Wall().restore_post(owner_id=os.getenv('GROUP_ID'), post_id='25'))
# logger.debug(vk_sess.Wall().restore_comment(owner_id=os.getenv('GROUP_ID'), comment_id=''))
# logger.debug(vk_sess.Wall().check_copyright_link(link=''))
# logger.debug(vk_sess.Wall().close_comment_on_post(owner_id=os.getenv('GROUP_ID'), post_id='24'))
# logger.debug(vk_sess.Wall().open_comment_on_post(owner_id=os.getenv('GROUP_ID'), post_id='24'))
# logger.debug(vk_sess.Wall().create_comment(owner_id=os.getenv('GROUP_ID'), post_id='23', reply_to_comment='26', photos={'owner': os.getenv('GROUP_ID'), 'media': '456239018'}))
# logger.debug(vk_sess.Wall().delete_post(owner_id=os.getenv('GROUP_ID'), post_id='22'))
# logger.debug(vk_sess.Wall().delete_comment(owner_id=os.getenv('GROUP_ID'), comment_id='28'))
# logger.debug(vk_sess.Wall().edit(
#     owner_id=os.getenv('GROUP_ID'),
#     post_id='21',
#     message='LALALALLALA',
# ))
# logger.debug(vk_sess.Wall().edit_comment(owner_id=os.getenv('GROUP_ID'), comment_id='26', message='Hello 123'))
# logger.debug(vk_sess.Wall().get(owner_id=os.getenv('GROUP_ID')))
# logger.debug(vk_sess.Wall().get(owner_id=os.getenv('GROUP_ID')))
# logger.debug(vk_sess.Wall().get_by_ids(posts_ids={'-226454606': '21'}))
# logger.debug(vk_sess.Wall().get_comment(owner_id=os.getenv('GROUP_ID'), comment_id='26'))
# logger.debug(vk_sess.Wall().get_comments(owner_id=os.getenv('GROUP_ID'), post_id='23'))
# logger.debug(vk_sess.Wall().get_reposts(owner_id=os.getenv('GROUP_ID'), post_id='23'))
# logger.debug(vk_sess.Wall().parse_attached_link(links='https://vk.com/video?z=video-211437014_456243438%2Fpl_cat_trends'))


# WORK_URL!!! = 'https://oauth.vk.com/authorize?client_id=51985053&redirect_url=https://api.vk.com/blank.html&scope=notify,friends,photos,audio,video,stories,pages,menu,status,notes,messages,ads,docs,groups,notifications,stats,email,market,phone_number,offline,wall&response_type=token'

