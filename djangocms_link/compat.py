from distutils.version import LooseVersion

import cms


CMS_VERSION = cms.__version__

CMS_LT_4 = LooseVersion(CMS_VERSION) < LooseVersion("4.0")