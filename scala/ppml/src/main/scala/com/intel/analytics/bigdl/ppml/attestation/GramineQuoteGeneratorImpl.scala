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

package com.intel.analytics.bigdl.ppml.attestation

import org.apache.logging.log4j.LogManager
import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;

/**
 * QuoteGenerator for Gramine (https://github.com/gramineproject/gramine)
 */
class GramineQuoteGeneratorImpl extends QuoteGenerator {

  val logger = LogManager.getLogger(getClass)

  val userReportPath = "/dev/attestation/user_report_data"
  val quotePath = "/dev/attestation/quote"

  @throws(classOf[AttestationRuntimeException])
  override def getQuote(userReportData: Array[Byte]): Array[Byte] = {

    if (userReportData.length == 0 || userReportData.length > 32) {
      logger.error("Incorrect userReport size!")
      throw new AttestationRuntimeException("Incorrect userReportData size!")
    }

    try {
      // write userReport
      val out = new BufferedOutputStream(new FileOutputStream(userReportPath))
      out.write(userReportData)
      out.close()
    } catch {
      case e: Exception =>
        logger.error(s"Failed to write user report, ${e}")
        throw new AttestationRuntimeException("Failed " +
        "to persist user report data to Gramine!", e)
    }

    try {
      // read quote
      val quoteFile = new File(quotePath)
      if (quoteFile.length == 0) {
        logger.error("Invalid quote file length.")
        throw new AttestationRuntimeException("Retrieving Gramine quote " +
          "returned Invalid file length!")
      }
      val in = new FileInputStream(quoteFile)
      val quote = new Array[Byte](quoteFile.length.toInt)
      in.read(quote)
      in.close()
      return quote
    } catch {
      case e: Exception =>
        logger.error("Failed to get quote.")
        throw new AttestationRuntimeException("Failed to obtain quote " +
          "content from file to buffer!", e)
    }

    throw new AttestationRuntimeException("Unexpected workflow when generating Gramine Quote!")
  }
}
