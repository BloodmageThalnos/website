$ = jQuery;

/***
Utility functions available across the site
***/
var SUNEWS = {


  size: function(){
    // return window size based on visibility as calculated by CSS
    var size = 'unknown';

    // if we don't already have the size-detect div's, add them
    if ( $('.size-detect-xs').length == 0 ) {
      $('body')
        .append('<div class="size-detect-xs" />')
        .append('<div class="size-detect-sm" />')
        .append('<div class="size-detect-md" />')
        .append('<div class="size-detect-lg" />');
    }

    $(['xs', 'sm', 'md', 'lg']).each(function(i, sz) {
      if ($('.size-detect-'+sz).css('display') != 'none') {
        size = sz;
      }
    });
    return size;
  },

  headerHeight: function () {
    return $('#top').outerHeight() + $('#header').outerHeight() + $('#mainmenu').outerHeight() + $('#wpadminbar').outerHeight();
  },

  stickFooter: function(){
    // adjust css to make footer sticky
    var h = $('#footer').height() + 'px';
    $('#su-content').css('padding-bottom', h);
    $('#footer').css('margin-top', '-'+h);
  },

  cardHeight: function (elements) {
    // only work on card-content - images will be equal height
    elements = $(elements).find(".card-content");

    // on phones, everything is auto height
    if (SUNEWS.size() == 'xs') {
      elements.each( function() { $(this).height('auto'); } );
      return elements; // allow chaining
    }

    var heights, maxHeight;
    heights = elements.map(function() {
      $(this).height('auto'); // ensure it has its natural height
      return $(this).height();
    });
    maxHeight = Math.max.apply(null, heights);

    elements.height(maxHeight);
    return elements; // allow chaining
  },

  equalHeight: function (container, containerlg) {
    // until CSS flexboxes are widely supported, use this to make div's be equal height
    var currentTallest = 0,
        currentRowStart = 0,
        rowDivs = new Array(),
        height = 0,
        numGaps = 0,
        $el,
        topPosition = 0;
    $(container).each(function () {

      $el = $(this);
      $($el).height('auto')
      topPostion = $el.parent().position().top;

      if (currentRowStart != topPostion) {
        height += currentTallest;
        numGaps++;
        for (currentDiv = 0; currentDiv < rowDivs.length; currentDiv++) {
          rowDivs[currentDiv].height(currentTallest);
        }
        rowDivs.length = 0; // empty the array
        currentRowStart = topPostion;
        currentTallest = $el.height();
        rowDivs.push($el);
      } else {
        rowDivs.push($el);
        currentTallest = (currentTallest < $el.height()) ? ($el.height()) : (currentTallest);
      }
      for (currentDiv = 0; currentDiv < rowDivs.length; currentDiv++) {
        rowDivs[currentDiv].height(currentTallest);
      }
    });
    height += currentTallest; numGaps--;

    // Set height for large card on diferent viewport sizes
    var gap = $(container).css('margin-bottom');
    gap = parseInt(gap);
    var cardfull = $(containerlg);
    if ($(window).width() > 992) {
      cardfull.height(height + (gap * numGaps));
    } else {
      cardfull.height('auto');
    }
    //set height for regular card to auto on smaller devices
    if ($(window).width() < 768) {
      $(container).height('auto');
    }
  },

  pushdown: function(e){
    if ( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || SUNEWS.size() == 'xs' ) {
      var elems = $(e);
      $('#main-bottom').find('[class*="col-"]').prepend( elems );
      elems.removeClass('pull-left pull-left-narrow pull-left-wide pull-right pull-right-narrow pull-right-wide').addClass('align-center center-block');
    }
  },

  trackClick: function() {
    if ( typeof ga == 'function' ) {
      var $this = $( this )
        , category = $this.closest('[data-ga-category]').data('ga-category') || 'Unknown'
        , action   = $this.closest('[data-ga-action]').data('ga-action') || ( $this.is( 'a' ) && this.hostname ) || 'click'
        , label    = $this.data('ga-label') || this.href
      ;
      ga( 'send', 'event', category, action, label);
    }
  }
};

$(function() {
  // add :external filter to elements
  $.expr[':'].external = function(obj) {
    return obj.hostname && (obj.hostname != document.location.hostname);
  };

  // style external links
  $('#section-list a:external, #post-list h3 a:external').addClass('external-link').attr('aria-label', 'external link');

  // set background image for elements that have data-bg-img attribute (e.g. infoboxes)
  $('[data-bg-img]').each(function () {
    $(this).css('background-image', 'url('+$(this).data('bg-img')+')');
  });

  // note resize events and trigger resizeEnd event when resizing stops
  $(window).resize(function() {
    if(this.resizeTO) clearTimeout(this.resizeTO);
    this.resizeTO = setTimeout(function() {
      $(this).trigger('resizeEnd');
    }, 200);
  });

  // Trigger resizeEnd when document is loaded
  $(window).load(function(){
    $(this).trigger('resizeEnd');
  });


  // Call responsive funtion when browser window resizing is complete
  $(window).bind('resizeEnd', function() {
    // SUNEWS.storyBannerFullScreenHeight('#story-banner.banner-full-screen img','#story-banner.banner-full-screen'); // make story banner container the same size as story banner full screen image
    // re-stick the footer in case its height has changed
    SUNEWS.stickFooter();
    SUNEWS.pushdown('.pushdown'); // move infoboxes, sidebars to bottom on small screens
    SUNEWS.equalHeight('.eq-height');

  });
  $(window).trigger('resizeEnd');

  // don't add skip links to browser history
  $('#skip > a').click(function(e){
    var href = $(this).attr('href').substr(1); // remove the #
    var target = $('a[name="' + href + '"]');
    target.focus();
  });

  // on small screens, reveal the top nav when they start scrolling up
  if (SUNEWS.size() == 'xs') {
    var nav = $('#mainmenu')[0]
        , $nav = $(nav)
        , $header = $('#header')
        , $article = $nav.next('article')
        , $navHeight = $nav.outerHeight()
        , navTop = $nav.position().top
        , navBottom = navTop + $nav.height()
        , prevScroll = 0
        ;
    $(window).scroll(function () {
      var currScroll = $(this).scrollTop();

      if (currScroll > navBottom) {
        $nav.addClass('fixed');
        $article.css("padding-top", $navHeight + 'px');
        if (currScroll > prevScroll) {
          $nav.removeClass('visible');
        } else {
          $nav.addClass('visible');
        }
      }
      else if (currScroll <= navTop) {
        $nav.removeClass('fixed');
        $nav.removeClass('visible');
        $article.css("padding-top", "0");
      }
      prevScroll = currScroll;
    });
  }
});