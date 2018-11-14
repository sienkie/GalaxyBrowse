# Based on JBrowse Configuration Guide:
# http://gmod.org/wiki/JBrowse_Configuration_Guide
# last update: July 4 2018

flatfile_options = [
    "trackType",
    "className",
    "urltemplate",
    "arrowheadClass",
    "thinType",
    "thickType",
    "type",
    "nclChunk",
    "sortMem",
    "nameAttributes",
    "trackLabel"
]

flatfile_config = [
    'displayMode',
    'category',
    'maxHeight',
    'maxFeatureScreenDensity',
    'glyph',
    'menuTemplate',
    'subParts',
    'transcriptType',
    'labelTranscripts',
    'impliedUTRs',
    'maxFeatureGlyphExpansion',
    'inferCdsParts',
    'disableCollapsedClick',
    'enableCollapsedMouseover',
    'topLevelFeatures',
    'ItemRgb'
]

flatfile_style = [
    'showLabels',
    'showTooltips',
    'featureScale',
    'maxDescriptionLength',
    'color',
    'mouseovercolor',
    'borderColor',
    'borderWidth',
    'height',
    'marginBottom',
    'strandArrow',
    'label',
    'textFont',
    'textColor',
    'text2Color',
    'text2Font',
    'description',
    'connectorColor',
    'connectorThickness',
    'utrColor',
    'transcriptLabelColor',
    'transcriptLabelFont'
]

wiggle_options = [
    'yScalePosition',
    'origin_color'
    'scale',
    'min_score',
    'max_score',
    'autoscale',
    'variance_band',
    'z_score_bound',
    'data_offset',
    'bicolor_pivot',
    'disable_clip_markers',
    'scoreType',
    'logScaleOption',
    'noFill',
    'category',
    'storeClass',
    'label'
]

wiggle_style = [
    'pos_color',
    'bg_color',
    'neg_color',
    'clip_marker_color',
    'height'
]

variant_options = [
    "storeClass",
    "type",
    "label",
    "category",
    "displayMode"
]

variant_style = [x for x in flatfile_style if x != 'label']

supported_flatfile = flatfile_options + flatfile_config + flatfile_style

supported_wiggle = wiggle_options + wiggle_style

supported_variant = variant_options + variant_style

default_flatfile = {
    'trackType': 'CanvasFeatures',
    'displayMode': 'collapsed',
    'category': 'flatfile'
}

default_wiggle = {
    'storeClass': 'JBrowse/Store/SeqFeature/BigWig',
    'autoscale': 'local',
    'category': 'wiggle'
}

default_variant = {
    'storeClass': 'JBrowse/Store/SeqFeature/VCFTabix',
    'category': 'variant',
    'displayMode': 'collapsed'
}

mapped_chars = {
    '>': '__gt__',
    '<': '__lt__',
    "'": '__sq__',
    '"': '__dq__',
    '[': '__ob__',
    ']': '__cb__',
    '{': '__oc__',
    '}': '__cc__',
    '@': '__at__',
    '#': '__pd__'
}
