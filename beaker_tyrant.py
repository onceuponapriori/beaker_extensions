# Courtesy of: http://www.jackhsu.com/2009/05/27/pylons-with-tokyo-cabinet-beaker-sessions

import logging
 
from beaker.container import NamespaceManager, Container
from beaker.synchronization import file_synchronizer
from beaker.util import verify_directory
 
try:
  from pytyrant import PyTyrant
except ImportError:
  raise InvalidCacheBackendError("PyTyrant cache backend requires the 'pytyrant' library")

try:
   import cPickle as pickle
except:
   import pickle
 
log = logging.getLogger(__name__)
 
class TokyoTyrantManager(NamespaceManager):
  def __init__(self, namespace, url=None, data_dir=None, lock_dir=None, **params):
    NamespaceManager.__init__(self, namespace)

    if not url:
      raise MissingCacheParameter("url is required")

    if lock_dir:
      self.lock_dir = lock_dir
    elif data_dir:
      self.lock_dir = data_dir + "/container_tcd_lock"
    if self.lock_dir:
      verify_directory(self.lock_dir)           

    host, port = url.split(':')
    self.tc = PyTyrant.open(host, int(port))

  def get_creation_lock(self, key):
    return file_synchronizer(
      identifier ="tccontainer/funclock/%s" % self.namespace,
      lock_dir = self.lock_dir)

  def _format_key(self, key):
    return self.namespace + '_' 

  def __getitem__(self, key):
    return pickle.loads(self.tc.get(self._format_key(key)))

  def __contains__(self, key):
    return self.tc.has_key(self._format_key(key))

  def has_key(self, key):
    return key in self

  def set_value(self, key, value):
    self.tc[self._format_key(key)] =  pickle.dumps(value)

  def __setitem__(self, key, value):
    self.set_value(key, value)

  def __delitem__(self, key):
    del self.tc[self._format_key(key)]

  def do_remove(self):
    self.tc.clear()

  def keys(self):
    raise self.tc.keys()
 
 
class TokyoTyrantContainer(Container):
    namespace_manager = TokyoTyrantManager