openerp.bista_readonly_input_text = function(instance) {
    var QWeb = instance.web.qweb,
    _t = instance.web._t;
     
    instance.web.form.FieldReadonlyText = instance.web.form.FieldChar.extend({
        template: 'FieldReadonlyText',        
		render_value: function() {
			var show_value = this.format_value(this.get('value'), '');
			if (!this.get("effective_readonly")) {
				this.$el.find('input').val(show_value);
			} else {				
				this.$(".oe_form_char_content").text(show_value);
			}
		},
    });
	
    instance.web.form.widgets = instance.web.form.widgets.extend({
        'readonly_text' : 'instance.web.form.FieldReadonlyText'
    });
}
