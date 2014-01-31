#!/usr/bin/env python
#
# Copyright 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Unittest for symbolize.py.

This test uses test libraries generated by the Android g++ toolchain.

Should things break you can recreate the libraries and get the updated
addresses and demangled names by running the following:
  cd test/symbolize/
  make
  nm -gC *.so
"""

import sys
import StringIO
import unittest

import symbolize

LIB_A_PATH = '/build/android/tests/symbolize/liba.so'
LIB_B_PATH = '/build/android/tests/symbolize/libb.so'

def RunSymbolizer(text):
  output = StringIO.StringIO()
  s = symbolize.Symbolizer(output)
  s.write(text)
  return output.getvalue()


class SymbolizerUnittest(unittest.TestCase):
  def testSingleLineNoMatch(self):
    # Leading '#' is required.
    expected = '00 0x00000000 ' + LIB_A_PATH + '+0x00000254\n'
    self.assertEqual(expected, RunSymbolizer(expected))

    # Whitespace should be exactly one space.
    expected = '#00  0x00000000 ' + LIB_A_PATH + '+0x00000254\n'
    self.assertEqual(expected, RunSymbolizer(expected))
    expected = '#00 0x00000000  ' + LIB_A_PATH + '+0x00000254\n'
    self.assertEqual(expected, RunSymbolizer(expected))

    # Decimal stack frame numbers are required.
    expected = '#0a 0x00000000 ' + LIB_A_PATH + '+0x00000254\n'
    self.assertEqual(expected, RunSymbolizer(expected))

    # Hexadecimal addresses are required.
    expected = '#00 0xghijklmn ' + LIB_A_PATH + '+0x00000254\n'
    self.assertEqual(expected, RunSymbolizer(expected))
    expected = '#00 0x00000000 ' + LIB_A_PATH + '+0xghijklmn\n'
    self.assertEqual(expected, RunSymbolizer(expected))

    # Addresses must be exactly 8 characters.
    expected = '#00 0x0000000 ' + LIB_A_PATH + '+0x00000254\n'
    self.assertEqual(expected, RunSymbolizer(expected))
    expected = '#00 0x000000000 ' + LIB_A_PATH + '+0x00000254\n'
    self.assertEqual(expected, RunSymbolizer(expected))

    expected = '#00 0x0000000 ' + LIB_A_PATH + '+0x0000254\n'
    self.assertEqual(expected, RunSymbolizer(expected))
    expected = '#00 0x000000000 ' + LIB_A_PATH + '+0x000000254\n'
    self.assertEqual(expected, RunSymbolizer(expected))

    # Addresses must be prefixed with '0x'.
    expected = '#00 00000000 ' + LIB_A_PATH + '+0x00000254\n'
    self.assertEqual(expected, RunSymbolizer(expected))
    expected = '#00 0x00000000 ' + LIB_A_PATH + '+00000254\n'
    self.assertEqual(expected, RunSymbolizer(expected))

    # Library name is required.
    expected = '#00 0x00000000\n'
    self.assertEqual(expected, RunSymbolizer(expected))
    expected = '#00 0x00000000 +0x00000254\n'
    self.assertEqual(expected, RunSymbolizer(expected))

    # Library name must be followed by offset with no spaces around '+'.
    expected = '#00 0x00000000 ' + LIB_A_PATH + ' +0x00000254\n'
    self.assertEqual(expected, RunSymbolizer(expected))
    expected = '#00 0x00000000 ' + LIB_A_PATH + '+ 0x00000254\n'
    self.assertEqual(expected, RunSymbolizer(expected))
    expected = '#00 0x00000000 ' + LIB_A_PATH + ' 0x00000254\n'
    self.assertEqual(expected, RunSymbolizer(expected))
    expected = '#00 0x00000000 ' + LIB_A_PATH + '+\n'
    self.assertEqual(expected, RunSymbolizer(expected))

  def testSingleLine(self):
    text = '#00 0x00000000 ' + LIB_A_PATH + '+0x00000254\n'
    expected = '#00 0x00000000 A::Bar(char const*)\n'
    actual = RunSymbolizer(text)
    self.assertEqual(expected, actual)

  def testSingleLineWithSurroundingText(self):
    text = 'LEFT #00 0x00000000 ' + LIB_A_PATH + '+0x00000254 RIGHT\n'
    expected = 'LEFT #00 0x00000000 A::Bar(char const*) RIGHT\n'
    actual = RunSymbolizer(text)
    self.assertEqual(expected, actual)

  def testMultipleLinesSameLibrary(self):
    text = '#00 0x00000000 ' + LIB_A_PATH + '+0x00000254\n'
    text += '#01 0x00000000 ' + LIB_A_PATH + '+0x00000234\n'
    expected = '#00 0x00000000 A::Bar(char const*)\n'
    expected += '#01 0x00000000 A::Foo(int)\n'
    actual = RunSymbolizer(text)
    self.assertEqual(expected, actual)

  def testMultipleLinesDifferentLibrary(self):
    text = '#00 0x00000000 ' + LIB_A_PATH + '+0x00000254\n'
    text += '#01 0x00000000 ' + LIB_B_PATH + '+0x00000234\n'
    expected = '#00 0x00000000 A::Bar(char const*)\n'
    expected += '#01 0x00000000 B::Baz(float)\n'
    actual = RunSymbolizer(text)
    self.assertEqual(expected, actual)

  def testMultipleLinesWithSurroundingTextEverywhere(self):
    text = 'TOP\n'
    text += 'LEFT #00 0x00000000 ' + LIB_A_PATH + '+0x00000254 RIGHT\n'
    text += 'LEFT #01 0x00000000 ' + LIB_B_PATH + '+0x00000234 RIGHT\n'
    text += 'BOTTOM\n'
    expected = 'TOP\n'
    expected += 'LEFT #00 0x00000000 A::Bar(char const*) RIGHT\n'
    expected += 'LEFT #01 0x00000000 B::Baz(float) RIGHT\n'
    expected += 'BOTTOM\n'
    actual = RunSymbolizer(text)
    self.assertEqual(expected, actual)


if __name__ == '__main__':
  unittest.main()
