# -*- coding: utf-8 -*-

"""
/***************************************************************************
 CounterpartStreams
                                 A QGIS plugin
 Conflation_DEM
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-03-30
        copyright            : (C) 2021 by Sokhrannykh V., Samsonov T. 
        email                : vitaliy_mapgeo@mail.ru
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Sokhrannykh V., Samsonov T., Lomonosov MSU Faculty of Geography '
__date__ = '2021-03-30'
__copyright__ = '(C) 2021 by Sokhrannykh V., Samsonov T. '

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsMessageLog,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterField,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterFeatureSink)

from .ConflationLinks_general import conflation_links

class ConflationLinksAlgorithm(QgsProcessingAlgorithm):

    COUNTERPART_STREAMS = 'Input Counterpart Streams'
    RIVERS = 'Input vector Streams'
    # RIVERS_FIELD = 'Streams Field ID'
    # COUNT_FIELD = 'Counterpart Streams Field ID'
    OUTPUT_LINKS = 'Output Conflation links'
    # OUTPUT_AREA = 'Output Conflation area'

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.RIVERS,
                self.tr('Input Vector Streams'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        # self.addParameter(
        #     QgsProcessingParameterField(
        #         self.RIVERS_FIELD,
        #         self.tr('Streams Field ID'),
        #         parentLayerParameterName=self.RIVERS
        #     )
        # )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.COUNTERPART_STREAMS,
                self.tr('Input Counterpart Streams'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        # self.addParameter(
        #     QgsProcessingParameterField(
        #         self.COUNT_FIELD,
        #         self.tr('Counterpart Streams Field ID'),
        #         parentLayerParameterName=self.COUNTERPART_STREAMS
        #     )
        # )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT_LINKS,
                self.tr('Output Conflation links'),
            )
        )

        # self.addParameter(
        #     QgsProcessingParameterFileDestination(
        #         self.OUTPUT_AREA,
        #         self.tr('Output Conflation area')
        #     )
        # )
        return

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        in_counterparts = self.parameterAsVectorLayer(parameters, self.COUNTERPART_STREAMS, context).dataProvider().dataSourceUri()
        in_hidrolines = self.parameterAsVectorLayer(parameters, self.RIVERS, context).dataProvider().dataSourceUri()

        QgsMessageLog.logMessage(message=in_hidrolines)

        # hydro_field = self.parameterAsFields(parameters, self.RIVERS_FIELD, context)[0]
        # count_field = self.parameterAsFields(parameters, self.COUNT_FIELD, context)[0]
        out_links = self.parameterAsOutputLayer(parameters, self.OUTPUT_LINKS, context)
        # out_area = self.parameterAsOutputLayer(parameters, self.OUTPUT_AREA, context)

        conflation_links(in_counterparts, in_hidrolines, out_links)

        return {self.OUTPUT_LINKS: out_links}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Conflation Links'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return ''

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ConflationLinksAlgorithm()