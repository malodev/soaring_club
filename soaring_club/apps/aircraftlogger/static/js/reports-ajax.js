function build_action(settings,action)
{
	if ( !settings[action]) 
		settings[action] = {};
	settings[action].form = '#' + action + '_form';
	settings[action].form_container = '#' + action + '_ajax_form';
	settings[action].form_template  = action + '_form';
	settings[action].return_data_form_id = action + '_form';
	settings[action].results_template  = action + '_table';
	settings[action].return_data_results_id = action + '_table';
	settings[action].return_data_blank_id = '<!-- Intentionally blank template -->';
	settings[action].base_url = '/reports/' + action + '/';
	settings[action].url_results =  settings[action].base_url + settings[action].results_template + '/';
	settings[action].url_form_refresh =  settings[action].base_url + settings[action].form_template + '/';
	settings[action].submit_callback = window[action + '_submit'];
	settings[action].class_to_show = '.' + action;
	return settings;
}

var settings = {};
build_action(settings,'receipts');
build_action(settings,'member');
build_action(settings,'clearance');
build_action(settings,'debits');

function toggleNotes() {
	/*
	$('.notes').each(function(idx,ele){
		if($(ele).css('display') == 'none') { 
	   		$(ele).show('slow'); 
		} else { 
	   		$(ele).hide('slow'); 
		}
	});
	*/
	if($('.notes').css('display') == 'none') { 
   		$('.notes').css('display','block'); 
	} else { 
   		$('.notes').css('display','none'); 
	}
}

function callFormsUI()
{
	// Form submit substitutions
	$("#clearance_form").submit(clearance_submit);
	$("#debits_form").submit(debits_submit);
	$("#receipts_form").submit(receipts_submit);
	$("#member_form").submit(member_submit);

	$( "#jqradio" ).buttonset();
	$( "input:submit" ).button();
	/*
	$( ".nonotes" ).dialog({ autoOpen: false });
	*/
	//$('legend').hover(function(){
		//$(this).next('.notes').show();
		//$(this).next('.notes').position({at: 'bottom center', of: $(this), my: 'top'})
	//});
	$('legend').click(toggleNotes);
	$('legend').css('cursor','help');
	$('#reports-forms h3 a').css('color','#fff');
	
}

function submit(action)
{
	
	//TODO check action
	
	//jQuery refreshing UI
	$( "#ajax-entry" ).empty();

	//refresh form to show or clear errors messages
	//url_form_refresh must call view that DON'T retrieve actual data but check only form data  
	$.post(action.url_form_refresh, $(action.form).serialize(), function(data) {
        //Check that data contains form
		if ( data.indexOf(action.return_data_form_id)>=0 ) {
	    	$( action.form_container ).html( data );
	    	// refreshing jquery UI in form 
	    	callFormsUI();
	    	//$( action.form ).submit( action.submit_callback );
        }
	});
	
	//post actual url. If there's form error, view must return void data
	$.post(action.url_results, $(action.form).serialize(), function(data) {
		//Check that data contains results or is blank 
		if ( data.indexOf(action.return_data_results_id)>=0 || data.indexOf(action.return_data_blank_id)>=0 )
        	$( "#ajax-entry" ).html( data );
  	});
	
	$( '#banner' ).hide();
	$( '.results' ).hide();
	$( action.class_to_show ).show();
	return false;
}

function clearance_submit() {
	return submit(settings['clearance']);
}

function debits_submit() {
	return submit(settings['debits']);
}

function receipts_submit() {
	return submit(settings['receipts']);
}

function member_submit() {
	return submit(settings['member']);
}


//jQuery document ready
$(function() {
	var icons = {
		header: "ui-icon-circle-arrow-e",
		headerSelected: "ui-icon-circle-arrow-s"
	};

	$( "#reports-forms" ).accordion({ 
		header: "h3", 
		collapsible: true,
		icons: icons,
		autoHeight: false,
		navigation: true,
		active: false
	});
	
	callFormsUI();
	$('.notes').css('display','none'); 
	
	
	$( document ).ajaxStart( function() {
		$( '#darkLayer' ).show();
		$( '#ajax-entry').hide();
	}).ajaxStop( function() {
		$( '#darkLayer' ).hide();
		$( '#ajax-entry').show();
	});
	
});