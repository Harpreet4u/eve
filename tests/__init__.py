# -*- coding: utf-8 -*-

import unittest
import eve
import string
import random
import os
import simplejson as json
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId
from test_settings import (
    MONGO_PASSWORD,
    MONGO_DBNAME,
    MONGO_USERNAME,
    DOMAIN,
    MONGO_HOST,
    MONGO_PORT,
)
from eve import ISSUES, ETAG
from eve.utils import date_to_str

try:
    from urlparse import parse_qs, urlparse
except ImportError:
    from urllib.parse import parse_qs, urlparse


class ValueStack(object):
    """
    Descriptor to store multiple assignments in an attribute.

    Due to the multiple self.app = assignments in tests, it is difficult to
    keep track by hand of the applications created in order to close their
    database connections. This descriptor helps with it.
    """

    def __init__(self, on_delete):
        """
        :param on_delete: Action to execute when the attribute is deleted
        """
        self.elements = []
        self.on_delete = on_delete

    def __set__(self, obj, val):
        self.elements.append(val)

    def __get__(self, obj, objtype):
        return self.elements[-1] if self.elements else None

    def __delete__(self, obj):
        for item in self.elements:
            self.on_delete(item)
        self.elements = []


def close_pymongo_connection(app):
    """
    Close the pymongo connection in an eve/flask app
    """
    if "pymongo" not in app.extensions:
        return
    del app.extensions["pymongo"]
    del app.media


class TestMinimal(unittest.TestCase):
    """ Start the building of the tests for an application
    based on Eve by subclassing this class and provide proper settings
    using :func:`setUp()`
    """

    app = ValueStack(close_pymongo_connection)

    def setUp(self, settings_file=None, url_converters=None):
        """ Prepare the test fixture

        :param settings_file: the name of the settings file.  Defaults
                              to `eve/tests/test_settings.py`.
        """
        self.this_directory = os.path.dirname(os.path.realpath(__file__))
        if settings_file is None:
            # Load the settings file, using a robust path
            settings_file = os.path.join(self.this_directory, "test_settings.py")

        self.connection = None
        self.known_resource_count = 101
        self.setupDB()

        self.settings_file = settings_file
        self.app = eve.Eve(settings=self.settings_file, url_converters=url_converters)

        self.test_client = self.app.test_client()

        self.domain = self.app.config["DOMAIN"]

    def tearDown(self):
        del self.app
        self.dropDB()

    def assert200(self, status):
        self.assertEqual(status, 200)

    def assert201(self, status):
        self.assertEqual(status, 201)

    def assert204(self, status):
        self.assertEqual(status, 204)

    def assert301(self, status):
        self.assertEqual(status, 301)

    def assert304(self, status):
        self.assertEqual(status, 304)

    def assert404(self, status):
        self.assertEqual(status, 404)

    def assert422(self, status):
        self.assertEqual(status, 422)

    def get(self, resource, query="", item=None):
        if resource in self.domain:
            resource = self.domain[resource]["url"]
        if item:
            request = "/%s/%s%s" % (resource, item, query)
        else:
            request = "/%s%s" % (resource, query)

        r = self.test_client.get(request)
        return self.parse_response(r)

    def post(self, url, data, headers=None, content_type="application/json"):
        if headers is None:
            headers = []
        headers.append(("Content-Type", content_type))
        r = self.test_client.post(url, data=json.dumps(data), headers=headers)
        return self.parse_response(r)

    def put(self, url, data, headers=None):
        if headers is None:
            headers = []
        headers.append(("Content-Type", "application/json"))
        r = self.test_client.put(url, data=json.dumps(data), headers=headers)
        return self.parse_response(r)

    def patch(self, url, data, headers=None):
        if headers is None:
            headers = []
        headers.append(("Content-Type", "application/json"))
        r = self.test_client.patch(url, data=json.dumps(data), headers=headers)
        return self.parse_response(r)

    def delete(self, url, headers=None):
        r = self.test_client.delete(url, headers=headers)
        return self.parse_response(r)

    def parse_response(self, r):
        try:
            v = json.loads(r.get_data())
        except json.JSONDecodeError:
            v = None
        return v, r.status_code

    def assertValidationErrorStatus(self, status):
        self.assertEqual(status, self.app.config.get("VALIDATION_ERROR_STATUS"))

    def assertValidationError(self, response, matches):
        self.assertTrue(eve.STATUS in response)
        self.assertTrue(eve.STATUS_ERR in response[eve.STATUS])
        self.assertTrue(ISSUES in response)
        issues = response[ISSUES]
        self.assertTrue(len(issues))

        for k, v in matches.items():
            self.assertTrue(k in issues)
            self.assertTrue(v in issues[k])

    def assertExpires(self, resource):
        # TODO if we ever get access to response.date (it is None), compare
        # it with Expires
        r = self.test_client.get(resource)

        expires = r.headers.get("Expires")
        self.assertTrue(expires is not None)

    def assertCacheControl(self, resource):
        r = self.test_client.get(resource)

        cache_control = r.headers.get("Cache-Control")
        self.assertTrue(cache_control is not None)
        self.assertEqual(
            cache_control, self.domain[self.known_resource]["cache_control"]
        )

    def assertIfModifiedSince(self, resource):
        r = self.test_client.get(resource)

        last_modified = r.headers.get("Last-Modified")
        self.assertTrue(last_modified is not None)
        r = self.test_client.get(
            resource, headers=[("If-Modified-Since", last_modified)]
        )
        self.assert304(r.status_code)
        self.assertTrue(not r.get_data())

    def assertItem(self, item, resource):
        self.assertEqual(type(item), dict)

        updated_on = item.get(self.app.config["LAST_UPDATED"])
        self.assertTrue(updated_on is not None)
        try:
            datetime.strptime(updated_on, self.app.config["DATE_FORMAT"])
        except Exception as e:
            self.fail(
                'Cannot convert field "%s" to datetime: %s'
                % (self.app.config["LAST_UPDATED"], e)
            )

        created_on = item.get(self.app.config["DATE_CREATED"])
        self.assertTrue(updated_on is not None)
        try:
            datetime.strptime(created_on, self.app.config["DATE_FORMAT"])
        except Exception as e:
            self.fail(
                'Cannot convert field "%s" to datetime: %s'
                % (self.app.config["DATE_CREATED"], e)
            )

        link = item.get("_links")
        _id = item.get(self.domain[resource]["id_field"])
        self.assertItemLink(link, _id)

    def assertPagination(self, response, page, total, max_results):
        p_key, mr_key = (
            self.app.config["QUERY_PAGE"],
            self.app.config["QUERY_MAX_RESULTS"],
        )
        self.assertTrue(self.app.config["META"] in response)
        meta = response.get(self.app.config["META"])
        self.assertTrue(p_key in meta)
        self.assertTrue(mr_key in meta)
        self.assertTrue("total" in meta)
        self.assertEqual(meta[p_key], page)
        self.assertEqual(meta[mr_key], max_results)
        self.assertEqual(meta["total"], total)

    def assertHomeLink(self, links):
        self.assertTrue("parent" in links)
        link = links["parent"]
        self.assertTrue("title" in link)
        self.assertTrue("href" in link)
        self.assertEqual("home", link["title"])
        self.assertEqual("/", link["href"])

    def assertResourceLink(self, links, resource):
        self.assertTrue("self" in links)
        link = links["self"]
        self.assertTrue("title" in link)
        self.assertTrue("href" in link)
        url = self.domain[resource]["url"]
        self.assertEqual(url, link["title"])
        self.assertEqual("%s" % url, link["href"])

    def assertCollectionLink(self, links, resource):
        self.assertTrue("collection" in links)
        link = links["collection"]
        self.assertTrue("title" in link)
        self.assertTrue("href" in link)
        url = self.domain[resource]["url"]
        self.assertEqual(url, link["title"])
        self.assertEqual("%s" % url, link["href"])

    def assertNextLink(self, links, page):
        self.assertTrue("next" in links)
        link = links["next"]
        self.assertTrue("title" in link)
        self.assertTrue("href" in link)
        self.assertEqual("next page", link["title"])
        self.assertTrue("%s=%d" % (self.app.config["QUERY_PAGE"], page) in link["href"])

    def assertPrevLink(self, links, page):
        self.assertTrue("prev" in links)
        link = links["prev"]
        self.assertTrue("title" in link)
        self.assertTrue("href" in link)
        self.assertEqual("previous page", link["title"])
        if page > 1:
            self.assertTrue(
                "%s=%d" % (self.app.config["QUERY_PAGE"], page) in link["href"]
            )

    def assertItemLink(self, links, item_id):
        self.assertTrue("self" in links)
        link = links["self"]
        # TODO we are too deep here to get a hold of the due title. Should fix.
        self.assertTrue("title" in link)
        self.assertTrue("href" in link)
        self.assertTrue("/%s" % item_id in link["href"])

    def assertLastLink(self, links, page):
        if page:
            self.assertTrue("last" in links)
            link = links["last"]
            self.assertTrue("title" in link)
            self.assertTrue("href" in link)
            self.assertEqual("last page", link["title"])
            self.assertTrue(
                "%s=%d" % (self.app.config["QUERY_PAGE"], page) in link["href"]
            )
        else:
            self.assertTrue("last" not in links)

    def assertRelatedLink(self, links, field):
        self.assertTrue("related" in links)
        data_relation_links = links["related"]
        self.assertTrue(field in data_relation_links)
        related_field_links = data_relation_links[field]
        for related_field_link in (
            related_field_links
            if isinstance(related_field_links, list)
            else [related_field_links]
        ):
            self.assertTrue("title" in related_field_link)
            self.assertTrue("href" in related_field_link)

    def assertCustomParams(self, link, params):
        self.assertTrue("href" in link)
        url_params = parse_qs(urlparse(link["href"]).query)
        for param, values in params.lists():
            self.assertTrue(param in url_params)
            for value in values:
                self.assertTrue(value in url_params[param])

    def assert400(self, status):
        self.assertEqual(status, 400)

    def assert401(self, status):
        self.assertEqual(status, 401)

    def assert401or405(self, status):
        self.assertTrue(status == 401 or 405)

    def assert403(self, status):
        self.assertEqual(status, 403)

    def assert405(self, status):
        self.assertEqual(status, 405)

    def assert412(self, status):
        self.assertEqual(status, 412)

    def assert428(self, status):
        self.assertEqual(status, 428)

    def assert500(self, status):
        self.assertEqual(status, 500)

    def setupDB(self):
        self.connection = MongoClient(MONGO_HOST, MONGO_PORT)
        self.connection.drop_database(MONGO_DBNAME)
        if MONGO_USERNAME:
            db = self.connection[MONGO_DBNAME]
            try:
                db.command(
                    "createUser", MONGO_USERNAME, pwd=MONGO_PASSWORD, roles=["dbAdmin"]
                )
            except:
                db.command("dropUser", MONGO_USERNAME)
                db.command(
                    "createUser", MONGO_USERNAME, pwd=MONGO_PASSWORD, roles=["dbAdmin"]
                )
        self.bulk_insert()

    def bulk_insert(self):
        pass

    def dropDB(self):
        self.connection = MongoClient(MONGO_HOST, MONGO_PORT)
        self.connection.drop_database(MONGO_DBNAME)
        self.connection.close()

