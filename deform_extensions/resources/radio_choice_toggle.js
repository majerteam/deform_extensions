var ToggleManager = {
    ui: {},
    showItem: function(tag_name){
        $('.item-' + tag_name).show();
    },
    hideItem: function(tag_name){
        $('.item-' + tag_name).hide();
    },
    toggle: function(visible_tag){
        var this_ = this;
        this.ui.field.each(
            function(index, tag){
                var target_name = $(tag).val();
                console.log("Managing %s", target_name);
                if (target_name == visible_tag){
                    this_.showItem(target_name);
                } else {
                    this_.hideItem(target_name);
                }
            }
        );
    },
    onChange: function(event){
        var target_name = $(event.target).val();
        this.toggle(target_name);
    },
    bindEvents: function(){
        this.ui.field.on('change', this.onChange.bind(this));
    },
    setup: function(field_id){
        console.log("Initializing togglemanager with %s", field_id);
        this.ui.field = $('input[name=' + field_id + ']');
        this.ui.form = this.ui.field.closest('form');
        this.bindEvents();
    }
};
