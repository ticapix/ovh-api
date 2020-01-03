#!/usr/bin/env python3

import logging
from typing import Tuple, Iterable

logger = logging.getLogger(__name__)

UNKNOWN_TYPE = set()


def gen_model_path(model):
    return '#/components/schemas/{}'.format(model)


def convert_type(type_: str, model_refs) -> dict:
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
        logger.warning("unknown type '{}'".format(type_))
        UNKNOWN_TYPE.add(type_)
    return {
        'type': 'string'
    }


def convert_properties(properties, model_refs) -> Iterable[Tuple[str, dict]]:
    for name, property_ in properties.items():
        yield (name, convert_type(property_['type'], model_refs))


def convert_model(models, model_refs) -> Iterable[Tuple[str, dict]]:
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
        logger.error("unknown type '{}'".format(model))
        if logger.level == logging.DEBUG:
            import pdb
            pdb.set_trace()


def convert_parameter(parameters, model_refs) -> Iterable[dict]:
    for parameter in parameters:
        yield {
            'name': parameter['name'],
            'in': parameter['paramType'],  # query, path, header, cookie
            'required': parameter.get('required', 0) == 1,
            'description': parameter['description'] or '',
            'schema': convert_type(parameter['dataType'], model_refs)
        }


def convert_body(params, model_refs) -> dict:
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


def convert_operation(operations, model_refs) -> Iterable[Tuple[str, dict]]:
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


def convert_api_paths(paths, model_refs) -> Iterable[Tuple[str, dict]]:
    for path in paths:
        yield (path['path'], dict(convert_operation(path['operations'], model_refs)))


def convert_api_to_oa3(api_json) -> dict:
    model_refs = list(api_json['models'].keys())
    return {
        'openapi': '3.0.0',
        'info': {
            'version': api_json['apiVersion'],
            'title': 'Swagger OVH API for {}/{}'.format(api_json['basePath'], api_json['resourcePath']),
            'license': {
                'name': 'OVH'
            }
        },
        'paths': dict(convert_api_paths(api_json['apis'], model_refs)),
        'components': {
            'schemas': dict(convert_model(api_json['models'], model_refs))
        }
    }
