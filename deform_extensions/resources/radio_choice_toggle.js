var ToggleManager = {
    ui: {},
    showItem: function(tag_name){
        $('.item-' + tag_name).show();
    },
    hideItem: function(tag_name){
        $('.item-' + tag_name).hide();
    },
    toggle: function(visible_target){
        /*
         * Toggle visibility keeping only visible_target
         */
        var this_ = this;
        this.ui.field.each(
            function(index, tag){
                var target_name = $(tag).val();
                console.log("Managing %s", target_name);
                if (target_name && (target_name == visible_target)){
                    this_.showItem(target_name);
                } else {
                    this_.hideItem(target_name);
                }
            }
        );
    },
    onChange: function(event){
        var target_name = $(event.target).attr('data-target');
        this.toggle(target_name);
    },
    bindEvents: function(){
        this.ui.field.on('change', this.onChange.bind(this));
    },
    initializeVisible: function(){
        /*
         * Initial toggle situation
         */
        var checked = this.ui.field.filter(':checked');
        var visible_target = "";
        if (checked.length >= 1){
            visible_target = checked.attr('data-target');
        }
        this.toggle(visible_target);
    },
    setup: function(field_id){
        console.log("Initializing togglemanager with %s", field_id);
        this.ui.field = $('input[name=' + field_id + ']');
        this.ui.form = this.ui.field.closest('form');
        this.bindEvents();
        this.initializeVisible();
    }
};
