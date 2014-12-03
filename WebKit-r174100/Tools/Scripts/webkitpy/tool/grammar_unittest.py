# Copyright (C) 2010 Google Inc. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#    * Neither the name of Google Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import unittest2 as unittest

from webkitpy.tool.grammar import join_with_separators
from webkitpy.tool.grammar import plural
from webkitpy.tool.grammar import pluralize

class GrammarTest(unittest.TestCase):

    def test_join_with_separators(self):
        self.assertEqual(join_with_separators(["one"]), "one")
        self.assertEqual(join_with_separators(["one", "two"]), "one and two")
        self.assertEqual(join_with_separators(["one", "two", "three"]), "one, two, and three")

    def test_plural(self):
        self.assertEqual(plural("patch"), "patches")
        self.assertEqual(plural("test"), "tests")

    def test_pluralize(self):
        self.assertEqual(pluralize(1, "patch"), "1 patch")
        self.assertEqual(pluralize(2, "patch"), "2 patches")
        self.assertEqual(pluralize(1, "patch", True), "1 patch")
        self.assertEqual(pluralize(2, "patch", True), "2 patches")
        self.assertEqual(pluralize(1, "patch", False), "patch")
        self.assertEqual(pluralize(2, "patch", False), "patches")
