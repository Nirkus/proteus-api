# -*- coding: utf-8 -*-
###############################################################################
# python-proteus - Proteus IPAM Python Library
# Copyright (C) 2012 Stephan Adig <sh@sourcecode.de>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
###############################################################################

import sys

from constants import *
from proteus.objects import *

try:
    from suds.sudsobject import asdict
except ImportError, e:
    print "You don't have the python suds library installed."
    sys.exit(1)


class DNS(object):
    """Proteus DNS Management Class"""

    def __init__(self, proteus_client=None):
        """
        :Parameters:
            - `proteus_client` : instance of :py:class:`proteus.api.client.ProteusClient`

        """
        self._client = proteus_client

    def get_view(self, view_name):
        """
        Get the Proteus View

        :Parameters:
            - `view_name` : string

        :return:
            - :py:class:`proteus.objects.apientity.View`

        """
        if self._client._configuration is None:
            self._client._get_configuration()
        if self._client.is_valid_connection():
            view = self._client._get_entity_by_name(
                self._client._configuration.id,
                view_name,
                TYPE_VIEW)
            return APIObject(TypeRecord=asdict(view))
        return None

    def get_views(self):
        """
        Get a list of all Views in Proteus

        :return:
            - list of :py:class:`proteus.objects.apientity.View`

        """
        if self._client._configuration is None:
            self._client._get_configuration()
        if self._client.is_valid_connection():
            views = self._client._get_entities(
                self._client._configuration.id,
                TYPE_VIEW,
                0,
                99999)
            view_arr = []
            for i in views.item:
                view_arr.append(APIObject(TypeRecord=asdict(i)))
            return view_arr
        return None

    def get_zone(self, zone_name=None, view=None, view_name=None):
        """
        Get a Zone Record from Proteus

        :Parameters:
            - `zone_name` : string
            - `view` : :py:class:`proteus.objects.apientity.View`
            - `view_name` : string

        :returns:
            - :py:class:`proteus.objects.apientity.Zone`

        """
        if self._client._configuration is None:
            self._client._get_configuration()
        if self._client.is_valid_connection():
            if zone_name is not None and zone_name != "":
                if view is not None:
                    zone = self._client._get_entity_by_name(
                        view.id,
                        zone_name,
                        TYPE_ZONE)
                    return APIObject(TypeRecord=asdict(zone))
                elif view is None \
                    and view_name is not None \
                    and view_name != '':
                    view_rec = self.get_view(view_name)
                    zone = self._client._get_entity_by_name(
                        view_rec.id,
                        zone_name,
                        TYPE_ZONE)
                    return APIObject(TypeRecord=asdict(zone))
        return False

    def _get_record(
        self,
        hostname,
        zonename,
        view=None,
        view_name=None,
        rec_type=TYPE_HOSTRECORD):
        """
        Generic method to retrieve the Proteus Resource Records

        :Parameters:
            - `hostname` : string
            - `zonename` : string
            - `view` : :py:class:`proteus.objects.apientity.View`
            - `view_name` : string
            - `rec_type` : string [ should be one of :py:data:`proteus.api.constants.DNS_ALLTYPES` ]


        :returns:
            - Depends on the result of Proteus call but can be one of these:
                - :py:class:`proteus.objects.apientity.HostRecord`
                - :py:class:`proteus.objects.apientity.MXRecord`
                - :py:class:`proteus.objects.apientity.TXTRecord`
                - :py:class:`proteus.objects.apientity.HINFORecord`
                - :py:class:`proteus.objects.apientity.CNAMERecord`
                - :py:class:`proteus.objects.apientity.SRVRecord`

        See: [#private_method]_
        """

        if self._client.is_valid_connection():
            if self._client._configuration is None:
                self._client._get_configuration()
            if view is not None:
                zone_arr = zonename.split(".")
                count = len(zone_arr)
                parent_view = view.id
            if view_name is not None:
                view_rec = self.get_view(view_name)
                zone_arr = zonename.split('.')
                count = len(zone_arr)
                parent_view = view_rec
            for i in reversed(zone_arr):
                if count != 0:
                    zone = self.get_zone(i, parent_view)
                    if zone is not None:
                        parent_view = zone
                if count == 1:
                    record = self._client._get_entity_by_name(
                        parent_view.id,
                        hostname,
                        rec_type)
                    if record is not None:
                        return APIObject(TypeRecord=asdict(record))
                    else:
                        return None
                count = count - 1
        return None

    def get_host_record(self, hostname, zonename, view=None, view_name=None):
        return self._get_record(
            hostname,
            zonename,
            view,
            view_name,
            TYPE_HOSTRECORD)

    def get_mx_record(self, hostname, zonename, view=None, view_name=None):
        return self._get_record(
            hostname,
            zonename,
            view,
            view_name,
            TYPE_MXRECORD)

    def get_txt_record(self, hostname, zonename, view=None, view_name=None):
        return self._get_record(
            hostname,
            zonename,
            view,
            view_name,
            TYPE_TXTRECORD)

    def get_cname_record(self, hostname, zonename, view=None, view_name=None):
        return self._get_record(
            hostname,
            zonename,
            view,
            view_name,
            TYPE_CNAMERECORD)

    def get_hinfo_record(self, hostname, zonename, view=None, view_name=None):
        return self._get_record(
            hostname,
            zonename,
            view,
            view_name,
            TYPE_HINFORECORD)

    def get_srv_record(self, hostname, zonename, view=None, view_name=None):
        return self._get_record(
            hostname,
            zonename,
            view,
            view_name,
            TYPE_SRVRECORD)

    def _get_records_by_zone(self, zone=None, record_type=TYPE_ZONE):
        if self._client.is_valid_connection():
            if self._client._configuration is None:
                self._client._get_configuration()
            if zone is not None:
                records = self._client._get_entities(
                    zone.id,
                    record_type,
                    0,
                    9999999)
                rec_list = []
                try:
                    for i in records.item:
                        a = APIObject(TypeRecord=asdict(i))
                        if a is not None:
                            rec_list.append(a)
                    return rec_list
                except AttributeError:
                    pass
        return None

    def get_hosts_by_zone(self, zone=None):
        return self._get_records_by_parent(zone, TYPE_HOSTRECORD)

    def get_zones_by_zone(self, zone=None):
        return self._get_records_by_parent(zone, TYPE_ZONE)

    def get_mxs_by_zone(self, zone=None):
        return self._get_records_by_parent(zone, TYPE_MXRECORD)

    def get_txts_by_zone(self, zone=None):
        return self._get_records_by_parent(zone, TYPE_TXTRECORD)

    def get_cnames_by_zone(self, zone=None):
        return self._get_records_by_parent(zone, TYPE_CNAMERECORD)

    def get_hinfo_by_zone(self, zone=None):
        return self._get_records_by_parent(zone, TYPE_HINFORECORD)

    def get_zone_list(
        self,
        zonename,
        view=None,
        view_name=None,
        rec_type=DNS_ALLTYPES):
        if self._client._configuration is None:
            self._client._get_configuration()
        if self._client.is_valid_connection():
            if view is not None and view_name is None:
                zone_arr = zonename.split('.')
                count = len(zone_arr)
                parent_view = view
            if view is None and view_name is not None:
                zone_arr = zonename.split('.')
                count = len(zone_arr)
                view_rec = self.get_view(view_name)
                parent_view = view_rec

            for i in reversed(zone_arr):
                if count != 0:
                    zone = self.get_zone(i, parent_view)
                    if zone is None:
                        return None
                    parent_view = zone
                if count == 1:
                    if rec_type == DNS_ALLTYPES:
                        zone_list = []
                        for i in DNS_ALLTYPES:
                            rec_list = []
                            rec_list = self._get_records_by_zone(zone, i)
                            if rec_list is not None:
                                zone_list.extend(rec_list)
                    else:
                        if rec_type in DNS_ALLTYPES:
                            rec_list = []
                            rec_list = self._get_records_by_zone(
                                zone,
                                rec_type)
                            if rec_list is not None:
                                return rec_list
                count = count - 1
        return None


