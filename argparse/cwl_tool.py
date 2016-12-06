import re
import os

import yaml
from jinja2 import Environment, FileSystemLoader

from cmdline2cwl import __version__
from cmdline2cwl.yamldict import YamlOrderedDict


class Param:
    def __init__(self, id, type, position=None, description=None, default=None, prefix=None, optional=False,
                 items_type=None, **kwargs):
        self.id = id
        self.position = position
        self.type = type
        self.default = default
        self.prefix = prefix
        self.optional = optional
        self.items_type = items_type
        if description:
            self.description = description.replace(':', ' -') \
                .replace('\n', ' ')  # `:` is a special character and must be replaced with smth
            self.description = re.sub('\s{2,}', ' ', self.description)
        else:
            self.description = None
        if self.type == 'enum':
            self.choices = list(kwargs.pop('choices', []))


class OutputParam(Param):
    pass


class CWLTool(object):
    def __init__(self, name, description, formcommand, basecommand=None, output_file=None):
        self.name = name
        self.output_file = output_file  # file with manually filled output section
        if description:
            self.description = description.replace('\n', '\n  ')
        else:
            self.description = None
        self.env = Environment(
            loader=FileSystemLoader(os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))),
            trim_blocks=True,
            lstrip_blocks=True)
        if basecommand:
            self.basecommands = [basecommand]
        else:
            self.basecommands = self.name.split()
        self.formcommand = formcommand
        self.inputs = []
        self.outputs = []

    def export(self):
        # inputs_template = self.env.get_template('cwltool_inputs.j2')
        # outputs_template = self.env.get_template('cwltool_outputs.j2')
        # main_template = self.env.get_template('cwltool.j2')
        # inputs = inputs_template.render(tool=self, basecommand=self.basecommands)
        # if self.output_file:
        #     with open(self.output_file) as f:
        #         outputs = f.read()
        # else:
        #     outputs = outputs_template.render(tool=self)
        # return main_template.render(tool=self,
        #                             version=__version__,
        #                             formcommand=self.formcommand,
        #                             stripped_options_command=re.sub('-.*', '', self.formcommand),
        #                             basecommand=self.basecommands,
        #                             inputs=inputs,
        #                             outputs=outputs)


        main_template = self.env.get_template('cwltool_new.j2')
        yaml.add_representer(YamlOrderedDict, yaml.representer.SafeRepresenter.represent_dict)
        if self.output_file:
            with open(self.output_file) as f:
                outputs = f.read()
        else:
            outputs = yaml.dump(self.get_outputs())
        inputs = yaml.dump(self.get_inputs())
        return main_template.render(tool=self,
                                    version=__version__,
                                    formcommand=self.formcommand,
                                    stripped_options_command=re.sub('-.*', '', self.formcommand),
                                    basecommand=self.basecommands,
                                    inputs=inputs,
                                    outputs=outputs)

    def get_inputs(self):
        result = YamlOrderedDict()
        if 'python' in self.basecommands[0]:
            result = {self.name: {'type': 'File',
                                  'default': {
                                      'class': 'File',
                                      'path': self.name,
                                  },
                                  'inputBinding': {
                                      'position': 0
                                  }}}
        for param in self.inputs:
            param_attrs = YamlOrderedDict()
            if param.type == 'enum' or param.type == 'array':
                if param.type == 'array':
                    if not param.optional:
                        param_attrs.update({
                            'type': (param.items_type or 'string') + '[]'
                        })
                    else:
                        param_attrs.update({
                            'type': ['null',
                                     {'type': param.type,
                                      'items': param.items_type or 'string'}]
                        })
                elif param.type == 'enum':
                    param_attrs.update({
                        'type': [{'type': param.type,
                                  'symbols': param.choices}]
                    })
                    if param.optional:
                        param_attrs['type'].insert(0, 'null')
            if param.optional:
                param_attrs.update({'type': '{0}?'.format(param.type)})
            else:
                param_attrs.update({'type': '{0}'.format(param.type)})
            if param.default:
                param_attrs.update({'default': param.default})
            if param.description:
                param_attrs.update({'doc': param.description})

            inputBinding = YamlOrderedDict()
            if param.position:
                inputBinding.update({'position': param.position})
            if param.prefix:
                inputBinding.update({'prefix': param.prefix})
            if inputBinding:
                param_attrs.update({
                    'inputBinding': inputBinding
                })
            result.update({'{0}'.format(param.id): param_attrs})
        return {'inputs': result}

    def get_outputs(self):
        result = YamlOrderedDict()
        if not self.outputs:
            return {'outputs': []}
        for param in self.outputs:
            param_attrs = YamlOrderedDict()
            param_attrs['type'] = 'File'
            if param.default:
                param_attrs.update({'default': param.default})
            if param.description:
                param_attrs.update({'doc': param.description})

            outputBinding = YamlOrderedDict()
            outputBinding.update({'glob': '$(inputs.{0}.path'.format(param.id)})
            if param.position:
                outputBinding.update({'position': param.position})
            if param.prefix:
                outputBinding.update({'prefix': param.prefix})
            if outputBinding:
                param_attrs.update({
                    'outputBinding': outputBinding
                })
            result.update({'{0}_out'.format(param.id): param_attrs})
        return {'outputs': result}

        # doc = YamlOrderedDict({'cwlVersion': "v1.0",
        #                    'class': "CommandLineTool",
        #                    'baseCommand': self.basecommands,
        #                    'doc': self.description,
        #                    'inputs': get_inputs(),
        #                     'outputs': get_outputs()})
        # doc = YamlOrderedDict({'cwlVersion': "v1.0",
        #                    'class': "CommandLineTool",
        #                    'baseCommand': self.basecommands,
        #                    'doc': self.description,
        #                    'inputs': get_inputs(),
        #                     'outputs': get_outputs()})
        # return doc