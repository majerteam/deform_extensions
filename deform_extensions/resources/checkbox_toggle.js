var CheckboxToggleManager = {
    ui: {},
    showItem: function(tag_name){
        console.log("Showing : %s", tag_name);
        $('.item-' + tag_name).show();
    },
    hideItem: function(tag_name){
        $('.item-' + tag_name).hide();
    },
    bindEvents: function(){
        this.ui.field.on('change', this.onChange.bind(this));
    },
    onChange: function(event){
        /*
         * Initial toggle situation
         */
        var checked = this.ui.field.is(':checked');
        if (checked){
            if (this.true_target){
                this.showItem(this.true_target);
            }
            if (this.false_target){
                this.hideItem(this.false_target);
            }
        } else {
            if (this.false_target){
                this.showItem(this.false_target);
            }
            if (this.true_target){
                this.hideItem(this.true_target);
            }
        }
    },
    setup: function(field_id, true_target, false_target){
        console.log("Initializing checkbox togglemanager with %s %s,%s", field_id, true_target, false_target);
        this.ui.field = $('#' + field_id);
        this.ui.form = this.ui.field.closest('form');
        this.bindEvents();
        this.true_target = true_target;
        this.false_target = false_target;
        this.onChange();
    }
};
