odoo.define('nibbana_tree_color', function(require) {
    var ListRenderer = require('web.ListRenderer');
    ListRenderer.include({
        _renderRow: function(record) {
            var $tr = this._super.apply(this, arguments);
            var data = record.data;
            if (data.area_color) {
                $tr.css('background-color', data.area_color);
            }
            return $tr;
        },
    });
});
