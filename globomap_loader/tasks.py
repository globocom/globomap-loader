"""
   Copyright 2018 Globo.com

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
from globomap_loader.loader.globomap import GloboMapClient
from globomap_loader.settings import GLOBOMAP_API_URL
from globomap_loader.settings import QUERIES


def run_queries():
    globomap_client = GloboMapClient(GLOBOMAP_API_URL)
    for qr in QUERIES.split(','):
        if qr:
            qr = qr.split(';')
            variable = qr[1] if len(qr) > 1 else ''
            query = qr[0]
            globomap_client.run_query(query, variable)
