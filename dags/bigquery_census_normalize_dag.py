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

'''
--------------------------------------------------------------

Before running this Airflow module...

  Install StarThinker in cloud composer from open source:

    pip install git+https://github.com/google/starthinker

  Or push local code to the cloud composer plugins directory:

    source install/deploy.sh
    4) Composer Menu
    l) Install All

--------------------------------------------------------------

Census Data Normalized

Convert given census table to percent of population, normalizing it.

Specify the geography, year, and span that make up the <a href='https://pantheon.corp.google.com/bigquery?redirect_from_classic=true&p=bigquery-public-data&d=census_bureau_acs&page=dataset' target='_blank'>census table names</a>.
Not every combination of geography, year, and span exists or contains all the required fields.
Every time the query runs it will overwrite the table.

'''

from starthinker_airflow.factory import DAG_Factory

# Add the following credentials to your Airflow configuration.
USER_CONN_ID = "starthinker_user" # The connection to use for user authentication.
GCP_CONN_ID = "starthinker_service" # The connection to use for service authentication.

INPUTS = {
  'auth': 'service',  # Credentials used for writing data.
  'census_geography': 'zip_codes',  # Census table to get data from.
  'census_year': '2018',  # Census table to get data from.
  'census_span': '5yr',  # Census table to get data from.
  'dataset': '',  # Existing BigQuery dataset.
  'type': 'table',  # Write Census_Percent as table or view.
}

TASKS = [
  {
    'census': {
      'auth': {
        'field': {
          'order': 0,
          'kind': 'authentication',
          'name': 'auth',
          'description': 'Credentials used for writing data.',
          'default': 'service'
        }
      },
      'normalize': {
        'census_geography': {
          'field': {
            'description': 'Census table to get data from.',
            'choices': [
              'zip_codes',
              'state',
              'zcta5',
              'schooldistrictunified',
              'puma',
              'place',
              'county',
              'congressionaldistrict',
              'censustract',
              'cbsa'
            ],
            'order': 1,
            'kind': 'choice',
            'name': 'census_geography',
            'default': 'zip_codes'
          }
        },
        'census_span': {
          'field': {
            'description': 'Census table to get data from.',
            'choices': [
              '1yr',
              '3yr',
              '5yr'
            ],
            'order': 3,
            'kind': 'choice',
            'name': 'census_span',
            'default': '5yr'
          }
        },
        'census_year': {
          'field': {
            'description': 'Census table to get data from.',
            'choices': [
              2018,
              2017,
              2016,
              2015,
              2014,
              2013,
              2012,
              2011,
              2010,
              2009,
              2008,
              2007
            ],
            'order': 2,
            'kind': 'choice',
            'name': 'census_year',
            'default': '2018'
          }
        }
      },
      'to': {
        'dataset': {
          'field': {
            'order': 4,
            'kind': 'string',
            'name': 'dataset',
            'description': 'Existing BigQuery dataset.',
            'default': ''
          }
        },
        'type': {
          'field': {
            'description': 'Write Census_Percent as table or view.',
            'choices': [
              'table',
              'view'
            ],
            'order': 5,
            'kind': 'choice',
            'name': 'type',
            'default': 'table'
          }
        }
      }
    }
  }
]

DAG_FACTORY = DAG_Factory('bigquery_census_normalize', { 'tasks':TASKS }, INPUTS)
DAG_FACTORY.apply_credentails(USER_CONN_ID, GCP_CONN_ID)
DAG = DAG_FACTORY.execute()

if __name__ == "__main__":
  DAG_FACTORY.print_commandline()
