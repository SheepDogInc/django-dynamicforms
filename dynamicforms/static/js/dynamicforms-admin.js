// django-dynamicforms
// Copyright 2011, SheepDogInc.ca
// Licensed under BSD

(function($){

  var changed, enableDisable, order;

  $(function(){
    $("tr input.action-select").actions();

    $('div.submit-row>input').click( function(event) {
      if (changed) {
        order = $("#sortable").sortable('serialize');
        $('#dynamicform_form').get(0).setAttribute('action', '?' + order);
      }
    });

    enableDisable = function() {
      var disabled = !$('#id_new_content_type').val();
      $('#add_content_submit').attr("disabled", !!disabled);
    };

    enableDisable();

    $('#id_new_content_type').change(enableDisable);
    $('#add_content_submit').click(function(){
      var selected = $('#id_new_content_type :selected');
      var val = selected.val();
      window.location = val;
      return false;
    });

    $("#sortable").sortable({
      delay: 300,
      handle: '.drag_handle',
      update: function() {
        $('#add_content_functionality').hide();
        if (!changed)
          alert("The form's content order will be updated when you save. To discard changes in order, refresh page.");
        changed = true;
      }
    });

  });

})(django.jQuery);
