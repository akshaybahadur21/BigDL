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

import tensorflow as tf
from bigdl.nano.tf.keras import Sequential, Model
from tensorflow.keras.layers import LSTM, Reshape, Dense, Input


class LSTMModel(Model):
    def __init__(self, input_dim, hidden_dim, layer_num, dropout, output_dim):
        super(LSTMModel, self).__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.layer_num = layer_num
        self.output_dim = output_dim
        self.dropout = dropout
        self.lstm_list = Sequential([Input(shape=(None, self.input_dim))])
        for layer in range(self.layer_num - 1):
            self.lstm_list.add(LSTM(self.hidden_dim[layer],
                                    return_sequences=True,
                                    dropout=self.dropout[layer],
                                    activation="linear",
                                    name="lstm_" + str(layer+1)))
        self.lstm_list.add(LSTM(self.hidden_dim[-1],
                                dropout=dropout[-1],
                                activation="linear",
                                name="lstm_" + str(self.layer_num)))
        self.fc = Dense(self.output_dim)
        self.out_shape = Reshape((1, self.output_dim), input_shape=(self.output_dim,))

    def call(self, input_seq):
        lstm_out = input_seq
        out = self.lstm_list(lstm_out)
        out = self.fc(out)
        out = self.out_shape(out)
        return out

    def get_config(self):
        return {'input_dim': self.input_dim,
                'hidden_dim': self.hidden_dim,
                'layer_num': self.layer_num,
                'dropout': self.dropout,
                'output_dim': self.output_dim}

    @classmethod
    def from_config(cls, config):
        return cls(**config)


def model_creator(config):
    hidden_dim = config.get('hidden_dim', 32)
    dropout = config.get('dropout', 0.2)
    layer_num = config.get('layer_num', 2)
    if isinstance(hidden_dim, list):
        assert len(hidden_dim) == layer_num, \
            "length of hidden_dim should be equal to layer_num"
    if isinstance(dropout, list):
        assert len(dropout) == layer_num, \
            "length of dropout should be equal to layer_num"
    if isinstance(hidden_dim, int):
        hidden_dim = [hidden_dim]*layer_num
    if isinstance(dropout, (float, int)):
        dropout = [dropout]*layer_num
    model = LSTMModel(input_dim=config['input_feature_num'],
                      hidden_dim=hidden_dim,
                      layer_num=layer_num,
                      dropout=dropout,
                      output_dim=config['output_feature_num'])

    learning_rate = config.get('lr', 1e-3)
    optimizer = getattr(tf.keras.optimizers, config.get('optim', "Adam"))(learning_rate)
    model.compile(loss=config.get("loss", "mse"),
                  optimizer=optimizer,
                  metrics=[config.get("metric", "mse")])
    return model
