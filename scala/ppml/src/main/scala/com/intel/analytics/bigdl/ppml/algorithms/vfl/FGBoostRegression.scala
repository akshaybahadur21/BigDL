/*
 * Copyright 2021 The BigDL Authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.intel.analytics.bigdl.ppml.algorithms.vfl

import com.intel.analytics.bigdl.dllib.nn.Sequential
import com.intel.analytics.bigdl.dllib.optim.MAE
import com.intel.analytics.bigdl.ppml.FLModel
import com.intel.analytics.bigdl.ppml.base.Estimator
import com.intel.analytics.bigdl.ppml.fgboost.FGBoostModel

/**
 * FGBoost regression algorithm
 * @param learningRate learning rate
 * @param maxDepth max depth of boosting tree
 * @param minChildSize
 */
class FGBoostRegression(learningRate: Float = 0.005f,
                        maxDepth: Int = 6,
                        minChildSize: Int = 1)
  extends FGBoostModel(continuous = true,
    learningRate = learningRate,
    maxDepth = maxDepth,
    minChildSize = minChildSize,
    validationMethods = Array(new MAE())) {
}
