# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Bug helper tests."""

import os
import unittest
from unittest import mock
from . import ecosystems


class GetNextVersionTest(unittest.TestCase):
  """get_next_version tests."""

  def test_pypi(self):
    """Test PyPI."""
    ecosystem = ecosystems.get('PyPI')
    self.assertEqual('1.36.0rc1', ecosystem.next_version('grpcio', '1.35.0'))
    self.assertEqual('1.36.1', ecosystem.next_version('grpcio', '1.36.0'))
    self.assertEqual('0.3.0', ecosystem.next_version('grpcio', '0'))
    with self.assertRaises(ecosystems.EnumerateError):
      ecosystem.next_version('doesnotexist123456', '1')

  def test_maven(self):
    """Test Maven."""
    ecosystem = ecosystems.get('Maven')
    self.assertEqual('1.36.0',
                     ecosystem.next_version('io.grpc:grpc-core', '1.35.1'))
    self.assertEqual('0.7.0', ecosystem.next_version('io.grpc:grpc-core', '0'))
    with self.assertRaises(ecosystems.EnumerateError):
      ecosystem.next_version('blah:doesnotexist123456', '1')

  @unittest.skipUnless(os.getenv('DEPS_DEV_API_KEY'), 'Requires API key')
  def test_maven_deps_dev(self):
    """Test Maven using deps.dev."""
    ecosystems.use_deps_dev = True
    ecosystems.deps_dev_api_key = os.getenv('DEPS_DEV_API_KEY')

    ecosystem = ecosystems.get('Maven')
    self.assertEqual('1.36.0',
                     ecosystem.next_version('io.grpc:grpc-core', '1.35.1'))
    self.assertEqual('0.7.0', ecosystem.next_version('io.grpc:grpc-core', '0'))
    with self.assertRaises(ecosystems.EnumerateError):
      ecosystem.next_version('blah:doesnotexist123456', '1')

    ecosystems.use_deps_dev = False

  def test_gems(self):
    """Test RubyGems."""
    ecosystem = ecosystems.get('RubyGems')
    self.assertEqual('0.8.0', ecosystem.next_version('rails', '0'))
    self.assertEqual('0.9.5', ecosystem.next_version('rails', '0.9.4.1'))
    self.assertEqual('2.3.8.pre1', ecosystem.next_version('rails', '2.3.7'))
    self.assertEqual('4.0.0.rc1',
                     ecosystem.next_version('rails', '4.0.0.beta1'))
    self.assertEqual('5.0.0.racecar1',
                     ecosystem.next_version('rails', '5.0.0.beta4'))
    with self.assertRaises(ecosystems.EnumerateError):
      ecosystem.next_version('doesnotexist123456', '1')

  def test_nuget(self):
    """Test NuGet."""
    ecosystem = ecosystems.get('NuGet')
    self.assertEqual('3.0.1',
                     ecosystem.next_version('NuGet.Server.Core', '3.0.0'))
    self.assertEqual('3.0.0.4001',
                     ecosystem.next_version('Castle.Core', '3.0.0.3001'))
    self.assertEqual('3.1.0-RC',
                     ecosystem.next_version('Castle.Core', '3.0.0.4001'))
    self.assertEqual('2.1.0-dev-00668',
                     ecosystem.next_version('Serilog', '2.1.0-dev-00666'))
    with self.assertRaises(ecosystems.EnumerateError):
      ecosystem.next_version('doesnotexist123456', '1')

  def test_debian(self):
    """Test Debian"""
    ecosystem = ecosystems.get('Debian:9')
    self.assertEqual('1.13.6-1', ecosystem.next_version('nginx', '1.13.5-1'))
    self.assertEqual('1.13.6-2', ecosystem.next_version('nginx', '1.13.6-1'))
    self.assertEqual('3.0.1+dfsg-2',
                     ecosystem.next_version('blender', '3.0.1+dfsg-1'))

    self.assertGreater(
        ecosystem.sort_key('1.13.6-2'), ecosystem.sort_key('1.13.6-1'))

    # Test Ecosystem remover
    ecosystem = ecosystems.get('Debian:10')
    versions = ecosystem.enumerate_versions('cyrus-sasl2', '2.1.27+dfsg-1',
                                            None)
    self.assertIn('2.1.27+dfsg-1+deb10u1', versions)
    self.assertNotIn('2.1.27~101-g0780600+dfsg-3+deb9u1', versions)
    self.assertNotIn('2.1.27~101-g0780600+dfsg-3+deb9u2', versions)

    with self.assertRaises(ecosystems.EnumerateError):
      ecosystem.next_version('doesnotexist123456', '1')

  def test_semver(self):
    """Test SemVer."""
    ecosystem = ecosystems.get('Go')
    self.assertEqual('1.0.1-0', ecosystem.next_version('blah', '1.0.0'))
    self.assertEqual('1.0.0-pre.0', ecosystem.next_version('blah', '1.0.0-pre'))

  @mock.patch('osv.cache.Cache')
  def test_cache(self, cache: mock.MagicMock):
    cache.get.return_value = None
    ecosystems.set_cache(cache)

    debian = ecosystems.get('Debian:9')
    debian.next_version('nginx', '1.13.5-1')
    cache.get.assert_called_once()
    cache.set.assert_called_once()


if __name__ == '__main__':
  unittest.main()
