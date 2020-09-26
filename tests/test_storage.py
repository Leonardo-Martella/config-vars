"""Tests for the 'storage' module."""
import json
import os.path
import secrets
import tempfile
import unittest

import configvars.storage  # the module we are testing


class TestStorageFuncs(unittest.TestCase):
    """Class responsible for testing the storage functions of the 'storage' module."""

    SAMPLE_VARS = {
        "SECRET_KEY": secrets.token_hex(),
        "MAIL_USERNAME": "user@example.com",
        "MAIL_PASSWORD": secrets.token_hex(),
    }
    PROJECT_NAMES = ["test_project", "my_flask_website",
                     "my_flask_website.config"]

    @classmethod
    def setUpClass(cls):
        """Set up cls.

        Create a temporary directory and a settings dict pointing to the temporary directory's name.
        """
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.SETTINGS = {
            "storage_dir": cls.temp_dir.name,
            "file_name": "{name}.test",
        }

    @classmethod
    def tearDownClass(cls):
        """Tear down cls.

        Delete the temporary directory.
        """
        cls.temp_dir.cleanup()

    def test_get_storage_location(self):
        """Test the _get_storage_location function."""
        for project_name in self.PROJECT_NAMES:
            self.assertEqual(
                configvars.storage._get_storage_location(project_name, settings=self.SETTINGS),
                self.SETTINGS["storage_dir"] + "/" + self.SETTINGS["file_name"].format(name=project_name)
            )

    def test_store_vars(self):
        """Test the _store_vars function."""
        for project_name in self.PROJECT_NAMES:
            configvars.storage._store_vars(project_name, self.SAMPLE_VARS, settings=self.SETTINGS)
            store_loc = configvars.storage._get_storage_location(project_name, settings=self.SETTINGS)
            with open(store_loc, "r") as f:
                vars_ = json.load(f)
            self.assertEqual(self.SAMPLE_VARS, vars_)

    def test_load_vars(self):
        """Test the _load_vars function."""
        with self.assertRaises(configvars.storage.NameNotFound):
            configvars.storage._load_vars(secrets.token_hex(), settings=self.SETTINGS)

        with self.assertRaises(configvars.storage.NameNotFound):
            configvars.storage._load_vars(os.path.join(secrets.token_hex(), secrets.token_hex()),
                                          settings=self.SETTINGS)

        for project_name in self.PROJECT_NAMES:
            store_loc = configvars.storage._get_storage_location(project_name, settings=self.SETTINGS)
            with open(store_loc, "w") as f:
                json.dump(self.SAMPLE_VARS, f)
            vars_ = configvars.storage._load_vars(project_name, settings=self.SETTINGS)
            self.assertEqual(self.SAMPLE_VARS, vars_)


class Test_AttrFrozenDict(unittest.TestCase):
    """Class responsible for testing the _AttrFrozenDict of the 'storage' module."""

    def setUp(self):
        self.test_dict = {
            "MY_SECRET": secrets.token_hex(),
            "USER": "myself"
        }
        self.fake_key = secrets.token_hex()
        self.frozen_dict = configvars.storage._AttrFrozenDict(self.test_dict)

    def test_getitem(self):
        """Test the __getitem__ dunder method."""
        for key in self.test_dict:
            self.assertEqual(self.test_dict[key], self.frozen_dict[key])

        with self.assertRaises(KeyError):
            self.frozen_dict[self.fake_key]

    def test_getattr(self):
        """Test the __getattr__ dunder method."""
        for key in self.test_dict:
            self.assertEqual(self.test_dict[key], getattr(self.frozen_dict, key))

        with self.assertRaises(KeyError):
            getattr(self.frozen_dict, self.fake_key)

    def test_setattr(self):
        """Test the frozen __setattr__ dunder method."""
        with self.assertRaises(configvars.storage.FrozenError):
            setattr(self.frozen_dict, list(self.test_dict)[0], "")

        with self.assertRaises(configvars.storage.FrozenError):
            setattr(self.frozen_dict, self.fake_key, "")

    def test_setitem(self):
        """Test the frozen __setitem__ dunder method."""
        with self.assertRaises(configvars.storage.FrozenError):
            self.frozen_dict[list(self.test_dict)[0]] = ""

        with self.assertRaises(configvars.storage.FrozenError):
            self.frozen_dict[self.fake_key] = ""

    def test_delattr(self):
        """Test the __delattr__ dunder method."""
        with self.assertRaises(configvars.storage.FrozenError):
            delattr(self.frozen_dict, list(self.test_dict)[0])

        with self.assertRaises(configvars.storage.FrozenError):
            delattr(self.frozen_dict, self.fake_key)

    def test_delitem(self):
        """Test the __delitem__ dunder method."""
        with self.assertRaises(configvars.storage.FrozenError):
            del self.frozen_dict[list(self.test_dict)[0]]

        with self.assertRaises(configvars.storage.FrozenError):
            del self.frozen_dict[self.fake_key]

    def test_eq(self):
        """Test the __eq__ dunder method."""
        self.assertEqual(self.frozen_dict, self.test_dict)
        self.assertEqual(self.frozen_dict, configvars.storage._AttrFrozenDict(self.test_dict))

    def test_iter(self):
        """Test the __iter__ dunder method (called internally by zip)."""
        for key_1, key_2 in zip(self.frozen_dict, self.test_dict):
            self.assertEqual(key_1, key_2)
