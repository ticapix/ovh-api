#!/usr/bin/env python3
import json
from pathlib import Path
import yaml
import requests

from datetime import timedelta

def gen_model_path(model):
    return '#/components/schemas/{}'.format(model)

def convert_type(type_, model_refs):
    type_mapping = {
        'boolean': ('boolean', ),
        'date': ('string', 'date'),
        'datetime': ('string', 'date-time'),
        'double': ('number', 'double'),
        'ip': ('string', ),
        'long': ('number', 'int64'),
        'password': ('string', 'password'),
    }
    if type_.endswith('[]'):
        return {
            'type': 'array',
            'items': convert_type(type_[:-2], model_refs)
            }
    if type_ in type_mapping:
        ret = {
            'type': type_mapping[type_][0]
        }
        if len(type_mapping[type_]) > 1:
            ret['format'] = type_mapping[type_][1]
        return ret
    if type_ in model_refs:
        return {
            '$ref': gen_model_path(type_)
        }
    if type_ != 'string':
        print("WARNING: unknown type '{}'".format(type_))
    return {
        'type': 'string'
    }

def convert_properties(properties, model_refs):
    for name, property_ in properties.items():
        yield (name, convert_type(property_['type'], model_refs))


def convert_model(models, model_refs):
    for name, model in models.items():
        if 'properties' in model:
            yield (name, {
                'type': 'object',
                'properties': dict(convert_properties(model['properties'], model_refs))
            })
            continue
        if 'enumType' in model:
            yield (name, {
                'type': 'string',
                'enum': model['enum']
            })
            continue
        print("ERROR: unknown type '{}'".format(model))        
        import pdb; pdb.set_trace()

def convert_parameter(parameters, model_refs):
    for parameter in parameters:
        yield {
            'name': parameter['name'],
            'in': parameter['paramType'], # query, path, header, cookie, 
            'required': parameter.get('required', 0) == 1,
            'description': parameter['description'] or '',
            'schema': convert_type(parameter['dataType'], model_refs)
            }

def convert_body(params, model_refs):
    schemas = {
        'type': 'object',
        'properties': {}
    }
    for param in params:
        if 'name' not in param:
            if len(params) != 1:
                raise Exception("There can be only one unamed body param")
            return {'$ref': gen_model_path(param['dataType'])}
        schemas['properties'][param['name']] = convert_type(param['dataType'], model_refs)
    return schemas            

def convert_operation(operations, model_refs):
    # cat schema/apis-me.json | jq '.apis[].operations[].parameters[] | select(.paramType == "body")' |less
    for operation in operations:
        method = {
            'summary': operation['description'],
            'responses': {
                '200': {
                    'description': 'OK'
                }
            }
        }
        parameters = list(filter(lambda e: e['paramType'] != 'body', operation['parameters']))
        body_parameters = list(filter(lambda e: e['paramType'] == 'body', operation['parameters']))
        if len(parameters) > 0:
            method['parameters'] = list(convert_parameter(parameters, model_refs))
        if len(body_parameters) > 0:
            method['requestBody'] = {
                'description': '',
                'content': {
                    'application/json': {
                        'schema': convert_body(body_parameters, model_refs)
                    }
                }
            }
        if operation['responseType'] != 'void':
            method['responses']['200'] = {
                'description': 'OK',
                'content': {
                    'application/json': {
                        'schema': convert_type(operation['responseType'], model_refs),
                    }
                }
            }
        yield (operation['httpMethod'].lower(), method)

def convert_api_paths(paths, model_refs):
    for path in paths:
        yield (path['path'], dict(convert_operation(path['operations'], model_refs)))

def convert_api_to_oa3(api_json):
    model_refs = list(api_json['models'].keys())
    return {
        'openapi': '3.0.0',
        'info': {
            'version': '1.0.0',
            'title': 'Swagger OVH API',
            'license': {
                'name': 'OVH'
            }
        },
        'paths': dict(convert_api_paths(api_json['apis'], model_refs)),
        'components': {
            'schemas': dict(convert_model(api_json['models'], model_refs))
        }
    }

# apis = {
#     'me': json.load(open(Path('schema') / 'apis-me.json', 'r')),
#     'ip': json.load(open(Path('schema') / 'apis-ip.json', 'r')),
#     'dedicatedCloud': json.load(open(Path('schema') / 'apis-dedicatedCloud.json', 'r')),
#     }

if __name__ == '__main__':
    apis = requests.get('https://api.ovh.com/1.0/').json()
    api_base = apis['basePath']
    for api in apis['apis']:
        api_path = '{}{}.json'.format(api_base, api['path'])
        api_name = api['path'].strip('/').replace('/', '_')
        print(api_path)
        print(api_name)
        api = requests.get(api_path).json()
        json.dump(api, open(Path('schemas') / 'ovh' / 'apis-{}.json'.format(api_name), 'w'))
        api_swagger = convert_api_to_oa3(api)
        yaml.dump(api_swagger, open(Path('schemas') / 'oa3' / 'apis-{}.yml'.format(api_name), 'w'), allow_unicode=True, default_flow_style=False)
