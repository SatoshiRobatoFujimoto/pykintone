# -*- coding: utf-8 -*-
import unittest
from datetime import datetime
import tests.envs as envs
import pykintone
from pykintone.model import kintoneModel
import pykintone.structure_field as sf
from pykintone.structure import PropertyDetail, FieldType


class TestAppModel(kintoneModel):

    def __init__(self):
        super(TestAppModel, self).__init__()
        self.my_key = ""
        self.stringField = ""
        self.numberField = 0
        self.radio = ""
        self.checkbox = []
        self.dateField = datetime.now()
        self.time = datetime.now()
        self.datetimeField = datetime.now()
        self.user_select = sf.UserSelect()
        self.created_time = None
        self.updated_time = None
        self.creator = None
        self.modifier = None
        self.changeLogs = []
        self.attachfile = sf.File()

        self._property_details.append(PropertyDetail("time", FieldType.TIME))
        self._property_details.append(PropertyDetail("created_time", FieldType.CREATED_TIME, field_name="作成日時", unsent=True))
        self._property_details.append(PropertyDetail("updated_time", FieldType.UPDATED_TIME, field_name="更新日時", unsent=True))
        self._property_details.append(PropertyDetail("creator", FieldType.CREATOR, field_name="作成者", unsent=True))
        self._property_details.append(PropertyDetail("modifier", FieldType.MODIFIER, field_name="更新者", unsent=True))
        self._property_details.append(PropertyDetail("changeLogs", FieldType.SUBTABLE, sub_type=History))


class History(kintoneModel):

    def __init__(self, desc="", ymd=None):
        super(History, self).__init__()
        self.changeYMD = datetime.now() if not ymd else ymd
        self.historyDesc = desc
        self._property_details.append(PropertyDetail("changeYMD", FieldType.DATETIME))


class TestModel(unittest.TestCase):

    def test_model(self):
        app = pykintone.load(envs.FILE_PATH).app()

        # initialize model
        model = TestAppModel()
        model.my_key = "model_test"
        model.stringField = "model_test"
        model.numberField = 1
        model.radio = "radio1"
        model.checkbox = ["check2"]
        model.changeLogs.append(History("initialized"))

        # create model
        result = app.create(model)
        self.assertTrue(result.ok)

        # get model
        created = app.get(result.record_id).model(TestAppModel)

        # update model
        created.stringField = "model_updated"
        created.changeLogs[0].historyDesc = "updated"
        created.changeLogs.append(History("added"))
        app.update(created)
        updated = app.get(result.record_id).model(TestAppModel)
        self.assertEqual(created.stringField, updated.stringField)
        self.assertEqual(2, len(updated.changeLogs))
        for i, c in enumerate(created.changeLogs):
            self.assertEqual(c.historyDesc, updated.changeLogs[i].historyDesc)

        # delete model
        app.delete(updated)
        deleted = app.get(result.record_id).model(TestAppModel)
        self.assertFalse(deleted)

    def test_models(self):
        app = pykintone.load(envs.FILE_PATH).app()
        keyword = "models_test"
        select_models = lambda : app.select("stringField = \"{0}\"".format(keyword)).models(TestAppModel)

        # initialize model
        ms = []
        for i in range(2):
            m = TestAppModel()
            m.my_key = "model_test_{0}".format(i)
            m.stringField = keyword
            m.numberField = i
            ms.append(m)

        # create model
        result = app.batch_create(ms)
        self.assertTrue(result.ok)

        # get model
        createds = select_models()

        # update model
        for i, m in enumerate(createds):
            m.numberField = i + 1
        app.batch_update(createds)

        updateds = select_models()
        for i, m in enumerate(createds):
            self.assertEqual(i + 1, m.numberField)

        # delete model
        app.delete(updateds)
        deleted = select_models()
        self.assertEqual(0, len(deleted))

    def test_user_select(self):
        app = pykintone.load(envs.FILE_PATH).app()

        model = TestAppModel()
        model.my_key = "user_select_field_check"
        result = app.create(model)
        self.assertTrue(result.ok)
        created = app.get(result.record_id).model(TestAppModel)

        created.user_select = sf.UserSelect(created.creator.code)
        result = app.update(created)
        self.assertTrue(result.ok)
        app.delete([created])

    def test_file(self):
        import os
        app = pykintone.load(envs.FILE_PATH).app()
        file_path = os.path.join(os.path.dirname(__file__), "./kintone.PNG")

        model = TestAppModel()
        model.my_key = "file_field_check"
        model.attachfile = sf.File.upload(file_path, app)
        self.assertTrue(model.attachfile)

        result = app.create(model)
        self.assertTrue(result.ok)
        created = app.get(result.record_id).model(TestAppModel)
        file = created.attachfile.download(app)
        self.assertTrue(file)
        app.delete([created])
