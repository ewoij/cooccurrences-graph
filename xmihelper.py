import xml.etree.ElementTree as ET
import intervaltree

class Xmi:
    def __init__(self, file_):
        self.file_ = file_
        self._root = ET.parse(file_).getroot()
        self.default_properties = {
            '{http://www.omg.org/XMI}id': { 'name': 'id', 'type': int },
            'sofa': { 'type': int },
            'begin': { 'type': int },
            'end': { 'type': int }
        }
    
    def get_text(self):
        return self._root.find('{http:///uima/cas.ecore}Sofa').attrib['sofaString']
    
    def get_annotations(self, types):
        result = dict()
        for type_, settings in types.items():
            annos = self._get_annotation_of_type(type_, settings)
            result[settings['name']] = annos
        return result
    
    def _get_annotation_of_type(self, type_, settings):
        properties = dict(settings.get('properties', dict()))
        for k, v in self.default_properties.items():
            if k not in properties:
                properties[k] = v
        annos = []
        for c in self._root.findall(type_):
            anno = dict()
            anno['type'] = settings['name']
            anno['properties'] = dict()
            for k, v in c.attrib.items():
                prop = properties.get(k, dict())
                k, v = prop.get('name', k), prop.get('type', type(v))(v)
                anno['properties'][k] = v
            annos.append(anno)
        return annos

def add_text(annotations, document):
    text = document.get_text()
    for a in annotations:
        a['text'] = text[a['properties']['begin']:a['properties']['end']]

def add_sub(parents, childs):
    t = intervaltree.IntervalTree()
    for p in parents:
        t.addi(p['properties']['begin'], p['properties']['end'], data=p)
    for c in childs:
        for p in (i.data for i in t[c['properties']['begin']]):
            p.setdefault('sub', []).append(c)

def make_sub_pos_relative(annotations):
    for a in annotations:
        begin = a['properties']['begin']
        for sa in a.get('sub', []):
            prop = sa['properties']
            prop['begin'] -= begin
            prop['end'] -= begin
