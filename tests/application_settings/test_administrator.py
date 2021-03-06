import unittest
import tests.envs as envs
import pykintone
from pykintone.application_settings.administrator import Administrator
import pykintone.application_settings.form_field as ff
from pykintone.application_settings.view import View


class TestGeneral(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        print("You have to delete the application from the application administration view.")

    def test_get_application_information(self):
        app = pykintone.load(envs.FILE_PATH).app()
        ai = app.administration().get_app_info().info
        self.assertTrue(ai)

    def test_get_application_informations(self):
        app = pykintone.load(envs.FILE_PATH).app()
        ai = app.administration().select_app_info(name="pykintone").infos
        self.assertTrue(ai)

        app_id = ai[0].app_id
        ai = app.administration().select_app_info(app_ids=[app_id]).infos
        self.assertTrue(ai)

    def test_create_rollback_application(self):
        kintone = pykintone.load(envs.FILE_PATH)

        with kintone.administration().transaction().as_test_mode() as admin:
            created = admin.create_application("test_create_application")
            admin.revision = created.revision
            self.assertTrue(created.ok)

    def test_create_application(self):
        kintone = pykintone.load(envs.FILE_PATH)

        with kintone.administration().transaction() as admin:
            # create application
            created = admin.create_application("my_application")

            # create form
            f1 = ff.BaseFormField.create("SINGLE_LINE_TEXT", "title", "Title")
            f2 = ff.BaseFormField.create("MULTI_LINE_TEXT", "description", "Desc")
            admin.form().add([f1, f2])

            # create view
            view = View.create("mylist", ["title", "description"])
            admin.view().update(view)

    def test_copy_application(self):
        kintone = pykintone.load(envs.FILE_PATH)
        app = kintone.app()

        with kintone.administration().transaction().as_test_mode() as admin:
            created = admin.copy_application("copied application", app.app_id)
            self.assertTrue(created.ok)
