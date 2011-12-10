function setItemStatus(status) {
	if (status == 1) {
		$('#item_enable').show();
		$('#item_price').show();
		$('#buy_item').button('enable');
	} else if (status == 2) {
		$('#item_disable').show();
	} else {
		$('#item_disable').show();
	}
}

function setTitle(title) {
	$('#item_title').text(title);
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
				$.mobile.changePage('/store/buy', {transition: 'slideup', reloadPage: true});
			}
		} else {
			consolo.log('data is null.');
		}
	}, 'json');
}
