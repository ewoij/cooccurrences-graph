(function () {
    // variables
    var edgeDisplayOut = 0;
    var edgeDisplayIn = 1;
    var edgeDisplayBoth = 2;
    var edgeDisplay = edgeDisplayOut;
    var minimumEdgeSize = 0;
    var selectedNode = null;
    var selectedEdge = null;

    $(document).ready(function () {
        function drawGraph() {
            function sizeFilter(edge) {
                return edge.size > minimumEdgeSize;
            };

            var filters = [sizeFilter];
            if (selectedNode) {
                filters.push(function (edge) {
                    switch (edgeDisplay) {
                        case edgeDisplayIn:
                            return edge.target == selectedNode;
                            break;
                        case edgeDisplayOut:
                            return edge.source == selectedNode;
                            break;
                        case edgeDisplayBoth:
                            return edge.source == selectedNode || edge.target == selectedNode;
                            break;
                        default:
                            throw 'invalid edge display value: ' + edgeDisplay;
                    }
                });
            }

            var nodesToDisplay = new Set();

            s.graph.edges().forEach(function (e) {
                display = true;
                filters.forEach(function (filter) {
                    if (display) {
                        display = filter(e);
                    }
                }, this);

                e.hidden = !display;

                if (display) {
                    nodesToDisplay.add(e.source);
                    nodesToDisplay.add(e.target);
                }

                if (e.id == selectedEdge) {
                    e.color = edgeColorSelected;
                } else {
                    e.color = edgeColorNormal;
                }
            });

            s.graph.nodes().forEach(function (n) {
                if (nodesToDisplay.has(n.id)) {
                    n.color = nodeColorNormal;
                }
                else {
                    n.color = nodeColorHidden;
                }

                if (selectedNode == n.id) {
                    n.color = nodeColorSelected;
                }
            });

            s.refresh();
        }

        var nodeColorNormal = '#000';
        var nodeColorHidden = '#D8C3BA';
        var nodeColorSelected = '#84C2F5';
        var edgeColorNormal = '#C4C4C4';
        var edgeColorSelected = nodeColorSelected;

        // initialize graph
        graph.nodes.forEach(function (node) {
           node.size = 1;
        });

        graph.edges.forEach(function (edge) {
            edge.size = 1;
            edge.type = 'curvedArrow';
        });

        s = new sigma({
            graph: graph,
            renderer: {
                container: document.getElementById('graph-container'),
                type: 'canvas'
            },
            settings: {
                edgeColor: 'default',
                defaultEdgeColor: edgeColorNormal,
                minArrowSize: 8,
                minNodeSize: 6,
                maxNodeSize: 10,
                minEdgeSize: 1,
                maxEdgeSize: 2,
                defaultLabelSize: 12,
                enableEdgeHovering: true,
                edgeHoverSizeRatio: 2,
                labelThreshold: 6
            }
        });

        function formatFileName(fileName){
            return fileName.split(/[\\/]/).pop();
        }

        function formatUrl(url){
            return `<a href="${url}" target="_blank">${url}<i class="ml-2 fa fa-external-link" aria-hidden="true"></i></a>`
        }

        function formatDocMetadata(metadata){
            var expectedMetadatas = [
                ['Title', 'title'],
                ['Year', 'year'],
                ['DOI', 'doi'],
                ['Url', 'url', formatUrl],
                ['File', 'file_name', formatFileName]
            ];

            var rows = expectedMetadatas
                .map(function(row){
                    name = row[0]
                    metadata_key = row[1]
                    format_func = row[2]
                    value = metadata[metadata_key]
                    if (!value) return null;
                    if (format_func) value = format_func(value);
                    return `<div class="row"><div class="col-sm-2 article-info-col-1">${name}</div><div class="col-sm-10 article-info-col-2">${value}</div></div>`
                })
                .filter(function(row){
                    return !!row;
                })
                .join('')

            return rows ? `<div class="container article-info collapse">${rows}</div>` : '';
        }

        function clearSentences(){
            $('#sentences').html('');
        }

        function displaySentences(sentenceIds){
            var localSentenceId = 0;
            
            var sentenceDivTitle = `<h1 class="mt-2">${sentenceIds.length} Sentences</h1>`

            function annotationOverlap(a1, a2){
                return a1.end > a2.begin;
            }

            function compareAnnotations(a, b) {
                if (a.begin < b.begin)
                    return -1;
                if (a.begin > b.begin)
                    return 1;
                return 0;
            }

            var elements = sentenceIds.map(function(sentence_id){
                localSentenceId++;
                [d_id, s_id] = sentence_id;
                var metadata = formatDocMetadata(docMetadatas[d_id]);
                var sentence = scopes[d_id][s_id];
                var text = sentence.text;
                var annotations = sentence.annotations.sort(compareAnnotations);
                var finalText = text;
                for (i = annotations.length - 1; i >= 0; i--){
                    var annotation = annotations[i];
                    if (i < annotations.length - 1 && annotationOverlap(annotation, annotations[i + 1])) continue;
                    var className = annotation.type.toLowerCase().replace(/\./g, '-');
                    var part0 = finalText.substring(0, annotation.end);
                    var part1 = finalText.substring(annotation.end);
                    finalText = part0 + '</span>' + part1;
                    var part0 = finalText.substring(0, annotation.begin);
                    var part1 = finalText.substring(annotation.begin);
                    finalText = part0 + `<span class="annotation ${className}">` + part1;
                }

                var localSentenceIdText = `sentence-${localSentenceId}`;
                var articleInfoSelector = `#${localSentenceIdText} .article-info`;
                var toggleLink = metadata ? `<a href="#" class="mr-2 article-info-toggle" data-toggle="collapse" data-target="${articleInfoSelector}"><i class="fa fa-file" aria-hidden="true"></i></a>` : ''

                finalText = `<p class="sentence-text">${toggleLink}${finalText}</p>`;
                return `<div id="${localSentenceIdText}" class="sentence">${finalText}${metadata}</div>`
            });

            $('#sentences').html([sentenceDivTitle].concat(elements));
        };

        s.bind('clickEdge', function (e) {
            if (selectedEdge == e.data.edge.id){
                selectedEdge = null;
                clearSentences();
            }
            else{
                selectedEdge = e.data.edge.id;
                displaySentences(e.data.edge.scope_ids);
            }

            drawGraph();
        });

        s.bind('clickNode', function (e) {
            var nodeId = e.data.node.id;
            if (selectedNode == nodeId) {
                selectedNode = null;
            } else {
                selectedNode = nodeId;
            }

            drawGraph();
        });

        // Components events
        edgeDisplay = parseInt($('#edges-direction .active input').get(0).name);
        $('#edges-direction input').change(function (e) {
            edgeDisplay = parseInt($(this).get(0).name);
            drawGraph();
        });

        $('#increment-size-filter').click(function () {
            updateMinimumSizeEdge(minimumEdgeSize + 1);
            drawGraph();
        });

        drawGraph();
    });
}());
