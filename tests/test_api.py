"""Tests for the 'load' module."""
import json
import secrets
import tempfile
import unittest

import configvars.api  # the module we are testing
import configvars.storage


class TestLoad(unittest.TestCase):
    """Test the 'load' function of the 'load' module."""

    PROJECT_NAME = "<test_project_name.something>"
    SAMPLE_VARS = {
        "SECRET_KEY": secrets.token_hex(),
        "MAIL_USERNAME": "user@example.com",
        "MAIL_PASSWORD": secrets.token_hex()
    }

    @classmethod
    def setUpClass(cls):
        """Set up cls.

        Create a temporary directory and a settings dict pointing to the temporary directory's name.
        Write self.SAMPLE_VARS to the file associated with self.PROJECT_NAME.
        """
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.SETTINGS = {
            "storage_dir": cls.temp_dir.name,
            "file_name": "{name}.test",
        }
        store_loc = configvars.storage._get_storage_location(cls.PROJECT_NAME, settings=cls.SETTINGS)
        with open(store_loc, "w") as f:
            json.dump(cls.SAMPLE_VARS, f)

    @classmethod
    def tearDownClass(cls):
        """Tear down cls.

        Delete the temporary directory.
        """
        cls.temp_dir.cleanup()

    def test_load_return(self):
        """Test that 'load' returns values when it isn't used as a decorator (i.e when 'vars_' is None)."""
        self.assertEqual(configvars.api.load(self.PROJECT_NAME, settings=self.SETTINGS), self.SAMPLE_VARS)

    def test_load_decorator(self):
        """Test that 'load' works correctly as a decorator (i.e when 'vars_' is not None)."""
        @configvars.api.load(self.PROJECT_NAME, list(self.SAMPLE_VARS)[:-1], settings=self.SETTINGS)
        class TestLoad:
            pass
        for var in list(self.SAMPLE_VARS)[:-1]:
            self.assertTrue(hasattr(TestLoad, var))
            self.assertEqual(getattr(TestLoad, var), self.SAMPLE_VARS[var])

        # test vars_="all" and vars_=True (equivalent)
        @configvars.api.load(self.PROJECT_NAME, vars_="all", settings=self.SETTINGS)
        class TestLoadAll:
            pass

        @configvars.api.load(self.PROJECT_NAME, vars_=True, settings=self.SETTINGS)
        class TestLoadTrue:
            pass

        for var in self.SAMPLE_VARS:
            self.assertTrue(hasattr(TestLoadAll, var))
            self.assertEqual(getattr(TestLoadAll, var), self.SAMPLE_VARS[var])
            self.assertTrue(hasattr(TestLoadTrue, var))
            self.assertEqual(getattr(TestLoadTrue, var), self.SAMPLE_VARS[var])

    def test_load_exception(self):
        """Test that 'load' raises VarNotFound when a variable isn't available."""
        with self.assertRaises(configvars.storage.VarNotFound):
            @configvars.api.load(self.PROJECT_NAME,
                                 list(self.SAMPLE_VARS) + ["VAR_NOT_AVAILABLE"],
                                 settings=self.SETTINGS)
            class _:
                pass
