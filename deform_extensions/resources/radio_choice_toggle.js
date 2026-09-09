var ToggleManager = {
    buildSelector: function(tag_name){
        if (tag_name.indexOf(',') === -1) {
            return `.item-${tag_name}`;
        }
        return tag_name.split(',').map(function(tag){
            return `.item-${tag.trim()}`;
        }).join(', ');
    },
    showItem: function(tag_name){
        const selector = this.buildSelector(tag_name);
        $(selector).show();
    },
    hideItem: function(tag_name){
        const selector = this.buildSelector(tag_name);
        $(selector).hide();
    },
    toggle: function(visible_target){
        /*
         * Toggle visibility keeping only visible_target
         */
        var this_ = this;
        this.ui.field.each(
            function(index, tag){
                var target_name = $(tag).attr('data-target');
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
        this.ui.field
            .off('change.radioChoiceToggle')
            .on('change.radioChoiceToggle', this.onChange.bind(this));
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
        var instance = Object.create(this);
        instance.ui = { field: $('input[name=' + field_id + ']') };
        instance.bindEvents();
        instance.initializeVisible();
    }
};
