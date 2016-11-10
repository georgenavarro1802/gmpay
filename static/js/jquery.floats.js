(function($) {


	$.fn.floats = function(options) {

		var options = $.extend({}, $.fn.floats.defaults, options);

		return this.each(function() {

			// pre defined options
			var $this = $(this);
			
			function pretify (e) {
				var value = e.value;
				e.value = $.fn.floats.pretify_fn(value, options);
			}
			
			function simplify (e) {
				var value = e.value;
				e.value = $.fn.floats.simplify_fn(value, options);
			}
			
			// bind the actions
			$this.bind('focus', function() {
				// Cuando coje el foco transforma el numero de bonito a plano.
//				$this.val( simplify(this) );
                simplify(this);
			}).bind('blur', function() {
				// Cuando pierde el foco transforma el numero de plano a bonito.
//				$this.val( pretify(this) );
                pretify(this);
			});
            pretify(this);
	
		});
	
	}; 	

	$.fn.floats.defaults = {
		prefix: '',
		sufix: '',
		decimalSeparator: '.', 
		thousandSeparator: ',',
		decimalPlaces: 2
	};

	$.fn.floats.pretify_fn = function (s, opts) {
		if (opts==undefined) opts = $.fn.floats.defaults;
		if (s==undefined) s = '';
		var sec = s.toString().split(opts.decimalSeparator);
		var i = (sec[0]=='')?"0":sec[0];
		var d = ((sec[1]!=undefined)?sec[1]:"")+"00000000000000000000";
		
		var ir = "";
		while (i.length>0) {
			if (i.length>3) {
				var last = i.slice(-3);
				i = i.slice(0, -3);
				ir = opts.thousandSeparator+last + ir;
			} else {
				ir = i + ir;
				i = '';
			}
		}
		
		return opts.prefix + ir + opts.decimalSeparator + d.slice(0,opts.decimalPlaces) + opts.sufix;
	}
	$.fn.floats.simplify_fn = function (value, opts) {
		return value.replace(opts.prefix, "").replace(opts.sufix, "").replace(opts.thousandSeparator, "");
	}

	
})(jQuery);


prety = function(v) {
    return $.fn.floats.pretify_fn(v.toFixed(2), {prefix: '$', thousandSeparator: ',', decimalSeparator: ".", sufix: '', decimalPlaces: 2});
};

pretyPct = function(v) {
    return $.fn.floats.pretify_fn(v.toFixed(1), {prefix: '', thousandSeparator: ',', decimalSeparator: ".", sufix: '%', decimalPlaces: 1});
};

simple = function(sid) {
    return Big($.fn.floats.simplify_fn($(sid).val(), {prefix: '$', thousandSeparator: ',', sufix: '%'}));
};

simpleV = function(v) {
    return Big($.fn.floats.simplify_fn(v, {prefix: '$', thousandSeparator: ','}));
};



