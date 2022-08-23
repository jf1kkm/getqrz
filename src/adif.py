# Copyright 2022 Shinji (kobie) Kobayashi, JF1KKM 
# using and incorporating extracts of earlier work available at
# https://gitlab.com/andreas_krueger_py/adif_io ,
# Copyright 2019 Andreas Krüger, DJ3EI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This is an ADIF parser in Python.

# It knows nothing about ADIF data types or enumerations,
# everything is a string, so it is fairly simple.

# But it does correcly handle things like:
# <notes:66>In this QSO, we discussed ADIF and in particular the <eor> marker.
# So, in that sense, this parser is somewhat sophisticated.

# Main result of parsing: List of QSOs.
# Each QSO is one Python dict.
# Keys in that dict are ADIF field names in upper case,
# value for a key is whatever was found in the ADIF, as a string.
# Order of QSOs in the list is same as in ADIF file.


import re

def read_from_string(adif_string):

    field_re = re.compile(r'<((eor)|(\w+)\:(\d+)(\:[^>]+)?)>', re.IGNORECASE)
    
    qsos = []
    cursor = 0
        
    qso = {}
    field_mo = field_re.search(adif_string, cursor)
    while(field_mo):
        if field_mo.group(2):
            # <eor> found:
            qsos.append(qso)
            qso = {}
            cursor = field_mo.end(0)
        else:
            # Field found:
            field = field_mo.group(3).upper()
            value_start = field_mo.end(0)
            value_end = value_start + int(field_mo.group(4))
            value = adif_string[value_start:value_end]
            qso[field] = value
            cursor = value_end
        field_mo = field_re.search(adif_string, cursor)

    #return [qsos]
    return qsos



