# input/output/template directories
xmi_dir = r'C:\tmp\xmi_output'
scopes_dir = r'output\scopes'
cooc_dir = r'output\cooccurrences'
graph_dir = r'output\graph'
graph_template_dir = 'graph_template'
# annotation to extract form xmi as scope
# (<xml type>, <new type name>)
scope_annotation = ('{http:///de/tudarmstadt/ukp/dkpro/core/api/segmentation/type.ecore}Sentence', 'scope')
# annotations to extract from xmi as sub annotations of the scope
# (<xml type>, <new type name>)
sub_annotations = [
    ('{http:///genericpipeline.ecore}Item', 'item'),
    ('{http:///genericpipeline.ecore}Event', 'event')
]
# the type of the scope annotations contain in the json files
scope_type = 'scope'
# the type of the item sub annotations contain in the json files
item_type = 'item'
# [optional] if the item has a property to be used instead of the covered-text. If None, the covered-text is normalized and used instead.
item_property = 'value'
# [optional] the type of the event used to filter scope
event_type = 'event'
# parameters to filter the co-occurences
cooc_min_count = 7
cooc_min_ratio = 0.66