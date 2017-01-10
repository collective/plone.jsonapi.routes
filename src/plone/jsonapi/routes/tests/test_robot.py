# -*- coding: utf-8 -*-

import unittest
import robotsuite
from plone.testing import layered

from plone.jsonapi.routes.tests.base import ROBOT_TESTING


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite("robot_tests.txt"),
                layer=ROBOT_TESTING),
    ])
    return suite
