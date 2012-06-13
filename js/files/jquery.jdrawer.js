(function($)
{
	$.fn.jDrawer = function(settings)
	{
		settings = $.extend({}, $.jDrawer.Settings, settings);

		return this.each(function()
		{
			var self = this, $self = $(this);

			var items = [];
			
			$self.addClass("jDrawer")
			.addClass("jDrawer-" + settings.direction)
			.children("li")
			.addClass("jDrawer-item")
			.each(function()
			{
				var current = $(this);
				
				current.html("<div class='jDrawer-item-border-1'><div class='jDrawer-item-border-2'><div class='jDrawer-item-border-3'><div class='jDrawer-content'>" + current.html() + "</div></div></div></div>");
				
				items.push(current);
			});
			
			$self.show();
			
			var first = items[0], last = items[self.length - 1];
			
			var over, out;

			/* <initialize> */

			var zid = items.length + settings.zindex;
			
			over = function(active)
			{
				var active = active === undefined ? $(this) : active.length ? $(active) : $(this);
				
				if(!$(this).hasClass("jDrawer-active"))
				{
					$("li.jDrawer-active", $self).removeClass("jDrawer-active");
					
					active.addClass("jDrawer-active");
					
					var set = first.jT * -1;
					
					$.each(items, function()
					{
						var current = this;
						
						var slide = function()
						{
							set += current.hasClass("jDrawer-active") ? current.jA : current.jN;
							
							var obj = {}; obj[settings.direction] = set + "px";
							
							current.stop().animate(obj, settings.speed);
						};
						
						settings.delay > 0 ? setTimeout(slide, settings.delay) : slide();
					});
					
					//settings.callback !== undefined ? settings.callback() : 0;
				}
			};
			
			if(settings.event === "hover")
				out = settings.sticky ? function() {} : over;
			
			$.each(items, function()
			{
				var jT = 0, jP = 0, jD = 0, jW = 0, jA = 0, jN = 0;
				
				var prev = this.prev("li.jDrawer-item");
				
				if(settings.direction === "top")
					jT = this.height(), jP = prev.height();
				else if(settings.direction === "left")
					jT = this.width(), jP = prev.width();
				
				var handle = this.find(".jDrawer-handle");
				
				if(settings.handle)
					jW = settings.handle;
				else if(handle.length > 0)
					jW = jT - (handle.offset()[settings.direction] - this.offset()[settings.direction]);
				else
					jW = 120;
				
				jD = prev.length > 0 ? jT - jP : 0;
				
				this.jT = jT,
				this.jN = jW + (jD * -1),
				this.jA = this.is(":first-child") === true ? jT + (jD * -1) : jT + (jD * -1) - 10;
				
				//horizontal bug fix
				settings.direction === "left" ?
					this.find(".jDrawer-content").append("<div style=\"clear: both\"></div>") : 0;
				
				this.css("z-index", zid--);
				
				out ? this.hover(over, out) : this.bind(settings.event, over);
			});

			/* </initialize> */
			
			/* <resize> */

			var t = 0, biggest = first;
			
			$.each(items, function()
			{
				this.jT > biggest.jT ? biggest = this : 0;
			});
			
			biggest.addClass("jDrawer-biggest");
			
			$.each(items, function()
			{
				t += this.hasClass("jDrawer-biggest") ? this.removeClass("jDrawer-biggest").jA : this.jN
			});
			
			if(settings.direction === "top")
				$self.height(t);
			else if(settings.direction === "left")
				$self.width(t);
					
			/* </resize> */
			
			/* <colorize> */

			var color = settings.color, parent = $self.parent();
			
			if(settings.color === undefined)
				while(parent.css("background-color") !== undefined && !parent.is("html"))
					color = parent.css("background-color"), parent = parent.parent();
			
			var id = $self.attr("id");
			
			$("#" + id + ", #" + id + " .jDrawer-content", $self.parent()).css("background-color", color);
		
			/* </colorize> */
			
			/* <preload> */
			
			$("*", self).each(function()
			{
				var bg = $(this).css("background-image");
				
				if(bg !== "none")
					if(bg.match(/^url[("']+(.*)[)"']+$/i))
						(new Image()).src = RegExp.$1;
			});

			/* </preload> */
			
			$(window).load(function()
			{
				setTimeout(function()
				{
					over($(".jDrawer-active", $self));
				}, 1 * 1000);
			});
		});
	};
	
	$.jDrawer =
	{
		Settings: 
		{
			direction: "top",
			speed: 300,
			delay: 0,
			color: "#FFF",
			sticky: true,
			zindex: 0,
			handle: undefined,
			event: "hover",
			callback: undefined
		},
		
		Initialized: false,
	
		Initialize: function()
		{
			if(!this.Initialized)
			{
				/* <fixFlicker> */
				
				if($.browser.msie === true)
					try { document.execCommand("BackgroundImageCache", false, true); } catch(e) {}
					
				/* </fixFlicker> */
			}
		},
		
		PreloadImages: function()
		{
			for(var i = 0; i++; i < arguments.length)
				if(arguments[i].type === "array")
					for(var j in arguments[i])
						(new Image()).src = arguments[i][j];
				else
					(new Image()).src = arguments[i];
		}
	};
	
	$(document).ready(function()
	{
		$.jDrawer.Initialize();
	});
})(jQuery);
