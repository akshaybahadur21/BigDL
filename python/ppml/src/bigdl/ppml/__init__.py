#
# Copyright 2016 The BigDL Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from bigdl.dllib.nncontext import *
from bigdl.dllib.utils.engine import prepare_env
from bigdl.dllib.utils.common import *
from bigdl.ppml.fl_server import *
from bigdl.ppml.utils import *
import bigdl

prepare_env()
creator_classes = JavaCreator.get_creator_class()[:]
JavaCreator.set_creator_class([])
JavaCreator.add_creator_class("com.intel.analytics.bigdl.ppml.python.PythonPPML")
for clz in creator_classes:
    JavaCreator.add_creator_class(clz)
