# -*- coding: utf-8 -*-


import requests
from odoo import http
from odoo.http import request
from odoo.osv.expression import AND
from odoo.tools import html2plaintext

GOOGLE_MAP_PLACES = 'https://maps.googleapis.com/maps/api/place'


class CustomController(http.Controller):

    def get_google_fields_mapping(self):

        return {'country': ['country'],
                'street_number': ['number'],
                'administrative_area_level_3': ['city'],
                'neighborhood': [''],
                'locality': ['city'],
                'route': ['street'],
                'sublocality_level_1': ['street2'],
                'postal_code': ['zip'],
                'administrative_area_level_1': ['state', 'city'],
                'administrative_area_level_2': ['state', 'country'],
                }

    def _convert_to_standard_address(self, g_fields):

        address_vals = {}
        google_fields_mapping = self.get_google_fields_mapping()
        for g_field in g_fields:
            fields_standard = google_fields_mapping[g_field['type']
                                                    ] if g_field['type'] in google_fields_mapping else []

            for s_field in fields_standard:
                if s_field in address_vals:
                    continue
                if s_field == 'country':
                    country = request.env['res.country'].search(
                        [('code', '=', g_field['short_name'].upper())], limit=1)
                    address_vals[s_field] = country.id if country else False
                    address_vals['country_code'] = country.code if country else False
                elif s_field == 'state':
                    domain = [('code', '=', g_field['short_name'].upper())]
                    if address_vals['country']:
                        domain = AND(
                            [domain, [('country_id.id', '=', address_vals['country'])]])
                    state = request.env['res.country.state'].search(domain)
                    if len(state) == 1:
                        address_vals[s_field] = state.id
                else:
                    address_vals[s_field] = g_field['long_name']
        return address_vals

    @http.route('/web_google/partial_address', type="json", auth="public", website=True)
    def at_get_partial_address(self, partial_address):

        company = request.env.user.company_id or request.env.company
        
        country_code_list = company.at_restricted_country_ids.mapped('code')
        if country_code_list:
            result = ["country:" + str(item) + '|'  for item in country_code_list]
            test_list = [''.join(result)]

        if company and company.at_is_enable_google_api_key and company.at_google_api_key:
            params = {
                'key': company.at_google_api_key,
                'fields': 'formatted_address,name',
                'inputtype': 'textquery',
                'types': 'address',
                'input': partial_address,
            }
            if country_code_list and test_list[0]:
                params.update({
                    'components': test_list[0],
                })
            try:
                results = requests.get(
                    F'{GOOGLE_MAP_PLACES}/autocomplete/json', params=params, timeout=2.5).json()
            except (TimeoutError, ValueError):
                return []
            results = results.get('predictions', []) if results.get(
                'status', False) == 'OK' else []

            return [{'description': result['description'], 'place_id': result['place_id']} for result in results]

        return []

    @http.route('/web_google/fill_address', type="json", auth="public", website=True)
    def at_fill_address(self, address, place_id):
        company = request.env.user.company_id or request.env.company
        if address and company and company.at_is_enable_google_api_key and company.at_google_api_key:
            params = {
                'key': company.at_google_api_key,
                'place_id': place_id,
                'fields': 'address_component,adr_address'
            }

            try:
                results = requests.get(
                    F'{GOOGLE_MAP_PLACES}/details/json', params=params, timeout=2.5).json()

                html_address = results['result']['adr_address']
                results = results['result']['address_components']

                for res in results:
                    res['type'] = res.pop('types')[0]

            except (TimeoutError, ValueError):
                return {}

            sequence = list(self.get_google_fields_mapping().keys())
            results.sort(key=lambda result: sequence.index(
                result['type']) if result['type'] in sequence else 143)
            complete_address = self._convert_to_standard_address(results)

            # To avoid missing any type of user-inputted number
            if 'number' not in complete_address:
                house_number = address.replace(complete_address.get('zip', ''), '').replace(
                    complete_address.get('street', ''), '').replace(complete_address.get('city', ''), '').replace('-', '')
                complete_address['number'] = house_number.split(',')[0].strip()
                complete_address[
                    'formatted_street'] = f'{complete_address["number"]} {complete_address.get("street", "")}'
            else:
                html2street = html2plaintext(html_address.split(',')[0])
                street = F'{complete_address["number"]} {complete_address.get("street", "")}'
                complete_address['formatted_street'] = html2street if len(
                    html2street) >= len(street) else street
            return complete_address if complete_address else {}
        return {}
