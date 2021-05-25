// This code primarily thanks to:
// https://openfolder.sh/django-tutorial-as-you-type-search-with-ajax
$(function(){ // this will be called when the DOM is ready

    const user_input = $("#user-input")
    const search_icon = $('#search-icon')
    const model = $('#model').val()

    const recipe_id = $('#recipe_id').val()
    let endpoint = window.location.pathname
    
    const delay_by_in_ms = 700
    let scheduled_function = false
    
    
    let ajax_call = function (endpoint, request_parameters) {
        $.getJSON(endpoint, request_parameters)
            .done(response => {
                
                let ing_div = $('#replaceable-content');
                console.log(ing_div)
            
                // fade out the ing_div, then:
                ing_div.fadeTo('fast', 0).promise().then(() => {
                    // replace the HTML contents
                    ing_div.html(response['html_from_view'])
                    // fade-in the div with new contents
                    ing_div.fadeTo('fast', 1)
                    // stop animating search icon
                    search_icon.removeClass('blink')
                })
            })
    }


    user_input.on('keyup', function () {

        const rbs = document.querySelectorAll('input[name="group"]');
        let selectedValue = undefined
        let len = rbs.length

        for (i=0; i<len; i++) {
            let rb = rbs.item(i)
            if (rb.checked) {
                selectedValue = rb.value;
                break;
            }
        }
        console.log('value', selectedValue)
        let request_parameters = {
            q: $(this).val(), // value of user_input: the HTML element with ID user-input
            radio: selectedValue,
            status: true,
        }

        // start animating the search icon with the CSS class
        search_icon.addClass('blink')

        // if scheduled_function is NOT false, cancel the execution of the function
        if (scheduled_function) {
            clearTimeout(scheduled_function)
        }

        // setTimeout returns the ID of the function to be executed
        scheduled_function = setTimeout(ajax_call, delay_by_in_ms, endpoint, request_parameters)
    })

    radios = document.querySelectorAll('input[name="group"]')
    length = radios.length
    for (i=0; i<length; i++) {
        let radio = radios.item(i);

        radio.onclick = function () {

            let value = $(this).val()
            let status = radio.checked

            let request_parameters = {
                q: user_input.val(),
                radio: value,
                status: status
            }

            console.log(value, status)

            scheduled_function = setTimeout(ajax_call, 0, endpoint, request_parameters)
        }
    }

})