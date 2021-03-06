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

Archive

Wipe old information from a Storage bucket based on last update time.

Specify how many days back to retain data and which buckets and paths to purge.
Everything under a path will be moved to archive or deleted depending on your choice.

'''

from starthinker_airflow.factory import DAG_Factory

# Add the following credentials to your Airflow configuration.
USER_CONN_ID = "starthinker_user" # The connection to use for user authentication.
GCP_CONN_ID = "starthinker_service" # The connection to use for service authentication.

INPUTS = {
  'archive_days': 7,
  'auth_write': 'service',  # Credentials used for writing data.
  'archive_bucket': '',
  'archive_path': '',
  'archive_delete': False,
}

TASKS = [
  {
    'archive': {
      'storage': {
        'bucket': {
          'field': {
            'order': 2,
            'kind': 'string',
            'name': 'archive_bucket',
            'default': ''
          }
        },
        'path': {
          'field': {
            'order': 3,
            'kind': 'string',
            'name': 'archive_path',
            'default': ''
          }
        }
      },
      'delete': {
        'field': {
          'order': 4,
          'kind': 'boolean',
          'name': 'archive_delete',
          'default': False
        }
      },
      'auth': {
        'field': {
          'order': 1,
          'kind': 'authentication',
          'name': 'auth_write',
          'description': 'Credentials used for writing data.',
          'default': 'service'
        }
      },
      'days': {
        'field': {
          'order': 1,
          'kind': 'integer',
          'name': 'archive_days',
          'default': 7
        }
      }
    }
  }
]

DAG_FACTORY = DAG_Factory('archive', { 'tasks':TASKS }, INPUTS)
DAG_FACTORY.apply_credentails(USER_CONN_ID, GCP_CONN_ID)
DAG = DAG_FACTORY.execute()

if __name__ == "__main__":
  DAG_FACTORY.print_commandline()
