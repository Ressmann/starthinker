###########################################################################
#
#  Copyright 2020 Google LLC
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
###########################################################################

citiesListResponse_Schema = [{
    'name':
        'cities',
    'type':
        'RECORD',
    'mode':
        'REPEATED',
    'fields': [{
        'description': '',
        'name': 'countryCode',
        'type': 'STRING',
        'mode': 'NULLABLE'
    }, {
        'description': '',
        'name': 'countryDartId',
        'type': 'INT64',
        'mode': 'NULLABLE'
    }, {
        'description': '',
        'name': 'dartId',
        'type': 'INT64',
        'mode': 'NULLABLE'
    }, {
        'description': '',
        'name': 'kind',
        'type': 'STRING',
        'mode': 'NULLABLE'
    }, {
        'description': '',
        'name': 'metroCode',
        'type': 'STRING',
        'mode': 'NULLABLE'
    }, {
        'description': '',
        'name': 'metroDmaId',
        'type': 'INT64',
        'mode': 'NULLABLE'
    }, {
        'description': '',
        'name': 'name',
        'type': 'STRING',
        'mode': 'NULLABLE'
    }, {
        'description': '',
        'name': 'regionCode',
        'type': 'STRING',
        'mode': 'NULLABLE'
    }, {
        'description': '',
        'name': 'regionDartId',
        'type': 'INT64',
        'mode': 'NULLABLE'
    }]
}, {
    'description': '',
    'name': 'kind',
    'type': 'STRING',
    'mode': 'NULLABLE'
}]
