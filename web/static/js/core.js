function addCompany(duns)
{
	var req = $.ajax({
		type: "POST",
		url: REST_BASE + duns
	});

	req.done(function()
	{
		alert('ok')
	})
	req.fail(function(){
		alert('Error');
	})
}