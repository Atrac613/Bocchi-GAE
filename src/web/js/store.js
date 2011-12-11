function setItemStatus(status) {
	if (status == 1) {
		$('#item_enable').show();
		$('#item_price').show();
		$('#item_wait').hide();
		
		$('#buy_item').button('enable');
	} else if (status == 2) {
		$('#item_disable').show();
		$('#item_title').hide();
		$('#item_price').hide();
		$('#item_wait').hide();
	} else if (status == 3) {
		$('#item_wait').show();
	} else if (status == 4) {
		$('#item_wait').hide();
	} else {
		$('#item_disable').show();
		$('#item_title').hide();
		$('#item_price').hide();
	}
}

function setTitle(title) {
	$('#item_title').text(title);
	$('#item_title').show();
}

function setPrice(price) {
	$('#item_price').text(price);
}

function setDescription(description) {
	$('#item_description').text(description);
}

function checkReceiptStatus(key) {
	console.log('checkReceiptStatus');
	$('#item_price').hide();
	$.post('/store_api/receipt_status', {key: key}, function(data){
		if (data) {
			if (data.pending) {
				setTimeout(checkReceiptStatus(key), 1000);
			} else {
				console.log('Window refresh.');
				$.mobile.changePage('/store/buy/success', {transition: 'slideup', reloadPage: true});
			}
		} else {
			consolo.log('data is null.');
		}
	}, 'json');
}
