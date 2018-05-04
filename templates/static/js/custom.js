jQuery(document).ready(function() {
    "use strict";

    /* ===================================
        SLIDER
    ====================================== */
    $( '#my-slider' ).sliderPro({
        width: '100%',
        height: 608,
        fade: true,
        arrows: true,
        waitForLayers: true,
        buttons: false,
        autoplay: true,
        autoplayDelay: 4000,
        autoScaleLayers: false,
        imageScaleMode: 'cover',
        slideAnimationDuration: 1500,
        breakpoints: {
            600: {
                height: 480
            }
        }
    });

    /* ===================================
		WOW JS
	====================================== */
    var wow = new WOW(
        {
            boxClass:     'wow',      // animated element css class (default is wow)
            animateClass: 'animated', // animation css class (default is animated)
            offset:       250,          // distance to the element when triggering the animation (default is 0)
            mobile:       true,       // trigger animations on mobile devices (default is true)
            live:         true,       // act on asynchronously loaded content (default is true)
            callback:     function(box) {
                // the callback is fired every time an animation is started
                // the argument that is passed in is the DOM node being animated
            }
        }
    );
    wow.init();

    $(document).ready(function() {
        $("#owl-demo").owlCarousel({
            items: 4,
            loop: true,
            autoPlay: true,
            navSpeed: 2000
        });
    });
});

