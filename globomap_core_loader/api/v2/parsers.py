# -*- coding: utf-8 -*-
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
from flask_restplus import reqparse

post_updates_parser = reqparse.RequestParser()
post_updates_parser.add_argument(
    'data',
    type=str,
    required=True,
    help='Updates',
    location='json'
)


auth_parser = reqparse.RequestParser()
auth_parser.add_argument(
    'data',
    type=str,
    required=True,
    help='Auth',
    location='json'
)
