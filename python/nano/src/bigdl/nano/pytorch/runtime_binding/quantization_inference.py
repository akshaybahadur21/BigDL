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

import warnings
from functools import partial
from io import BytesIO

import torch
from bigdl.nano.pytorch.lightning import LightningModuleFromTorch
from pytorch_lightning import LightningModule

QUANTIZATION_BINDED_COMPONENTS = ['_quantized_model',
                                  '_quantized_model_up_to_date',
                                  '_forward_fx_quantize',
                                  '_fx_quantize_on_train',
                                  '_fx_quantize_on_fit_start']


def _forward_fx_quantize(self, *args):
    return self._quantized_model(*args)


def _fx_quantize_on_train(self, mode=True):
    self._quantized_model_up_to_date = False
    self._default_inference_quantize = False
    self._quantized_model = None
    self.forward = self._torch_forward


def _fx_quantize_on_fit_start(self):
    self._quantized_model_up_to_date = False
    self._default_inference_quantize = False
    self._quantized_model = None
    self.forward = self._torch_forward


def _fx_quantize_eval(self, quantize=False):
    if quantize:
        if self._quantized_model_up_to_date:
            self.forward = self._forward_fx_quantize
        else:
            raise RuntimeError("Please call trainer.quantize again since the quantized model is"
                               " not up-to-date")
    else:
        self.forward = self._torch_forward


def quantized_state_dict(self):
    if self._quantized_model_up_to_date:
        return self._quantized_model.state_dict()
    else:
        raise RuntimeError("Please call trainer.quantize again since the quantized model is"
                           " not up-to-date.")


def quantized_model_size(self):
    if self._quantized_model:
        """
        This part is from https://github.com/PyTorchLightning/pytorch-lightning/blob
        /master/pytorch_lightning/utilities/memory.py
        Calculates the size of a Module in megabytes.
        The computation includes everything in the :meth:`~torch.nn.Module.state_dict`,
        i.e., by default the parameters and buffers.
        Returns:
            Number of megabytes in the parameters of the input module.
        """
        # TODO when pytorch-lightning is upgraded to 1.5, we can refactor this part
        model_size = BytesIO()
        torch.save(self.quantized_state_dict(), model_size)
        size_mb = model_size.getbuffer().nbytes / 1e6
        return size_mb
    return


def load_quantized_state_dict(self, state_dict):
    import torch
    from torch.quantization.quantize_fx import prepare_fx, convert_fx
    back_to_train = self.training

    self.eval()
    qconfig = torch.quantization.get_default_qconfig('fbgemm')
    if isinstance(self, LightningModuleFromTorch):
        prepared_model = prepare_fx(self.model, {"": qconfig})
    else:
        prepared_model = prepare_fx(self, {"": qconfig})
    qmodel = convert_fx(prepared_model)
    qmodel.load_state_dict(state_dict)

    if back_to_train:
        self.train()
    self._quantized_model = qmodel
    self._quantized_model_up_to_date = True  # set to true before training next time


def on_save_checkpoint(self, checkpoint):
    if "_quantized_model" in dir(self):
        tmp = self._quantized_model
        self._quantized_model = None
        checkpoint['state_dict'] = self.state_dict()
        warnings.warn("Quantized model will not be saved, please call `quantized_state_dict` and "
                      "load_quantized_state_dict for saving and loading.")
        self._quantized_model = tmp


def bind_quantize_methods(pl_model, q_model):
    # check conflicts
    for component in QUANTIZATION_BINDED_COMPONENTS:
        if component in dir(pl_model):
            warnings.warn(f"{component} method/property will be replaced. You may rename your"
                          " customized attributes or methods and call `trainer.quantize again `"
                          "to avoid being overwrite.")

    pl_model._quantized_model = q_model
    pl_model._quantized_model_up_to_date = True
    if q_model:
        pl_model._default_inference_quantize = True
    else:
        pl_model._default_inference_quantize = False
    pl_model._forward_fx_quantize = partial(_forward_fx_quantize, pl_model)
    pl_model._fx_quantize_eval = partial(_fx_quantize_eval, pl_model)
    pl_model._fx_quantize_on_train = partial(_fx_quantize_on_train, pl_model)
    pl_model._fx_quantize_on_fit_start = partial(_fx_quantize_on_fit_start, pl_model)
    pl_model.quantized_state_dict = partial(quantized_state_dict, pl_model)
    pl_model.quantized_model_size = quantized_model_size(pl_model)
    pl_model.load_quantized_state_dict = partial(load_quantized_state_dict, pl_model)
    pl_model.on_save_checkpoint = partial(on_save_checkpoint, pl_model)

    return pl_model
