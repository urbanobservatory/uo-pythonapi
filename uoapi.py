#!/usr/bin/env python3
# ~ coding: utf-8 ~
#
# Python module to interface with the Urban Observatory API (initially for the Urban Sciences Building)
#
import urllib.parse
import requests
import datetime
import logging

log = logging.getLogger(__name__)

"""
List of example API requests from Luke's 17 December email:
 
Paginated list of entities
    https://api.usb.urbanobservatory.ac.uk/api/v0.1/sensors/entity?page=1
Single entity by its UUID
    https://api.usb.urbanobservatory.ac.uk/api/v0.1/sensors/entity/47d42c59-0a33-4267-9a33-e64f5d11afc9
Single feed by its UUID
    https://api.usb.urbanobservatory.ac.uk/api/v0.1/sensors/feed/f163a36e-e65a-4739-911d-9b909eccb83e
Summary list (non-paginated) of all entities and their feeds
    https://api.usb.urbanobservatory.ac.uk/api/v0.1/sensors/summary
Single timeseries by its UUID
    https://api.usb.urbanobservatory.ac.uk/api/v0.1/sensors/timeseries/ba37dd32-68b2-45f5-aeaf-be727d1812db
Wind speed during the last 24 hours
    https://api.usb.urbanobservatory.ac.uk/api/v0.1/sensors/timeseries/bd0cc46d-ba2e-4924-a66e-b032d7ca33a5/historic
Outside air temperature yesterday
    https://api.usb.urbanobservatory.ac.uk/api/v0.1/sensors/timeseries/cc567a16-c3e7-4ee5-bbd5-841644d825dd/historic?startTime=2017-12-16T00:00:00Z&endTime=2017-12-16T23:59:59Z
 
"""


class APIRequestException(Exception):
    """
    An exception class indicating something went wrong with an API Request
    """
    pass


class UrbanAPI:
    # API version to hit on server
    api_version = 0.1
    base_url = "https://api.usb.urbanobservatory.ac.uk/api/v{}/"

    REST_METHODS = {
        'entities': "sensors/entity",
        'feed': "sensors/feed",
        'timeseries': "sensors/timeseries",
        'summary': "sensors/summary"
    }

    def __init__(self, api_version=0.1, base_url=None):
        """
        Constructor
        :param api_version:
        :param base_url:
        """

        self.api_version = api_version

        if base_url is not None:
            self.base_url = base_url

        self.base_url = self.base_url.format(self.api_version)

    def create_method(self, method, path):
        """
        Add or override a method in the REST_METHODS dict
        :param method:
        :param path:
        :return:
        """
        self.REST_METHODS[method] = path

    def get_url(self, method, path_components=[], params=None):
        """
        Construct and return a URL for the REST method provided
        :param method:          Method to look up from REST_METHODS
        :param path_components: URL path to further append to the URL before params (e.g. uuid)
        :param params:          dict containing URL parameters
        :return:                dict object parsed from returned JSON
        """
        url = urllib.parse.urljoin(self.base_url, UrbanAPI.REST_METHODS[method]) + '/'  # Trailing / hack for urljoin
        for p in path_components:
            url = urllib.parse.urljoin(url, p + '/')

        if params is not None:
            url = "?".join((url, urllib.parse.urlencode(params)))

        log.debug(url)
        return url

    def resolve(self, url, expected_response=200):
        """
        Resolve a URL using the requests library
        :param url:               URL to resolve
        :param expected_response: Status code indicating success
        :return:
        """
        result = requests.get(url) 

        if result.status_code == expected_response:
            return result.json()
        else:
            raise APIRequestException("Status: {0}\n\n{1}".format(result.status_code, result.content))

    def get_entities(self, page):
        """
        Grab and return all entities for the provided page number
        E.g. https://api.usb.urbanobservatory.ac.uk/api/v0.1/sensors/entity?page=1
        :param page:
        :return:
        """
        url = self.get_url('entities', params={'page': page})
        return self.resolve(url)

    def get_single_entity(self, entity_uuid):
        """
        Get a single entity by its UUID
            https://api.usb.urbanobservatory.ac.uk/api/v0.1/sensors/entity/47d42c59-0a33-4267-9a33-e64f5d11afc9
        :param entity_uuid:
        :return:
        """
        url = self.get_url('entities', path_components=[entity_uuid])
        return self.resolve(url)

    def get_feed(self, entity_uuid):
        """
        Get the feed for an entity by UUID
        :param entity_uuid:
        :return:
        """
        url = self.get_url('feed',  path_components=[entity_uuid])
        return self.resolve(url)

    def get_timeseries(self, entity_uuid, start_time=None, end_time=None, last_24=False):
        """
        Get time series data for an entity by UUID
        Takes optional parameters for last 24 hours, or specific time window:
            ?startTime=2017-12-16T00:00:00Z&endTime=2017-12-16T23:59:59Z
        :param entity_uuid:
        :param last_24:
        :param start_time:
        :param end_time:
        :return:
        """
        if start_time is not None and end_time is not None:
            # Support datetime objects
            if type(start_time) is datetime.datetime:
                start_time = start_time.replace(microsecond=0).isoformat()

            if type(end_time) is datetime.datetime:
                end_time = end_time.isoformat()

            if type(start_time) is not str and type(end_time) is not str:
                raise TypeError("Unrecognised type for date argument")

            url = self.get_url('timeseries', path_components=[entity_uuid, 'historic'],
                               params={"startTime": start_time, "endTime": end_time})

        elif last_24:
            url = self.get_url('timeseries',  path_components=[entity_uuid, 'historic'])

        else:
            url = self.get_url('timeseries',  path_components=[entity_uuid])
        return self.resolve(url)

    def get_summary(self):
        """
        Summary list (non-paginated) of all entities and their feeds
            https://api.usb.urbanobservatory.ac.uk/api/v0.1/sensors/summary

        :return: Summary
        """
        url = self.get_url('summary')
        return self.resolve(url)

    def test(self):
        """
        Run tests and return success, or throw exceptions

        :return: success
        """

        #
        log.info("Test: get multiple entities")
        res = self.get_entities(0)
        assert('pagination' in res)
        assert('items' in res)
        log.info("PASS\n")

        #
        log.info("Test get single entity")
        test_uuid = "47d42c59-0a33-4267-9a33-e64f5d11afc9"
        res = self.get_single_entity(test_uuid)
        assert('entityId' in res)
        assert(res['entityId'] == test_uuid)
        assert('meta' in res)
        log.info("PASS\n")

        #
        log.info("Test: get feed from single entity")
        test_uuid = "f163a36e-e65a-4739-911d-9b909eccb83e"
        res = self.get_feed(test_uuid)
        assert('feedId' in res)
        assert(res['feedId'] == test_uuid)
        assert('metric' in res)
        assert('meta' in res)
        log.info("PASS\n")

        #
        log.info("Test: get summary data")
        res = self.get_summary()
        assert(type(res) is list)
        assert(len(res) > 0)
        assert('entityId' in res[0])
        log.info("PASS\n")

        #
        log.info("Test: get timeseries data from single entity using datetime objects")
        test_uuid = "bd0cc46d-ba2e-4924-a66e-b032d7ca33a5"
        res = self.get_timeseries(test_uuid,
                                  start_time=datetime.datetime(2018, 1, 20, 0),
                                  end_time=datetime.datetime(2018, 1, 20, 1))
        assert('timeseries' in res)
        assert('timeseriesId' in res['timeseries'])
        assert(res['timeseries']['timeseriesId'] == test_uuid)
        log.info("PASS\n")

        #
        log.info("Test: get timeseries data from single entity using strings")
        test_uuid = "bd0cc46d-ba2e-4924-a66e-b032d7ca33a5"
        res = self.get_timeseries(test_uuid,
                                  start_time="2018-01-20T00:00:00Z",
                                  end_time="2018-01-20T01:00:00Z")
        assert('timeseries' in res)
        assert(res['timeseries']['timeseriesId'] == test_uuid)
        log.info("PASS\n")

        return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    urbs = UrbanAPI()
    urbs.test()

