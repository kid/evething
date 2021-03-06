# ------------------------------------------------------------------------------
# Copyright (c) 2010-2013, EVEthing team
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#     Redistributions of source code must retain the above copyright notice, this
#       list of conditions and the following disclaimer.
#     Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
# OF SUCH DAMAGE.
# ------------------------------------------------------------------------------

from .apitask import APITask

from thing.models import RefType

# ---------------------------------------------------------------------------

class RefTypes(APITask):
    name = 'thing.ref_types'

    def run(self, url, taskstate_id, apikey_id, zero):
        if self.init(taskstate_id, apikey_id) is False:
            return

        # Fetch the API data
        if self.fetch_api(url, {}, use_auth=False) is False or self.root is None:
            return

        # Build a refTypeID:row dictionary
        bulk_data = {}
        for row in self.root.findall('result/rowset/row'):
            bulk_data[int(row.attrib['refTypeID'])] = row

        # Bulk retrieve all of those stations that exist
        rt_map = RefType.objects.in_bulk(bulk_data.keys())

        new = []
        for refTypeID, row in bulk_data.items():
            reftype = rt_map.get(refTypeID)

            # RefType does not exist, make a new one
            if reftype is None:
                new.append(RefType(
                    id=refTypeID,
                    name=row.attrib['refTypeName'],
                ))

            # RefType exists and name has changed, update it
            elif reftype.name != row.attrib['refTypeName']:
                reftype.name = row.attrib['refTypeName']
                reftype.save()

        # Create any new stations
        if new:
            RefType.objects.bulk_create(new)

        return True

# ---------------------------------------------------------------------------
